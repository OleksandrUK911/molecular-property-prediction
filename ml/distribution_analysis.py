"""Distribution analysis of the target variable and descriptors.

Closes the two still-open P1 items from data/TODO_quality_validation.md:
"target distribution (histogram, skew, outliers)" and "descriptor
distribution (MolWt, LogP, etc.)". Complements the leakage/duplicate/IQR
checks already in data/processed/report.md, which look at *which* molecules
are unusual but not at what the overall distribution shape looks like.

Usage:
    python ml/distribution_analysis.py

Reads data/processed/esol_processed.csv.
Writes ml/results/distribution_report.md and ml/results/distribution_histograms.png.
"""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # headless - no display available in CI/containers
import matplotlib.pyplot as plt
import pandas as pd
from scipy.stats import skew

ROOT = Path(__file__).resolve().parent.parent
PROCESSED_CSV = ROOT / "data" / "processed" / "esol_processed.csv"
REPORT_PATH = ROOT / "ml" / "results" / "distribution_report.md"
PLOT_PATH = ROOT / "ml" / "results" / "distribution_histograms.png"
FEATURE_ENGINEERING_REPORT = ROOT / "ml" / "results" / "feature_engineering_report.md"

DESCRIPTOR_COLUMNS = [
    "MolWt",
    "LogP",
    "TPSA",
    "NumHDonors",
    "NumHAcceptors",
    "NumRotatableBonds",
    "RingCount",
]
COLUMNS = ["target"] + DESCRIPTOR_COLUMNS

# Rough thresholds for calling a distribution "notably skewed" (Fisher-Pearson
# skewness, as returned by scipy.stats.skew): |skew| > 1 is commonly
# considered substantially skewed for a unimodal distribution.
SKEW_THRESHOLD = 1.0


