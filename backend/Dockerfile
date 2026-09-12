# Multi-stage build - RDKit/xgboost wheels are large, so we install into a
# venv in the builder stage and copy only the venv + app into a slim final
# image (see TODO/devops/TODO_containerization.md's note on image size).
FROM python:3.14-slim AS builder

WORKDIR /app
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY backend/requirements.txt .
# xgboost's PyPI wheel pulls in nvidia-nccl-cu13 (~250MB) for multi-GPU
# support we don't use (CPU-only inference) - uninstalled in this same
# stage/layer so the final image (COPY --from=builder below) never
# contains it; uninstalling in a later layer wouldn't shrink the image,
# since Docker layers are additive.
RUN pip install --no-cache-dir -r requirements.txt \
    && pip uninstall -y nvidia-nccl-cu13

FROM python:3.14-slim

# RDKit's Draw/rdMolDraw2D (used to render structure_svg) needs these X11
# libs even for headless SVG rendering - without them the import fails at
# runtime (ImportError: libXrender.so.1), which pip install alone doesn't
# catch since it only installs Python packages.
RUN apt-get update && apt-get install --no-install-recommends -y \
    libxrender1 libxext6 libexpat1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# backend/app needs its parent package layout (backend.app.*) and the
# production model produced by the ml/ pipeline (not committed to git -
# run ml/preprocess.py -> ml/experiments_xgboost.py -> ml/select_winner.py
# -> ml/register_model.py first, see ml/TODO_model_registry.md).
COPY backend/__init__.py backend/__init__.py
COPY backend/app backend/app
COPY models/production models/production

EXPOSE 8000
CMD ["uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
