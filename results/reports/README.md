# Analysis Reports Directory

This directory contains comprehensive analysis reports and summary statistics.

## Contents

```
reports/
├── pipeline_report.html            # Main HTML report
├── sample1_variant_stats.txt       # Variant statistics
├── sample1_fastqc_summary.txt      # QC summary
├── sample2_variant_stats.txt
└── analysis_summary.txt            # Overall summary
```

## Main Report

### pipeline_report.html

**Publication-ready HTML report with:**

1. **Summary Statistics**
   - Total variants
   - Pass rate
   - Ts/Tv ratio
   - Mean quality
   - Mean depth

2. **Variant Type Distribution**
   - SNPs vs INDELs
   - Multi-allelic variants
   - Percentage breakdown

3. **Quality Metrics**
   - Mean quality score
   - Median quality score
   - High quality (≥30) variants
   - Medium quality (≥20) variants

4. **Sequencing Depth**
   - Mean depth
   - Median depth
   - Min/max coverage
   - Depth distribution

5. **Visual Design**
   - Professional gradient backgrounds
   - Color-coded statistics
   - Responsive mobile layout
   - Print-friendly format

### Opening Report

```bash
# View in web browser
open results/reports/pipeline_report.html

# Or
firefox results/reports/pipeline_report.html
```

## Variant Statistics

### sample1_variant_stats.txt

Detailed statistics for each sample:

```
=== VARIANT CALLING STATISTICS ===
Sample ID: sample1
Analysis Date: 2026-04-24
Reference: GRCh38

=== OVERALL STATISTICS ===
Total variants called: 4,521,234
Variants passed filters: 4,215,987
Pass rate: 93.2%
Filtered out: 305,247

=== VARIANT CLASSIFICATION ===
Single Nucleotide Polymorphisms (SNPs): 3,415,876
  - Percentage: 81.1%
  - Transitions: 2,400,000
  - Transversions: 1,015,876
  
Insertion/Deletion (INDEL): 723,445
  - Percentage: 17.2%
  - Insertions: 392,156
  - Deletions: 331,289
  
Multi-allelic sites: 76,666
  - Percentage: 1.8%

=== TRANSITION/TRANSVERSION RATIO ===
Total transitions: 2,400,000
Total transversions: 1,015,876
Ts/Tv ratio: 2.36
Expected range: 2.0-2.2
Status: ✓ Within expected range

=== QUALITY METRICS ===
Mean variant quality: 48.5
Median variant quality: 45.0
Quality score range: 1-255

Variants by quality category:
  High quality (QUAL ≥ 30): 4,100,500 (97.3%)
  Medium quality (QUAL 20-30): 100,000 (2.4%)
  Low quality (QUAL < 20): 15,487 (0.4%)

=== SEQUENCING DEPTH ===
Mean depth (DP): 35.2×
Median depth: 34.0×
Minimum depth: 1×
Maximum depth: 500×
Depth std dev: 8.4

Positions by coverage:
  Low coverage (DP < 10): 45,000 (1.1%)
  Standard (10 ≤ DP ≤ 100): 4,120,000 (97.7%)
  High coverage (DP > 100): 50,987 (1.2%)

=== ALLELE FREQUENCY DISTRIBUTION ===
Homozygous reference: 95.8% of genome
Heterozygous: 3.8% of variants
Homozygous alternate: 0.4% of variants

=== VARIANT NOVELTY ===
Known variants (dbSNP): 4,100,000 (97.3%)
Novel variants: 115,987 (2.7%)

=== FUNCTIONAL IMPACT ===
HIGH impact variants: 1,234
MODERATE impact: 56,789
LOW impact: 234,567
MODIFIER (non-coding): 3,922,897

=== FILTERING SUMMARY ===
Filters applied:
  QUAL ≥ 30: Removed 45,000
  DP ≥ 10: Removed 89,000
  DP ≤ 500: Removed 1,200
  Other: Removed 170,047

=== CHROMOSOME DISTRIBUTION ===
Chr1: 123,456 variants (2.9%)
Chr2: 115,234 variants (2.7%)
...
ChrX: 34,567 variants (0.8%)
ChrY: 2,345 variants (0.1%)
ChrMT: 5,678 variants (0.1%)

=== INDEL SIZE DISTRIBUTION ===
1bp indels: 450,000 (62.2%)
2bp indels: 150,000 (20.7%)
3-10bp: 100,000 (13.8%)
>10bp: 23,445 (3.2%)

=== QUALITY CONTROL PASS/FAIL ===
Ts/Tv ratio: ✓ PASS (2.36, expected 2.0-2.2)
Transition/transversion: ✓ PASS
Pass rate: ✓ PASS (>90%)
Mean quality: ✓ PASS (>40)
Mean depth: ✓ PASS (20-50×)

Overall QC Status: ✓ PASSED
```

