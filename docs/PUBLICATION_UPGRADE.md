# 🚀 Publication Upgrade Guide — NGS WGS Variant-Calling Pipeline

Advanced configurations for scaling to multi-sample cohorts, containerisation,
cloud execution, and publication-grade analysis.

---

## 1. Multi-Sample Joint Genotyping

Joint genotyping across cohorts improves sensitivity by sharing information
between samples.

### Step 1 — Generate per-sample GVCFs

Already done by the standard pipeline.

### Step 2 — Combine GVCFs

```bash
gatk CombineGVCFs \
  -R data/reference/GRCh38.fa \
  --variant results/variants/sample1.g.vcf.gz \
  --variant results/variants/sample2.g.vcf.gz \
  -O results/variants/cohort.g.vcf.gz
```

### Step 3 — Joint Genotyping

```bash
gatk GenotypeGVCFs \
  -R data/reference/GRCh38.fa \
  -V results/variants/cohort.g.vcf.gz \
  -O results/variants/cohort.vcf.gz
```

Enable in `config/config.yaml`:
```yaml
joint_genotyping:
  enabled: true
```

---

## 2. VQSR (Variant Quality Score Recalibration)

VQSR is the gold-standard filtering approach for cohorts ≥ 30 samples.

```bash
# SNP recalibration
gatk VariantRecalibrator \
  -R data/reference/GRCh38.fa \
  -V results/variants/cohort.vcf.gz \
  --resource:hapmap,known=false,training=true,truth=true,prior=15 hapmap.vcf.gz \
  --resource:omni,known=false,training=true,truth=false,prior=12 omni.vcf.gz \
  --resource:1000G,known=false,training=true,truth=false,prior=10 1000G_snps.vcf.gz \
  --resource:dbsnp,known=true,training=false,truth=false,prior=2 dbsnp.vcf.gz \
  -an QD -an MQ -an MQRankSum -an ReadPosRankSum -an FS -an SOR \
  -mode SNP \
  -O results/variants/cohort.snps.recal \
  --tranches-file results/variants/cohort.snps.tranches
```

---

## 3. Docker / Container Deployment

### Build the image

```bash
docker build -t ngs-pipeline:latest .
```

### Run the pipeline inside Docker

```bash
docker run --rm \
  -v $(pwd)/data:/workspace/data \
  -v $(pwd)/results:/workspace/results \
  -v $(pwd)/config:/workspace/config \
  ngs-pipeline:latest \
  snakemake --cores 8
```

### Using docker-compose

```bash
docker-compose up pipeline
```

---

## 4. Cloud Execution (AWS / Google Cloud)

### AWS Batch via Snakemake

```bash
snakemake --cores 8 \
  --aws-s3-prefix s3://my-bucket/ngs-run/ \
  --default-remote-provider S3 \
  --default-remote-prefix my-bucket
```

### Google Cloud Life Sciences

See [Snakemake docs](https://snakemake.readthedocs.io/en/stable/executing/cloud.html)
for GCP/GLS configuration.

---

## 5. Ancestry and Population Stratification

Use gnomAD allele frequencies from VEP annotation to flag common variants:

```bash
bcftools filter \
  -e 'INFO/gnomADe_AF > 0.01' \
  -o results/variants/rare_variants.vcf.gz \
  results/annotated/sample.annotated.vcf.gz
```

---

## 6. Structural Variant Calling (SVs)

Add SV calling with Manta or LUMPY:

```bash
configManta.py --bam results/aligned/sample.markdup.bam \
               --referenceFasta data/reference/GRCh38.fa \
               --runDir results/sv/manta
results/sv/manta/runWorkflow.py -j 8
```

---

## 7. Publication-Ready Figures

Use the `matplotlib` integration in `ngs.report.html` or generate standalone plots:

```python
from ngs.parsers.vcf import VCFParser
import matplotlib.pyplot as plt

parser = VCFParser("results/variants/sample.filtered.vcf.gz")
stats = parser.parse_vcf()

types = stats["variant_types"]
plt.bar(types.keys(), types.values())
plt.xlabel("Variant Type")
plt.ylabel("Count")
plt.title("Variant Type Distribution")
plt.tight_layout()
plt.savefig("figures/variant_types.pdf", dpi=300)
```

---

## 8. Reproducibility Checklist for Publication

- [ ] Pin all tool versions in `environment.yaml`
- [ ] Record `snakemake --version` in `config/config.yaml`
- [ ] Archive raw FASTQ in SRA/ENA with accession numbers
- [ ] Tag the exact pipeline version used: `git tag v1.0.0`
- [ ] Include `config/config.yaml` as supplementary material
- [ ] Report Ts/Tv ratio, depth distribution, and pass-rate in Methods section
- [ ] Share the HTML report as supplementary file
