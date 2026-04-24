# EXECUTION GUIDE - NGS WGS VARIANT-CALLING PIPELINE

## Complete Step-by-Step Instructions

This guide covers everything needed to successfully execute the pipeline from start to finish.

---

## 📋 PHASE 1: PRE-EXECUTION SETUP (30 minutes)

### Step 1.1: Clone Repository

```bash
git clone https://github.com/adarshii/ngs.git
cd ngs
pwd  # Verify you're in correct directory
```

### Step 1.2: Run Setup Script

```bash
bash setup.sh
```

This automatically:
- ✓ Creates conda environment
- ✓ Installs all dependencies
- ✓ Creates directory structure
- ✓ Validates configuration

### Step 1.3: Activate Environment

```bash
conda activate ngs-wgs
```

Verify activation:
```bash
which python  # Should show conda path
python --version  # Should be 3.11.x
```

### Step 1.4: Prepare Reference Genome

First-time setup only:

```bash
bash scripts/prepare_reference.sh
```

This:
- ✓ Downloads GRCh38 reference (3.2 GB)
- ✓ Creates required indexes
- ✓ Validates integrity

**Time required:** 20-30 minutes (download dependent)

---

## 📁 PHASE 2: DATA PREPARATION (15 minutes)

### Step 2.1: Add FASTQ Files

Copy your sequencing data:

```bash
# Copy to raw_data directory
cp /path/to/sample1_R1.fastq.gz data/raw_data/
cp /path/to/sample1_R2.fastq.gz data/raw_data/
cp /path/to/sample2_R1.fastq.gz data/raw_data/
cp /path/to/sample2_R2.fastq.gz data/raw_data/

# Or create test data (for testing)
bash scripts/generate_example_data.sh
```

**Expected Structure:**
```
data/raw_data/
├── sample1_R1.fastq.gz
├── sample1_R2.fastq.gz
├── sample2_R1.fastq.gz
└── sample2_R2.fastq.gz
```

### Step 2.2: Create Sample Sheet

Edit `config/samples.tsv`:

```bash
nano config/samples.tsv
```

Format (tab-separated):
```
sample_id       read1                               read2                               platform  sample_name
sample1         data/raw_data/sample1_R1.fastq.gz   data/raw_data/sample1_R2.fastq.gz   ILLUMINA  S001
sample2         data/raw_data/sample2_R1.fastq.gz   data/raw_data/sample2_R2.fastq.gz   ILLUMINA  S002
```

### Step 2.3: Verify Configuration

Check `config/config.yaml`:

```bash
# Key parameters to verify:
grep "reference:" config/config.yaml
grep "output:" config/config.yaml
grep "trimmomatic:" -A 3 config/config.yaml
grep "gatk:" -A 3 config/config.yaml
```

---

## 🧪 PHASE 3: VALIDATION (10 minutes)

### Step 3.1: Dry Run (Validate Workflow)

```bash
snakemake -n --configfile config/config.yaml
```

**Expected Output:**
```
Job counts:
    count   jobs
    1       all
    1       fastqc
    1       trimmomatic
    1       bwa_alignment
    ...
    12      total
```

### Step 3.2: DAG Visualization (Optional)

```bash
snakemake --dag --configfile config/config.yaml | dot -Tpdf > dag.pdf
open dag.pdf  # View workflow diagram
```

### Step 3.3: Check Inputs Exist

```bash
# Verify reference genome
ls -lh data/reference/GRCh38.fa*

# Verify FASTQ files
ls -lh data/raw_data/*.fastq.gz

# Verify samples.tsv
head config/samples.tsv
```

---

## ▶️ PHASE 4: EXECUTION (2-4 hours)

### Step 4.1: Run Full Pipeline

```bash
# Single-threaded (safe for testing)
snakemake --configfile config/config.yaml

# Parallel execution (8 cores - recommended)
snakemake -j 8 --configfile config/config.yaml

# Parallel execution (all cores)
snakemake -j --configfile config/config.yaml

# With progress visualization
snakemake -j 8 --configfile config/config.yaml --progress
```

**Typical Runtime:**
- Single sample: 40-150 minutes
- Depends on:
  - File size (whole genome ~100x coverage ≈ 30-50 GB)
  - CPU threads available
  - Disk I/O speed