def main() -> None:
    df = pd.read_csv(PROCESSED_CSV)

    stats = {}
    for col in COLUMNS:
        values = df[col]
        stats[col] = {
            "mean": float(values.mean()),
            "median": float(values.median()),
            "std": float(values.std()),
            "skew": float(skew(values)),
            "min": float(values.min()),
            "max": float(values.max()),
        }

    fig, axes = plt.subplots(2, 4, figsize=(20, 9))
    axes = axes.flatten()
    for ax, col in zip(axes, COLUMNS):
        ax.hist(df[col], bins=30, color="#4C72B0", edgecolor="white")
        ax.set_title(f"{col} (skew={stats[col]['skew']:+.2f})")
        ax.set_xlabel(col)
        ax.set_ylabel("count")
    # Unused subplot (8 slots, 8 columns -> none unused, but keep this
    # defensive in case COLUMNS ever shrinks).
    for ax in axes[len(COLUMNS):]:
        ax.axis("off")
    fig.suptitle("Target and descriptor distributions (ESOL, all splits)")
    plt.tight_layout()
    plt.savefig(PLOT_PATH, dpi=120)
    plt.close(fig)

    lines = ["# Distribution analysis: target and descriptors\n\n"]
    lines.append(
        "Answers the two still-open data-quality items: what does the "
        "target/descriptor distribution actually look like (shape, skew, "
        "range), not just which individual molecules are IQR outliers "
        "(already covered in `data/processed/report.md`).\n\n"
    )
    lines.append(f"n = {len(df)} molecules (all splits combined).\n\n")

    lines.append("## Summary statistics\n\n")
    lines.append("| Variable | Mean | Median | Std | Skewness | Min | Max |\n")
    lines.append("|---|---|---|---|---|---|---|\n")
    for col in COLUMNS:
        s = stats[col]
        lines.append(
            f"| {col} | {s['mean']:.2f} | {s['median']:.2f} | {s['std']:.2f} | "
            f"{s['skew']:+.2f} | {s['min']:.2f} | {s['max']:.2f} |\n"
        )

    lines.append(f"\n![Distribution histograms]({PLOT_PATH.name})\n")

    target_skew = stats["target"]["skew"]
    lines.append("\n## Interpretation\n\n")
    lines.append(
        f"**Target (log solubility, mol/L):** skewness = {target_skew:+.2f}. "
        + (
            "This is a mild-to-moderate left skew (a longer tail toward very "
            "insoluble compounds) rather than a severe one - the target is "
            "reasonably well-behaved for both a linear model (Ridge) and a "
            "tree-based model (XGBoost), so no target transformation looks "
            "necessary.\n\n"
            if abs(target_skew) <= SKEW_THRESHOLD
            else "This is a substantial skew, consistent with the dataset "
            "containing a tail of very poorly soluble compounds (e.g. the "
            "PCB/PAH/long-chain-alkane outliers already flagged in "
            "`data/processed/report.md` and analyzed further in "
            "`ml/results/evaluation_report.md`). A tree-based model like the "
            "winning XGBoost is largely unaffected by this since it splits on "
            "value order rather than assuming a symmetric error distribution, "
            "but a linear model such as the Ridge baseline is more sensitive "
            "to it - this is one plausible contributor to Ridge's higher "
            "residual variance on the low-solubility tail.\n\n"
        )
    )

    skewed_descriptors = [
        col for col in DESCRIPTOR_COLUMNS if abs(stats[col]["skew"]) > SKEW_THRESHOLD
    ]
    if skewed_descriptors:
        parts = ", ".join(f"`{c}` ({stats[c]['skew']:+.2f})" for c in skewed_descriptors)
        lines.append(
            f"**Notably skewed descriptors (|skew| > {SKEW_THRESHOLD}):** {parts}. "
            "Long right tails on count-like descriptors (e.g. `NumRotatableBonds`, "
            "`RingCount`, `NumHAcceptors`) are typical for small drug-like "
            "molecule datasets - most compounds have a handful of rotatable "
            "bonds/rings/acceptors, with a few larger, more flexible or more "
            "polycyclic outliers pulling the tail. This is more of a concern "
            "for a linear model (a few high-leverage points can dominate the "
            "fit) than for XGBoost, which only needs a sensible split point "
            "and does not assume linearity or homoscedasticity.\n\n"
        )
    else:
        lines.append(
            "**Descriptors:** none of the 7 descriptors exceed the "
            f"|skew| > {SKEW_THRESHOLD} threshold used here for the target - "
            "distributions are unimodal without an extreme long tail.\n\n"
        )

    if FEATURE_ENGINEERING_REPORT.exists():
        fe_text = FEATURE_ENGINEERING_REPORT.read_text(encoding="utf-8")
        multicollinear_pairs = []
        for line in fe_text.splitlines():
            line = line.strip()
            if line.startswith("- ") and "<->" in line:
                multicollinear_pairs.append(line[2:])
        overlap = [
            pair
            for pair in multicollinear_pairs
            if any(col in pair for col in skewed_descriptors)
        ]
        lines.append(
            "**Connection to multicollinearity findings "
            "(`ml/results/feature_engineering_report.md`):** that report "
            f"found these high-correlation (|r| > 0.7) descriptor pairs: "
            f"{', '.join(multicollinear_pairs) if multicollinear_pairs else 'none'}.\n"
        )
        if overlap:
            lines.append(
                f"Of the skewed descriptors here, {', '.join(overlap)} also "
                "appear in that multicollinearity list - a skewed variable "
                "that is also highly correlated with another feature is a "
                "double reason a linear model needs care (e.g. dropping or "
                "combining one of the pair, or a monotonic transform), while "
                "for the winning XGBoost model neither skew nor this "
                "correlation is a correctness issue - at most a mild loss of "
                "interpretability if two correlated features split "
                "importance between them.\n"
            )
        else:
            lines.append(
                "None of the skewed descriptors identified here are also "
                "part of that high-correlation list, so skew and "
                "multicollinearity look like separate, non-compounding "
                "concerns for this dataset.\n"
            )

    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text("".join(lines), encoding="utf-8")

    print("".join(lines))
    print(f"Wrote {REPORT_PATH}\nWrote {PLOT_PATH}")


if __name__ == "__main__":
    main()
