# Decision: DVC for dataset/model versioning

**Recommendation: defer.** Do not adopt DVC now; revisit if/when the
dataset or model registry stops being fully reproducible from scratch by
a deterministic script pipeline, or when more than one dataset/model
needs to be tracked side by side with real storage-of-record semantics.

## Current state (why this is a real recommendation, not "it depends")

- `data/raw/`, `data/processed/`, and `models/**/*.pkl` are all gitignored
  (`.gitignore`) - they are build outputs, not source, by design.
- `ml/preprocess.py` self-downloads its one input
  (`delaney-processed.csv` from a public S3 URL) if `data/raw/` is empty
  - there is no manual dataset-acquisition step to lose track of.
- The full pipeline (`preprocess.py` -> `baseline.py` ->
  `experiments_xgboost.py` -> `experiments_fingerprint_models.py` ->
  `select_winner.py` -> `register_model.py`) is deterministic and cheap
  to rerun end to end (verified while doing this task: full rerun took
  well under two minutes on a laptop CPU, on a ~1,100-row dataset).
- CI (`.github/workflows/ci.yml`) reruns the ML pipeline from scratch on
  every push rather than pulling a cached/versioned artifact - the
  project has already implicitly chosen "regenerate, don't store" as its
  model-provenance strategy.
- There is exactly one dataset (ESOL/Delaney) and one production model at
  a time, with a simple built-in rollback mechanism
  (`models/archive/<version>/`, written by `register_model.py`'s
  `_archive_previous_production()`, documented in `backend/ROLLBACK.md`).
  DVC's main value - versioning large binary artifacts and letting
  teammates `dvc pull` the exact data/model a given commit used - doesn't
  apply when the artifact is fully and cheaply reconstructible from a
  pinned public URL plus deterministic code.

## Why not adopt now

DVC earns its keep when at least one of these is true, and none of them
are true here yet:
1. The raw dataset is large, private, or not trivially re-downloadable
   (this one is a small public CSV, self-fetched).
2. Regenerating the model is expensive (minutes-to-hours training,
   expensive compute) such that "just rerun the pipeline" is impractical
   for reviewers/CI. (Current full pipeline: well under two minutes.)
3. Multiple datasets/model versions need to coexist and be referenced by
   commit (e.g. A/B testing two training sets). Today there is one
   dataset and one production model.
4. Multiple contributors need bit-for-bit reproducible artifacts without
   each re-running training (this is a single-maintainer portfolio
   project).

Adopting DVC now would add a remote storage dependency (S3/GCS/etc. -
its own cost and credentials to manage, cutting against "no secrets in
git" simplicity noted in `OWASP_CHECKLIST.md`), a second tool for
contributors to learn, and `.dvc` metadata files to keep in sync with
git commits - for no reproducibility benefit this project doesn't
already have via "clone repo, run six scripts."

## When to revisit

- The dataset stops being small/free/public (e.g. moving to a larger or
  licensed dataset that can't be casually re-downloaded in CI).
- Training time grows enough that "just rerun it" stops being a
  reasonable CI/reviewer workflow.
- The project needs to compare/serve more than one model version
  concurrently, beyond what the existing `models/archive/` convention
  handles.
- A second contributor needs to reproduce an exact past training run
  without re-executing the pipeline themselves.

Any of those would justify introducing DVC (or an equivalent - MLflow's
artifact store, a cloud bucket with content-hashed paths) at that point;
none of them apply to the project as it stands today.
