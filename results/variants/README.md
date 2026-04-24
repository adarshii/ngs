# Variants Directory

This directory contains variant call sets (VCF files) from the pipeline.

## Contents

```
variants/
├── sample1.raw.vcf.gz            # Raw variant calls
├── sample1.raw.vcf.gz.tbi        # Tabix index
├── sample1.filtered.vcf.gz        # Quality-filtered variants
├── sample1.filtered.vcf.gz.tbi
├── sample1_variant_stats.txt      # Statistics
├── sample2.raw.vcf.gz
├── sample2.filtered.vcf.gz
└── ...
```

## VCF Format Overview

VCF (Variant Call Format) is a standard for representing genetic variants.

### File Structure

```
##fileformat=VCFv4.2
##source=HaplotypeCaller
##reference=GRCh38.fa
#CHROM  POS     ID      REF     ALT     QUAL    FILTER  INFO    FORMAT  sample1
chr1    1000    .       A       T       100     PASS    DP=40;AF=0.5    GT:GQ:DP        0/1:99:40
```

### Fields

| Field | Description |
|-------|-------------|
| CHROM | Chromosome |
| POS | Position |
| ID | Variant ID (dbSNP) or . |
| REF | Reference allele |
| ALT | Alternate allele(s) |
| QUAL | Variant quality score |
| FILTER | Filter status (PASS or reason) |
| INFO | Variant information |
| FORMAT | Genotype format |
| sample1, sample2... | Sample genotypes |

## Variant Calling Pipeline

### Stage 1: Raw Variants

**GATK HaplotypeCaller** discovers variants:
- De novo assembly approach
- Detects SNPs and INDELs
- GVCF output (keeps low-confidence calls)
- Unfiltered, all candidates included

**File:** `sample.raw.vcf.gz`

### Stage 2: Filtered Variants

**bcftools** applies quality filters:
- QUAL ≥ 30 (Phred score)
- DP ≥ 10 (coverage depth)
- DP ≤ 500 (removes repeat regions)
- MQ ≥ 20 (mapping quality)

**File:** `sample.filtered.vcf.gz`

**After filtering:**
- ~5-10% of raw calls typically removed
- Reduced false positives
- High-confidence variant set

## Variant Statistics

### Example Statistics Output

```
Sample: sample1
Analysis Date: 2026-04-24

=== OVERALL STATISTICS ===
Total variants: 4,521,234
Passed filter: 4,215,987
Pass rate: 93.2%

=== VARIANT TYPES ===
SNPs: 3,415,876 (81%)
INDELs: 723,445 (17%)
Multi-allelic: 76,666 (2%)

=== QUALITY METRICS ===
Mean quality: 48.5
Median quality: 45.0
High quality (≥30): 4,100,500
Medium quality (≥20): 4,200,000

=== DEPTH STATISTICS ===
Mean depth: 35.2×
Median depth: 34.0×
Minimum: 1×
Maximum: 500×

=== TRANSITION/TRANSVERSION ===
Ts/Tv ratio: 2.14
Expected: 2.0-2.2
Status: Within expected range ✓

=== ALLELE FREQUENCIES ===
Hom ref: 95.8%
Het: 3.8%
Hom alt: 0.4%
```

## File Access and Querying

### View VCF Header

```bash
zcat sample1.filtered.vcf.gz | head -20
# or
bcftools view --header-only sample1.filtered.vcf.gz
```

### Extract Specific Variants

```bash
# Extract variants from chromosome 1
bcftools view sample1.filtered.vcf.gz chr1 -O z -o chr1_variants.vcf.gz

# Extract variants in region
bcftools view sample1.filtered.vcf.gz chr1:1000-2000 -O z -o region_variants.vcf.gz

# Extract only SNPs
bcftools view -v snps sample1.filtered.vcf.gz -O z -o snps_only.vcf.gz

# Extract only INDELs
bcftools view -v indels sample1.filtered.vcf.gz -O z -o indels_only.vcf.gz
```

### Query Statistics

```bash
# Count variants
bcftools view -c sample1.filtered.vcf.gz

# Get variant density
bcftools view sample1.filtered.vcf.gz | awk 'NR>24 {chrom[$1]++} END {for (c in chrom) print c, chrom[c]}'

# Calculate Ts/Tv
bcftools view sample1.filtered.vcf.gz | awk 'NR>24 {
    if ($4 ~ /[AT]/ && $5 ~ /[AT]/) ts++
    else if ($4 ~ /[GC]/ && $5 ~ /[GC]/) ts++
    else tv++
} END {print "Ts/Tv:", ts/tv}'
```

## Downstream Annotation

Filtered variants proceed to:

**VEP (Variant Effect Predictor)**
- Predicts variant consequences
- Provides functional impact scores
- Adds population frequencies
- Output: `results/annotated/*.annotated.vcf.gz`

## Using VCF Files

### IGV Visualization

```bash
# IGV can display VCF files
# File → Open → sample1.filtered.vcf.gz
# Must have .tbi index in same directory
```

### Format Conversion

```bash
# VCF to BED (for overlapping with regions)
bcftools query -f '%CHROM\t%POS\t%POS\t%REF,%ALT\n' sample1.filtered.vcf.gz > variants.bed

# VCF to tab-delimited
bcftools query -f '%CHROM\t%POS\t%REF\t%ALT\t%QUAL\t%DP\n' sample1.filtered.vcf.gz > variants.txt

# VCF to uncompressed (if needed)
bcftools view sample1.filtered.vcf.gz -O v -o sample1.filtered.vcf
```

## Quality Control

### Validate VCF

```bash
# Check VCF validity
bcftools view sample1.filtered.vcf.gz > /dev/null && echo "Valid VCF"

# Check index
ls -l sample1.filtered.vcf.gz.tbi

# Verify index integrity
bcftools index -s sample1.filtered.vcf.gz
```

### Variant Consistency

```bash
# Check for chromosomes
bcftools query -f '%CHROM\n' sample1.filtered.vcf.gz | sort | uniq -c

# Check for duplicate positions
bcftools query -f '%CHROM:%POS\n' sample1.filtered.vcf.gz | sort | uniq -d | wc -l
# Should be 0 (no duplicates)
```

## Common Metrics

| Metric | Typical Range | Meaning |
|--------|---------------|----------|
| Total variants | 3-5 million | Human germline |
| SNP rate | 80-85% | Most variants are SNPs |
| INDEL rate | 15-20% | Rest are indels |
| Ts/Tv ratio | 2.0-2.2 | Evolutionary constraint |
| Pass rate | >90% | Quality filtering effectiveness |
| Mean depth | 20-50× | Sequencing coverage |
| Mean quality | >40 | High-confidence calls |

## Troubleshooting

### Empty VCF files
- Check BAM file quality
- Verify GATK parameters
- Check if reference genome matches

### Index missing
```bash
bcftools index -t sample1.filtered.vcf.gz
# Creates sample1.filtered.vcf.gz.tbi
```

### VCF won't open in IGV
- Ensure .tbi index exists
- Index must match VCF exactly
- Verify VCF is bgzip compressed

```bash
# Re-compress with bgzip
bcftools view sample1.filtered.vcf.gz -O z -o sample1.filtered.reindex.vcf.gz
bcftools index -t sample1.filtered.reindex.vcf.gz
```

## References

- **VCF Specification:** https://samtools.github.io/hts-specs/VCFv4.2.pdf
- **bcftools:** https://samtools.github.io/bcftools/
- **GATK HaplotypeCaller:** https://gatk.broadinstitute.org/hc/articles/13832687
- **VEP:** https://useast.ensembl.org/info/docs/tools/vep/
