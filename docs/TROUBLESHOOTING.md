# 🔧 Troubleshooting Guide — NGS WGS Variant-Calling Pipeline

Common errors, their causes, and how to fix them.

---

## 1. Environment / Installation Issues

### `conda: command not found`

**Cause:** Conda is not installed or not on `PATH`.

**Fix:**
```bash
# Install Miniconda
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
bash Miniconda3-latest-Linux-x86_64.sh
source ~/.bashrc
```

---

### `snakemake: command not found`

**Cause:** The conda environment is not activated.

**Fix:**
```bash
conda activate ngs-pipeline
```

---

## 2. Reference Genome Issues

### `bwa mem: no such file or directory: data/reference/GRCh38.fa`

**Cause:** Reference genome has not been downloaded or indexed.

**Fix:**
```bash
bash scripts/prepare_reference.sh
```

---

### `GATK: Missing required argument --sequence-dictionary`

**Cause:** The GATK `.dict` file is missing.

**Fix:**
```bash
gatk CreateSequenceDictionary -R data/reference/GRCh38.fa
```

---

## 3. Memory Errors

### `java.lang.OutOfMemoryError: Java heap space` (Picard / GATK)

**Cause:** Insufficient Java heap allocation.

**Fix:** Increase `java_mem` in `config/config.yaml`:
```yaml
gatk:
  java_mem: "16G"
picard:
  java_mem: "16G"
```

---

### `Killed` (process killed by OS)

**Cause:** System OOM killer terminated the process.

**Fix:** Reduce thread count or use fewer parallel jobs:
```bash
snakemake --cores 4  # instead of 8
```

---

## 4. VCF / Variant Calling Issues

### `HaplotypeCaller: Input files are not in the same order as the reference`

**Cause:** BAM file chromosome order does not match the reference dictionary.

**Fix:**
```bash
samtools sort -o sample.sorted.bam sample.bam
samtools index sample.sorted.bam
```

---

### `RuntimeError: VCF header sample column mismatch`

**Cause:** Read-group (`@RG`) tags are missing or inconsistent.

**Fix:** Ensure read groups are added during BWA alignment:
```bash
bwa mem -R "@RG\tID:sample\tSM:sample\tPL:ILLUMINA" ...
```

---

## 5. Quality Control Issues

### Ts/Tv ratio << 2.0

**Cause:** High false-positive rate; filters may be too lenient.

**Fix:** Tighten quality thresholds in `config/config.yaml`:
```yaml
bcftools:
  min_quality: 50
  min_depth: 15
```

---

### FastQC: `Overrepresented sequences` FAIL

**Cause:** Adapter contamination in raw reads.

**Fix:** This is expected before trimming. Trimmomatic removes adapters in the next step.
If it persists after trimming, check the adapter sequence in config:
```yaml
trimmomatic:
  adapters: "AGATCGGAAGAGCACACGTCTGAACTCCAGTCAC"
```

---

## 6. Snakemake Workflow Issues

### `MissingInputException: Missing input files for rule`

**Cause:** A dependency output file was not created.

**Fix:** Run with `--rerun-incomplete` to rerun failed steps:
```bash
snakemake --cores 8 --rerun-incomplete
```

---

### `IncompleteFilesException`

**Cause:** A previous run was interrupted mid-write.

**Fix:**
```bash
snakemake --cores 8 --rerun-incomplete
# or clean and restart
snakemake --cores 8 --forceall
```

---

## 7. Test Failures

### `ModuleNotFoundError: No module named 'ngs'`

**Cause:** The package has not been installed in development mode.

**Fix:**
```bash
pip install -e ".[dev]"
```

---

### `pytest: no tests found`

**Cause:** Tests are run from the wrong directory.

**Fix:**
```bash
# Run from the repository root
pytest tests/
```

---

## Getting Further Help

- Check the [GitHub Issues](https://github.com/adarshii/ngs/issues) for known problems.
- Open a new issue with:
  - Full error message and traceback
  - Snakemake version (`snakemake --version`)
  - Python version (`python --version`)
  - Operating system and available RAM/CPU
