# Annotated Variants Directory

This directory contains functionally annotated variant calls with predicted consequences and impact scores.

## Contents

```
annotated/
├── sample1.annotated.vcf.gz       # Annotated variant calls
├── sample1.annotated.vcf.gz.tbi   # Tabix index
├── sample1_annotation_report.txt   # Annotation summary
├── sample2.annotated.vcf.gz
├── sample2.annotated.vcf.gz.tbi
└── ...
```

## Annotation Process

### VEP (Variant Effect Predictor)

Ensembl VEP adds functional predictions:

1. **Variant Consequence**
   - Missense
   - Frameshift
   - Synonymous
   - Splice site
   - Intergenic
   - etc.

2. **Impact Prediction**
   - **HIGH:** Frameshift, stop codon, splice
   - **MODERATE:** Missense, inframe indel
   - **LOW:** Synonymous, intron
   - **MODIFIER:** Intergenic, intronic

3. **Protein Scores**
   - **SIFT:** Deleterious vs Tolerated
   - **PolyPhen-2:** Probably damaging vs Benign

4. **Population Data**
   - **gnomAD_AF:** Allele frequency in gnomAD
   - **dbSNP ID:** If known variant

## VCF Info Fields Added

### Example Annotated Variant

```
CSQ=T|missense_variant|MODERATE|BRCA1|ENSG00000012048|ENST00000357654|protein_coding|2/24|c.68A>G|p.Asp23Gly|75/1863|SIFT=deleterious|PolyPhen=probably_damaging|gnomAD_AF=0.0001
```

### Field Meanings

| Field | Value | Meaning |
|-------|-------|----------|
| Consequence | missense_variant | Type of variant |
| Impact | MODERATE | Predicted impact level |
| Gene | BRCA1 | Gene name |
| Transcript | ENST000... | Affected transcript |
| Exon | 2/24 | Which exon |
| Coding | c.68A>G | HGVS coding nomenclature |
| Protein | p.Asp23Gly | HGVS protein nomenclature |
| SIFT | deleterious | Conservation score |
| PolyPhen | probably_damaging | Structural impact |
| gnomAD_AF | 0.0001 | Population frequency |

## Using Annotated VCF

### Filter by Impact

```bash
# Extract HIGH impact variants
bcftools view sample1.annotated.vcf.gz | awk 'BEGIN {FS="\t"; OFS="\t"} 
  /^#/ {print; next}
  $8 ~ /HIGH/ {print}' > high_impact.vcf

# Extract variants with damaging predictions
bcftools view sample1.annotated.vcf.gz | grep -E "(SIFT=deleterious|PolyPhen=probably_damaging)" > damaging.vcf
```

### Extract Variant Features

```bash
# Parse annotation (requires VCFannotationTools or similar)
# Or use bcftools query
bcftools query -f '%CHROM:%POS %REF/%ALT\t%INFO/CSQ\n' sample1.annotated.vcf.gz | head
```

### Common Queries

```bash
# Count high-impact variants
bcftools view sample1.annotated.vcf.gz | awk 'BEGIN {count=0} $8 ~ /HIGH/ {count++} END {print "HIGH impact variants:", count}'

# Get rare variants (gnomAD_AF < 0.01)
bcftools view sample1.annotated.vcf.gz | awk '$8 ~ /gnomAD_AF=([0-9]*\.)?[0-9]{1,4}[^0-9]/ {print}' | wc -l

# Extract pathogenic predictions
bcftools view sample1.annotated.vcf.gz | grep -E "(deleterious|probably_damaging)" | wc -l
```

## Interpretation Guide

### Consequence Priority

**Most Important (Top to Bottom):**
1. Frameshift
2. Stop codon (gained/lost)
3. Splice site (±2bp)
4. Missense (amino acid change)
5. Inframe indel
6. Synonymous (silent)
7. Intronic/Intergenic

### Impact Scoring

**SIFT Score (Sorting Intolerant From Tolerant)**
- **< 0.05:** Deleterious (intolerant to substitution)
- **≥ 0.05:** Tolerated (can tolerate substitution)

