# 📚 Tutorial — NGS WGS Variant-Calling Pipeline

A step-by-step guide to running the complete variant-calling workflow from raw FASTQ to
annotated VCF and HTML report.

---

## Prerequisites

| Requirement | Minimum Version |
|-------------|-----------------|
| Python      | 3.11            |
| Conda / Mamba | Latest stable |
| Snakemake   | 8.10            |
| Disk space  | ≥ 100 GB (for 30× WGS) |
| RAM         | ≥ 16 GB         |
| CPU cores   | ≥ 8 (recommended) |

---

## 1. Environment Setup

```bash
# Clone the repository
git clone https://github.com/adarshii/ngs.git
cd ngs

# Create and activate the conda environment
conda env create -f environment.yaml   # or use setup.sh
conda activate ngs-pipeline
```

### Install the Python package (for library use / tests)

```bash
pip install -e ".[dev]"
```

---

## 2. Prepare the Reference Genome

Download and index the GRCh38 reference genome:

```bash
bash scripts/prepare_reference.sh
```

This script:
1. Downloads the GRCh38 FASTA from NCBI
2. Creates BWA index (`bwa index`)
3. Creates SAMtools FAI index (`samtools faidx`)
4. Creates GATK sequence dictionary (`gatk CreateSequenceDictionary`)

---

## 3. Configure Your Samples

Edit `config/samples.tsv` to point to your FASTQ files:

```
sample  fastq_r1                    fastq_r2
NA12878 data/raw_data/NA12878_R1.fastq.gz  data/raw_data/NA12878_R2.fastq.gz
```

Review `config/config.yaml` and adjust tool parameters if needed (thread counts,
memory, quality thresholds, etc.).

---

## 4. Dry Run

Validate the workflow before submitting:

```bash
snakemake --cores 1 --dry-run
```

Snakemake will print every rule it would execute without actually running them.

---

## 5. Run the Pipeline

### Local machine (8 cores)

```bash
snakemake --cores 8
```

### HPC / SLURM cluster

```bash
snakemake --cores 8 --cluster "sbatch --mem={resources.memory} --cpus-per-task={threads}"
```

---

## 6. Check Outputs

After a successful run your `results/` directory will contain:

| Directory           | Contents                              |
|---------------------|---------------------------------------|
| `results/fastqc/`   | FastQC HTML quality reports           |
| `results/aligned/`  | Sorted, duplicate-marked BAM files    |
| `results/variants/` | GVCF and filtered VCF files           |
| `results/annotated/`| VEP-annotated VCFs                    |
| `results/reports/`  | Summary HTML report                   |

---

## 7. Parse VCF & Generate Report Manually

```bash
# Extract variant statistics
ngs-parse-vcf --vcf results/variants/NA12878.filtered.vcf.gz \
              --output results/reports/stats.json

# Generate HTML report
ngs-report --stats results/reports/stats.json \
           --output results/reports/pipeline_report.html \
           --title "NA12878 WGS Analysis"
```

---

## 8. Understanding Key Quality Metrics

| Metric       | Expected Value    | Interpretation                       |
|--------------|-------------------|--------------------------------------|
| Ts/Tv ratio  | 2.0 – 2.2         | Confirms biological variant signal   |
| Mean depth   | ≥ 30×             | Sufficient coverage for SNP calling  |
| Pass rate    | ≥ 80 %            | High-quality call set                |
| Mean QUAL    | ≥ 30              | Phred 30 = 1 error per 1 000 bases   |

---

## Next Steps

- See `docs/TROUBLESHOOTING.md` for common issues and solutions.
- See `docs/PUBLICATION_UPGRADE.md` for multi-sample joint calling, Docker, and cloud
  deployment.
- See `CONTRIBUTING.md` to contribute back to this project.