### Step 4.2: Monitor Execution

Watch progress in real-time:

```bash
# In separate terminal, watch log files
tail -f results/logs/*.log

# Or check main pipeline log
tail -f .snakemake/log
```

### Step 4.3: Handle Errors

If rules fail:

```bash
# Check specific tool log
cat results/logs/bwa_sample1.log

# Re-run specific rule
snakemake -j 8 --configfile config/config.yaml --touch bwa_alignment

# Continue from where it failed
snakemake -j 8 --configfile config/config.yaml
```

---

## 📊 PHASE 5: RESULTS ANALYSIS (30 minutes)

### Step 5.1: View HTML Report

```bash
# Open in browser
open results/reports/pipeline_report.html

# Or view in terminal
cat results/reports/pipeline_report.html | w3m  # if w3m installed
```

### Step 5.2: Examine Variant Statistics

```bash
# View variant counts
cat results/reports/sample1_variant_stats.txt

# Check Ts/Tv ratio (should be ~2.0-2.2)
grep "Ts/Tv" results/reports/sample1_variant_stats.txt
```

### Step 5.3: Inspect VCF Files

```bash
# View header
bcftools view -h results/annotated/sample1.annotated.vcf.gz | head -20

# Count variants
bcftools view -H results/annotated/sample1.annotated.vcf.gz | wc -l

# View first 10 variants
bcftools view results/annotated/sample1.annotated.vcf.gz | head -15
```

### Step 5.4: Check Quality Metrics

```bash
# FastQC reports
ls results/fastqc/*.html
open results/fastqc/sample1_R1_fastqc.html

# Alignment statistics
samtools flagstat results/aligned/sample1.sorted.bam

# Duplicate metrics
cat results/aligned/sample1.dup_metrics.txt
```

---

## 📁 PHASE 6: OUTPUT FILES

### Generated Files Structure

```
results/
├── fastqc/
│   ├── sample1_R1_fastqc.html      # Quality report
│   ├── sample1_R1_fastqc.zip       # Detailed data
│   └── ...
│
├── trimmed/
│   ├── sample1_R1.trimmed.fastq.gz # Trimmed reads
│   └── sample1_R2.trimmed.fastq.gz
│
├── aligned/
│   ├── sample1.sorted.bam          # Final BAM file
│   ├── sample1.sorted.bam.bai      # Index
│   └── sample1.dup_metrics.txt     # Duplicate statistics
│
├── variants/
│   ├── sample1.raw.vcf.gz          # Raw variants
│   ├── sample1.raw.vcf.gz.tbi      # Index
│   ├── sample1.filtered.vcf.gz     # Filtered variants
│   └── sample1.filtered.vcf.gz.tbi # Index
│
├── annotated/
│   ├── sample1.annotated.vcf.gz    # Functional annotation
│   └── sample1.annotated.vcf.gz.tbi
│
└── reports/
    ├── pipeline_report.html        # Main report
    ├── sample1_variant_stats.txt  # Statistics
    └── sample2_variant_stats.txt
```

### Key Output Descriptions

| File | Size | Purpose |
|------|------|---------|
| .annotated.vcf.gz | 50-200 MB | Final variant calls with annotations |
| .sorted.bam | 20-100 GB | Aligned reads (can be deleted after variant calling) |
| _fastqc.html | 1-5 MB | Quality assessment report |
| pipeline_report.html | 500 KB | Summary of entire analysis |

---

## 🔄 PHASE 7: ADVANCED EXECUTION

### Cluster Submission (HPC)

#### SLURM

```bash
# Create submission script: submit_ngs.sh
#!/bin/bash
#SBATCH --job-name=ngs-pipeline
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=16
#SBATCH --mem=64G
#SBATCH --time=12:00:00
#SBATCH --output=pipeline.log

conda activate ngs-wgs
snakemake -j 16 --configfile config/config.yaml

# Submit
sbatch submit_ngs.sh
```

#### SGE

