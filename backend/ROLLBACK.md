# Model rollback procedure

## Current architecture

`models/production/model.pkl` + `models/production/metadata.json` are the
**only** pointer to the "active" model. `backend/app/inference.py`'s
`ModelService` loads these two files once, at process startup
(`backend/app/main.py`'s `lifespan`). There is no database row, no model
registry service, and no built-in versioned history of previously-deployed
models - each run of `ml/register_model.py` used to simply overwrite
`models/production/` in place, with no way to get the old model back short
of re-running the whole training pipeline (`ml/preprocess.py` ->
`ml/experiments_xgboost.py` -> `ml/select_winner.py`) and hoping it
reproduces the same artifact.

## What this change adds

`ml/register_model.py` now archives the *previous* production model before
overwriting it: if `models/production/metadata.json` already exists (i.e.
this isn't the very first registration), its `model_version` is read and
the current contents of `models/production/` (`model.pkl` +
`metadata.json`) are copied to `models/archive/<old_version>/` before the
new model is written. If a version's archive already exists, it is left
alone (re-registering the same version is a no-op archive-wise, never
clobbers a good archive with a partial one).

`models/archive/` is gitignored (like `models/production/*.pkl`) - this is
local/deploy-host state, not something committed to the repo. Each
deployment host that runs `ml/register_model.py` accumulates its own
archive; there is currently no shared/remote registry, so an archive on one
machine is not automatically available on another.

## How to roll back today

1. **Identify the version to roll back to.** Check
   `models/archive/<version>/metadata.json` for `model_version` and
   `trained_at`, or ask whoever last ran `ml/register_model.py` on that
   host which version preceded the current one. If nothing was ever
   archived for the version you want (e.g. this rollback feature didn't
   exist yet for that deployment), you must instead re-run the training
   pipeline from a checked-out git commit that produced that model
   version.

2. **Restore the archived files.**
   ```bash
   cp models/archive/<old_version>/model.pkl models/production/model.pkl
   cp models/archive/<old_version>/metadata.json models/production/metadata.json
   ```

3. **Restart the API process.** `ModelService` only loads the model at
   startup (by design - see `backend/app/main.py`'s `lifespan`), so the
   running process must be restarted (or the container/service redeployed)
   to pick up the restored files. There is no hot-reload.

4. **Verify.** `GET /model/info` should report the rolled-back
   `model_version`. Spot-check `POST /predict` on a known SMILES against
   previously-observed output if you have it.

5. **Note the rollback.** Nothing currently logs "this was a rollback"
   anywhere - only the `metadata.json` currently in `models/production/`
   is authoritative for "what's live". If a proper audit trail matters,
   record the rollback manually (deploy log, incident ticket, etc.) until
   a real model registry exists.

## Follow-up ideas (not implemented, out of scope for this MVP)

- A `models/archive/` retention policy - right now it grows unbounded, one
  directory per distinct `model_version` ever registered on a host.
- Recording provenance (git commit, training data hash) in `metadata.json`
  so an archived model can be traced back to the exact code/data that
  produced it, not just a version string.
- A real model registry (even a simple JSON manifest of
  `{version: {path, trained_at, metrics}}`) shared across deployment hosts,
  instead of each host's local `models/archive/` being independent.
- A CLI flag on `ml/register_model.py` (e.g. `--rollback <version>`) that
  performs steps 2-3 above automatically instead of by hand.
