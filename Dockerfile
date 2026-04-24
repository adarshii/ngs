# ─────────────────────────────────────────────────────────────────────────────
# NGS WGS Variant-Calling Pipeline — Dockerfile
# Base image: continuumio/miniconda3 (bioconda-friendly)
# ─────────────────────────────────────────────────────────────────────────────

FROM continuumio/miniconda3:24.1.2-0

LABEL maintainer="Adarsh Dheeraj Dubey <adarshii@users.noreply.github.com>"
LABEL description="NGS WGS Variant-Calling Pipeline"
LABEL version="1.0.0"

# ── system packages ───────────────────────────────────────────────────────────
RUN apt-get update && apt-get install -y --no-install-recommends \
        procps \
        curl \
    && rm -rf /var/lib/apt/lists/*

# ── conda environment ─────────────────────────────────────────────────────────
WORKDIR /workspace

COPY environment.yaml .
RUN conda env create -f environment.yaml \
    && conda clean --all --yes

# Make the conda environment the default shell environment
SHELL ["conda", "run", "-n", "ngs-pipeline", "/bin/bash", "-c"]

# ── copy source and install Python package ────────────────────────────────────
COPY . .
RUN pip install --no-cache-dir -e ".[dev]"

# ── default directories ───────────────────────────────────────────────────────
RUN mkdir -p data/raw_data data/reference data/trimmed \
             results/fastqc results/aligned results/variants \
             results/annotated results/reports

# ── entrypoint ────────────────────────────────────────────────────────────────
ENV PATH="/opt/conda/envs/ngs-pipeline/bin:${PATH}"

ENTRYPOINT ["conda", "run", "--no-capture-output", "-n", "ngs-pipeline"]
CMD ["snakemake", "--help"]