**PolyPhen-2 Score (Polymorphism Phenotyping)**
- **0.0 - 0.45:** Benign
- **0.45 - 0.95:** Possibly damaging
- **0.95 - 1.0:** Probably damaging

## Variant Prioritization

### High Priority (Likely Pathogenic)

```bash
# HIGH impact + damaging score + rare
bcftools view sample1.annotated.vcf.gz | awk '
  $8 ~ /HIGH/ && 
  ($8 ~ /SIFT=deleterious/ || $8 ~ /PolyPhen=probably_damaging/) && 
  $8 ~ /gnomAD_AF=[0-9.]*e-[0-9]|0\.00[0-9]/ {
    print
}' > high_priority_variants.vcf
```

### Medium Priority (Possibly Pathogenic)

```bash
# MODERATE impact + damaging + rare
# (similar to above but with MODERATE impact)
```

## Population Data

### gnomAD Reference Panels

| Population | Description |
|------------|-------------|
| AFR | African |
| AMR | Admixed American |
| ASJ | Ashkenazi Jewish |
| EAS | East Asian |
| FIN | Finnish |
| NFE | Non-Finnish European |
| OTH | Other |
| SAS | South Asian |

### Allele Frequency Thresholds

For rare disease association:
- **Very rare:** AF < 0.0001 (1 in 10,000)
- **Rare:** AF < 0.001 (1 in 1,000)
- **Uncommon:** AF < 0.01 (1 in 100)
- **Common:** AF > 0.01

## Generating Reports

### Automated Report

The pipeline generates `sample1_annotation_report.txt`:

```
Annotation Summary Report
========================================
Sample: sample1
Analysis Date: 2026-04-24

=== VARIANT COUNTS BY IMPACT ===
HIGH: 1,234
MODERATE: 56,789
LOW: 234,567
MODIFIER: 4,000,000

=== CONSEQUENCE DISTRIBUTION ===
missense_variant: 45,123
synonymous_variant: 234,567
intergenic_variant: 3,900,000
splice_region_variant: 567
...

=== PATHOGENIC PREDICTIONS ===
Deleterious (SIFT): 12,345
Probably Damaging (PolyPhen): 23,456
Both: 5,678

=== RARE VARIANTS (AF < 0.01) ===
Total: 234,567
HIGH impact: 123
MODERATE impact: 5,678
```

## Integration with Clinical Analysis

### For Disease Association

1. Filter for HIGH/MODERATE impact
2. Filter for rarity (AF < 0.01)
3. Check for damaging predictions (SIFT/PolyPhen)
4. Check disease-specific databases (ClinVar, HGMD)
5. Validate with literature

### For Pharmacogenomics

1. Extract variants in drug metabolism genes (CYP, etc.)
2. Check PharmGKB database
3. Predict phenotype (poor/normal/ultra metabolizer)

## Limitations

⚠️ **Important considerations:**

- **Prediction accuracy:** ~70-80% for impact prediction
- **Incomplete annotation:** Some variants may lack prediction data
- **Reference bias:** Predictions based on mostly European genomes
- **Novel variants:** New variants may not have population data
- **Not clinical:** Predictions are computational, require validation

## Troubleshooting

### No annotation data
- Check that VEP was run successfully
- Verify reference genome version (GRCh38)
- Check for errors in VEP output

### Missing CSQ field
- VEP may have failed silently
- Check config for VEP parameters
- Re-run VEP step: `snakemake --force -j 8 rule_vep_annotation`

## References

- **VEP Documentation:** https://useast.ensembl.org/info/docs/tools/vep/
- **VEP Consequences:** https://useast.ensembl.org/info/genome/variation/prediction/predicted_data.html
- **ClinVar:** https://www.ncbi.nlm.nih.gov/clinvar/
- **gnomAD:** https://gnomad.broadinstitute.org/
- **HGVS Nomenclature:** https://varnomen.hgvs.org/
