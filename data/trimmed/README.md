# Trimmed Data Directory

This directory contains intermediate trimmed reads after adapter and quality filtering.

## Contents

```
trimmed/
├── sample1_R1.trimmed.fastq.gz
├── sample1_R2.trimmed.fastq.gz
├── sample1_unpaired.fastq.gz      # Single reads after partner removal
├── sample2_R1.trimmed.fastq.gz
├── sample2_R2.trimmed.fastq.gz
└── ...
```

## Processing Details

### What Happens Here

The `trimmomatic` rule processes raw FASTQ files:

1. **Adapter Removal**
   - Removes Illumina TruSeq adapters
   - Pattern matching at 5' and 3' ends

2. **Quality Trimming**
   - LEADING: Remove leading poor quality (Q < 10)
   - TRAILING: Remove trailing poor quality (Q < 10)
   - SLIDINGWINDOW: 4bp window, Q ≥ 20

3. **Length Filtering**
   - Minimum read length: 50 bp
   - Shorter reads discarded

### File Naming

- **Paired after trimming:** `{sample}_R1.trimmed.fastq.gz` + `{sample}_R2.trimmed.fastq.gz`
- **Unpaired reads:** `{sample}_unpaired.fastq.gz` (one read from broken pair)

## File Sizes

| Stage | Typical Size |
|-------|-------------|
| Raw FASTQ | 30-50 GB |
| Trimmed (paired) | 25-45 GB | 
| Data loss | 10-20% |

## Quality Metrics

To assess trimming quality:

```bash
# Count reads before/after
echo "Before:" && gunzip -c ../raw_data/sample1_R1.fastq.gz | grep -c "^+"
echo "After:" && gunzip -c sample1_R1.trimmed.fastq.gz | grep -c "^+"
```

## Next Steps in Pipeline

Trimmed reads proceed to:
1. **Alignment** → `results/aligned/`
2. **Quality control** → `results/fastqc/`

## Storage Management

⚠️ **Intermediate files - can be deleted after variant calling:**

```bash
# Delete after alignment is complete and verified
rm -f *.trimmed.fastq.gz

# Reclaim ~10-20 GB per sample
```

**Safety tip:** Keep trimmed files until you confirm variant calling completed successfully.

## Troubleshooting

### File count mismatch
- Some read pairs may be discarded if one read fails filters
- This is normal
- Unpaired reads can still be used (see Trimmomatic documentation)

### Empty trimmed files
- Indicates raw data quality issues
- Check with FastQC first
- Review Trimmomatic parameters in config.yaml

### Pipeline fails at alignment
- Verify trimmed files aren't corrupted
- Check that paired files have similar line counts

```bash
zcat sample1_R1.trimmed.fastq.gz | wc -l
zcat sample1_R2.trimmed.fastq.gz | wc -l
# Should both be divisible by 4 and roughly equal
```