## Statistical Analysis

### Interpreting Key Metrics

**Ts/Tv Ratio**
- Germline: 2.0-2.2
- Somatic: 0.8-1.0
- Exome: 3.0-3.5 (more transitions)
- Genome: 2.1 (expected)

**Mean Quality**
- < 30: Low confidence
- 30-40: Medium confidence
- > 40: High confidence

**Mean Depth**
- < 10×: Unreliable
- 10-50×: Standard
- > 100×: Over-sequenced

## Report Generation

### Automatic Generation

Reports generated automatically by pipeline:

```bash
# Run pipeline
snakemake -j 8 --configfile config/config.yaml

# Reports created in results/reports/
```

### Manual Report Generation

```bash
# Generate HTML report
python scripts/generate_report.py \
  --stats variant_stats.json \
  --output custom_report.html \
  --title "Custom Analysis Report"

# Generate statistics from VCF
python scripts/parse_vcf.py \
  --vcf results/variants/sample1.filtered.vcf.gz \
  --output results/reports/sample1_stats.txt
```

## Multi-Sample Comparison

### Creating Comparison Report

```bash
# Create comparative statistics
cat > comparison_report.txt << EOF
Comparative Analysis Report
============================

Sample\tTotal Variants\tPass Rate\tMean Quality\tMean Depth\tTs/Tv
EOF

# Add data for each sample
for vcf in results/variants/*.filtered.vcf.gz; do
  sample=$(basename $vcf .filtered.vcf.gz)
  # Extract stats and append to report
  echo "$sample\t..." >> comparison_report.txt
done

cat comparison_report.txt
```

## Exporting for Publication

### Convert to PDF

```bash
# Install wkhtmltopdf
sudo apt-get install wkhtmltopdf

# Convert HTML to PDF
wkhtmltopdf results/reports/pipeline_report.html results/reports/pipeline_report.pdf
```

### Create Publication Tables

```bash
# Extract key statistics for paper
cat > supplementary_table.txt << EOF
Table S1. Variant Calling Summary Statistics

Sample\tTotal\tPassed\t% Pass\tSNPs\tINDELs\tTs/Tv\tMean QUAL\tMean DP
EOF

# Populate table from stats files
```

## Reproducibility Documentation

### Create Methods Section

Documentation for publication:

```
=== METHODS ===

Variant Calling Pipeline

Raw sequencing reads were processed following GATK Best Practices for 
whole genome sequencing. Quality control was performed with FastQC. 
Reads were trimmed using Trimmomatic to remove adapters and low-quality 
bases. Trimmed reads were aligned to GRCh38 using BWA-MEM. 

PCR duplicates were marked with Picard MarkDuplicates. Variants were 
called using GATK HaplotypeCaller. Raw variants were filtered for QUAL ≥ 30, 
DP ≥ 10, MQ ≥ 20. Variants were functionally annotated using Ensembl VEP.

Pipeline version: 1.0.0
Analysis date: 2026-04-24
Reference genome: GRCh38
```

## Quality Metrics Reference

### Expected Ranges (Whole Genome)

| Metric | Typical Range | Below Expected | Above Expected |
|--------|---------------|---------------|-----------------|
| Total variants | 3-5M | Undercalling | Overcalling |
| SNP rate | 80-85% | Bias | Annotation error |
| Pass rate | 90-95% | Over-filtered | Lenient filters |
| Ts/Tv | 2.0-2.2 | Transition bias | Transversion bias |
| Mean quality | 35-50 | Low conf calls | High conf calls |
| Mean depth | 20-50× | Low coverage | Over-sequenced |

## Troubleshooting

### Empty Reports
- Check that pipeline completed successfully
- Verify input VCF files exist
- Check for parsing errors

### Missing Statistics
- Ensure parse_vcf.py ran without errors
- Check VCF file format validity
- Verify output directory permissions

### Report Display Issues
- Clear browser cache
- Try different browser
- Check HTML file permissions

## References

- **GATK Best Practices:** https://gatk.broadinstitute.org/hc/en-us/articles/360035535932
- **VCF Format:** https://samtools.github.io/hts-specs/VCFv4.2.pdf
- **Phred Scores:** https://en.wikipedia.org/wiki/Phred_quality_score