```bash
# Create submission script: submit_ngs.sge
#!/bin/bash
#$ -N ngs-pipeline
#$ -pe multi-thread 16
#$ -l h_vmem=4G
#$ -o pipeline.log
#$ -e pipeline.err

conda activate ngs-wgs
snakemake -j 16 \\
    --cluster "qsub -l h_vmem={resources.mem_mb}M" \\
    --configfile config/config.yaml

# Submit
qsub submit_ngs.sge
```

### Multi-Sample Processing

```bash
# Edit samples.tsv to include all samples
cat config/samples.tsv
# sample1    ...
# sample2    ...
# sample3    ...

# Run entire pipeline
snakemake -j 8 --configfile config/config.yaml

# Generate joint genotyping report
python scripts/parse_vcf.py --vcf results/annotated/combined.vcf.gz
```

### Docker Execution (Optional)

```bash
# Build Docker image (if Dockerfile provided)
docker build -t ngs-pipeline .

# Run pipeline in Docker
docker run -v $(pwd):/work ngs-pipeline \\
    snakemake -j 8 --configfile /work/config/config.yaml
```

---

## 🛠️ PHASE 8: TROUBLESHOOTING

### Common Issues

**Issue: "Reference genome not found"**
```bash
# Solution:
bash scripts/prepare_reference.sh
# Verify:
ls -l data/reference/GRCh38.fa*
```

**Issue: "Sample file not found"**
```bash
# Check paths
head config/samples.tsv
# Verify files exist
ls -l data/raw_data/*.fastq.gz
```

**Issue: "Memory error"**
```bash
# Reduce threads (uses less memory)
snakemake -j 4 --configfile config/config.yaml
# Or increase system memory available
```

**Issue: "Disk space error"**
```bash
# Check available space
df -h
# Clean intermediate files (after successful completion)
rm results/trimmed/*.fastq.gz
rm results/aligned/*.bam  # Keep filtered VCFs
```

### Debug Mode

```bash
# Run with verbose output
snakemake -j 8 --configfile config/config.yaml -v

# Show commands being executed
snakemake -j 8 --configfile config/config.yaml --printshellcmds

# Keep temporary files for inspection
snakemake -j 8 --configfile config/config.yaml --keep-incomplete
```

---

## 📞 Getting Help

### Check Logs

```bash
# View specific tool logs
cat results/logs/bwa_sample1.log
cat results/logs/haplotypecaller_sample1.log

# View snakemake log
cat .snakemake/log
```

### Documentation

- **docs/TROUBLESHOOTING.md** - 10+ issue categories with solutions
- **docs/TUTORIAL.md** - Detailed explanation of each step
- **CONTRIBUTING.md** - How to report issues

### External Resources

- GATK docs: https://gatk.broadinstitute.org/
- Snakemake: https://snakemake.readthedocs.io/
- VEP: https://useast.ensembl.org/info/docs/tools/vep/

---

## 📝 Summary Timeline

| Phase | Time | Task |
|-------|------|------|
| 1 | 30 min | Setup and environment |
| 2 | 15 min | Data preparation |
| 3 | 10 min | Validation |
| 4 | 2-4 hrs | Pipeline execution |
| 5 | 30 min | Results analysis |
| **Total** | **3-5 hours** | Complete analysis |

---

## ✅ Checklist

Before running pipeline:
- [ ] Setup completed successfully
- [ ] Environment activated
- [ ] Reference genome downloaded and indexed
- [ ] FASTQ files in data/raw_data/
- [ ] Sample sheet (config/samples.tsv) filled out
- [ ] Configuration reviewed (config/config.yaml)
- [ ] Dry run validated
- [ ] Sufficient disk space (>500 GB recommended)

After pipeline completes:
- [ ] No errors in execution logs
- [ ] Results directory populated
- [ ] HTML report generated and readable
- [ ] Variant statistics reasonable
- [ ] Variants can be loaded in IGV/other viewers

---

## 🎉 Next Steps

After successful execution:

1. **Analyze Results** → docs/TUTORIAL.md
2. **Interpret Variants** → docs/TROUBLESHOOTING.md
3. **Scale to Production** → docs/PUBLICATION_UPGRADE.md
4. **Share Analysis** → Upload HTML report to lab wiki/GitHub

---

**Version:** 1.0.0  
**Last Updated:** 2026-04-24  
**Status:** ✅ Ready for Production Use
