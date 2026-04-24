# Aligned Data Directory

This directory contains BAM (Binary Alignment Map) files with aligned sequencing reads.

## Contents

```
aligned/
├── sample1.sorted.bam
├── sample1.sorted.bam.bai       # BAM index
├── sample1.dup_metrics.txt       # Duplicate metrics (Picard)
├── sample2.sorted.bam
├── sample2.sorted.bam.bai
├── sample2.dup_metrics.txt
└── ...
```

## File Format

### BAM File Structure

BAM (Binary Alignment/Map) format:
- Compressed binary version of SAM
- Space-efficient (~1/4 size of SAM)
- Contains header + aligned reads
- Supports indexing for fast lookup

### BAM Index (.bai)

- Created by `samtools index`
- Enables random access to BAM files
- Required for visualization (IGV, samtools)
- ~0.1% of BAM file size

## Processing Details

### Pipeline Steps

1. **Alignment (BWA-MEM)**
   - Maps trimmed reads to reference genome (GRCh38)
   - Read groups added (platform, library, center)
   - Output: SAM format

2. **Conversion & Sorting (SAMtools)**
   - Converts SAM → BAM (binary format)
   - Sorts by genomic coordinate
   - Compression level 9 (maximum)
   - Output: `sample.sorted.bam`

3. **Duplicate Marking (Picard)**
   - Identifies PCR duplicates
   - Marks but doesn't remove (research use)
   - Generates metrics file
   - Output: `sample.dup_metrics.txt`

4. **Indexing**
   - Creates BAI index for fast access
   - Output: `sample.sorted.bam.bai`

## File Sizes

| Data Type | Typical Size | Compression |
|-----------|--------------|-------------|
| Raw SAM | ~150-250 GB | Uncompressed |
| Compressed BAM | ~20-50 GB | ~8-10x smaller |
| BAM Index | 50-100 MB | Minimal |

## Quality Assessment

### Basic Statistics

```bash
# Get alignment summary
samtools flagstat sample1.sorted.bam

# Expected output:
# Total reads
# Properly paired
# Duplicates marked
# Mapping rate
```

### Detailed Inspection

```bash
# View header
samtools view -H sample1.sorted.bam | head -20

# View first 5 reads
samtools view sample1.sorted.bam | head -5

# Get depth at specific position
samtools depth -r chr1:1000-2000 sample1.sorted.bam | head

# Coverage statistics
samtools depth sample1.sorted.bam | awk '{sum+=$3; sumsq+=$3*$3; n++} END {print "Mean:", sum/n, "Stdev:", sqrt(sumsq/n - (sum/n)^2)}'
```

## Downstream Analysis

BAM files are used for:

1. **Variant Calling** → GATK HaplotypeCaller
2. **Visualization** → IGV, samtools tview
3. **QC Analysis** → Picard, samtools
4. **Custom Analysis** → Any BAM-compatible tool

## Storage Management

⚠️ **Large intermediate files:**

BAM files can be deleted after:
- Variant calling is complete
- Results have been validated
- Backup exists

**Safe deletion:**

```bash
# After variant calls are verified
rm sample1.sorted.bam sample1.sorted.bam.bai

# Reclaim ~20-50 GB per sample
```

**Keep BAM if:**
- Running additional analyses
- Joint calling across samples
- Publication quality assurance
- De novo discovery

## Visualization

### Using IGV (Integrative Genomics Viewer)

```bash
# Install IGV
conda install -c bioconda igv

# Launch and load BAM
igv &
# File → Open → sample1.sorted.bam
```

### Using samtools

```bash
# Text-based viewer
samtools tview sample1.sorted.bam data/reference/GRCh38.fa

# Navigate: Press '?' for help
# Jump to position: 'g' then enter chromosome:position
```

## Troubleshooting

### BAM file not indexed
```bash
samtools index sample1.sorted.bam
# Creates sample1.sorted.bam.bai
```

### Corrupted BAM file
```bash
# Validate
samtools quickcheck sample1.sorted.bam

# Detailed check
samtools view -c sample1.sorted.bam
```

### IGV can't read BAM
- Ensure .bai index exists
- Index must be in same directory as BAM
- Index name must match BAM name

## Read Groups

BAM headers include read group information:

```
@RG	ID:sample1	SM:sample1	PL:ILLUMINA	LB:TruSeq	CN:NGSC
```

- **ID:** Unique identifier
- **SM:** Sample name
- **PL:** Platform (ILLUMINA, PACBIO, etc.)
- **LB:** Library
- **CN:** Sequencing center

## Performance Tips

```bash
# Fast file size check
ls -lh *.bam

# Quick coverage estimate
samtools depth sample1.sorted.bam | awk '{sum+=$3} END {print "Total bases covered:", sum}'

# Parallelized indexing
for bam in *.sorted.bam; do
  samtools index -@ 4 "$bam" &
done
wait
```

## References

- **SAM/BAM Format:** https://samtools.github.io/hts-specs/SAMv1.pdf
- **SAMtools:** https://samtools.github.io/
- **IGV:** https://software.broadinstitute.org/software/igv/
- **GATK Best Practices:** https://gatk.broadinstitute.org/
