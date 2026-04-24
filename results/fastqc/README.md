# FastQC Quality Reports Directory

This directory contains quality control reports from raw sequence data assessment.

## Contents

```
fastqc/
├── sample1_R1_fastqc.html        # Read 1 quality report
├── sample1_R1_fastqc.zip         # Detailed data
├── sample1_R2_fastqc.html        # Read 2 quality report
├── sample1_R2_fastqc.zip
├── sample2_R1_fastqc.html
├── sample2_R1_fastqc.zip
└── ...
```

## FastQC Analysis

### What FastQC Checks

1. **Per-base Quality**
   - Phred quality scores (Q-values)
   - Distribution across read length
   - Green = high quality (≥30)
   - Orange = medium (20-30)
   - Red = low (<20)

2. **Sequence Content**
   - Base composition (A, T, G, C)
   - Should be relatively balanced
   - Biased composition suggests contamination

3. **GC Content**
   - Expected bell curve distribution
   - Deviation may indicate contamination
   - Typical range: ±5% from theoretical

4. **Adapter Content**
   - Illumina adapters at 3' end
   - Should be minimal (<5%)
   - High content → need trimming

5. **N Content**
   - Positions with ambiguous base calls
   - Should be <1%
   - High N content → low coverage or sequencing issues

6. **Sequence Duplication**
   - PCR duplicates in raw reads
   - Some duplication normal
   - >50% suggests over-amplification

## Report Interpretation

### Quality Indicators

**✅ PASS (Green):**
- Per-base quality: Q ≥ 30 throughout
- Adapter content: < 2%
- GC content: Normal distribution
- N content: < 1%
- Duplication: < 10%

**⚠️ WARN (Orange):**
- Per-base quality: Q 20-30 in portion
- Adapter content: 2-10%
- GC content: Slight deviation
- Slight sequence bias

**❌ FAIL (Red):**
- Per-base quality: Q < 20
- Adapter content: > 10%
- GC content: Highly biased
- N content: > 5%
- Duplication: > 50%

## Using HTML Reports

### Open Reports

```bash
# Open in web browser
open results/fastqc/sample1_R1_fastqc.html

# Or from command line
firefox results/fastqc/sample1_R1_fastqc.html &
```

### Batch Report Generation

To create a summary of all samples:

```bash
# View all reports in directory
ls -la results/fastqc/*.html

# Create index.html for browsing all reports
echo "<h1>FastQC Reports</h1><ul>" > results/fastqc/index.html
for f in results/fastqc/*_fastqc.html; do
  echo "<li><a href='$(basename $f)'>$(basename $f)</a></li>" >> results/fastqc/index.html
done
echo "</ul>" >> results/fastqc/index.html

open results/fastqc/index.html
```

## Quality Assessment Workflow

### Pre-Trimming

1. Check raw FastQC reports
2. Identify:
   - Adapter contamination
   - Quality degradation
   - GC bias
   - N content

### Post-Trimming

1. Run FastQC on trimmed reads
2. Expected improvements:
   - ✓ Adapter content → near 0%
   - ✓ Per-base quality → improved (Q ≥ 30)
   - ✓ N content → reduced

## Troubleshooting Quality Issues

### Problem: Low Quality Scores

**Causes:**
- Sequencer issue
- Old sequencing reagents
- High cluster density

**Solution:**
- Trim more aggressively (SLIDINGWINDOW:4:15)
- Contact sequencing provider
- May not be usable

### Problem: High Adapter Content

**Causes:**
- Insufficient insert size
- Over-clustering
- Library prep issue

**Solution:**
- Increase Trimmomatic stringency
- Use custom adapter sequences
- May require resequencing

### Problem: GC Bias

**Causes:**
- Contamination
- PCR bias
- Sequencing primer issues

**Solution:**
- Check for common contaminants (vector, rRNA, etc.)
- Reduce PCR cycles
- May affect variant calling

### Problem: High Duplication

**Causes:**
- Low input DNA
- Over-amplification
- Sequencing depth

**Note:**
- Raw duplication expected
- Picard removes marked duplicates
- Not usually disqualifying

## Performance Metrics

### Expected Metrics (Illumina WGS)

| Metric | Expected Range | Action |
|--------|----------------|--------|
| Q30 bases | > 80% | Good |
| Mean quality | > 35 | Good |
| Adapter % | < 2% | Good |
| GC content | ±5% | Good |
| Duplication | 0-10% | Normal |

### Read Length Distribution

- **Typical Illumina:** 150 bp
- **NovaSeq:** 150-250 bp
- **HiSeq:** 100-150 bp
- After trimming: 50-150 bp expected

## Batch Analysis

### Run FastQC on Multiple Files

```bash
# Run on all raw FASTQ files
fastqc -t 4 data/raw_data/*.fastq.gz -o results/fastqc/

# Run on trimmed files for comparison
fastqc -t 4 data/trimmed/*.fastq.gz -o results/fastqc/
```

### Compare Pre/Post Trimming

```bash
# Create comparison document
cat > QC_Comparison.txt << EOF
Sample: sample1

Pre-Trimming:
- $(grep 'Per base sequence quality' results/fastqc/sample1_R1_fastqc/summary.txt)
- $(grep 'Adapter Content' results/fastqc/sample1_R1_fastqc/summary.txt)

Post-Trimming:
- Check trimmed report here
EOF

cat QC_Comparison.txt
```

## Advanced Analysis

### Extract Raw Data from FastQC Output

```bash
# FastQC generates zip files with detailed data
unzip -l results/fastqc/sample1_R1_fastqc.zip

# Extract and analyze per-base quality
unzip -p results/fastqc/sample1_R1_fastqc.zip \
  sample1_R1_fastqc/fastqc_data.txt | grep -A 20 'Per base sequence quality'
```

### Custom QC Scripts

For automated batch processing:

```bash
#!/bin/bash
# check_fastqc_quality.sh

for html in results/fastqc/*_fastqc.html; do
  if grep -q 'FAIL' "$html"; then
    echo "⚠️ WARNING: $(basename $html) has FAIL status"
  else
    echo "✓ $(basename $html) PASSED"
  fi
done
```

## References

- **FastQC Documentation:** https://www.bioinformatics.babraham.ac.uk/projects/fastqc/
- **Phred Quality Scores:** https://en.wikipedia.org/wiki/Phred_quality_score
- **Illumina Quality Control:** https://support.illumina.com/content/dam/illumina-support/documents/documentation/system_documentation/nextseq/nextseq-500-system-guide-15048776-h.pdf
- **NGS Quality Control:** https://www.ncbi.nlm.nih.gov/pmc/articles/PMC5887334/
