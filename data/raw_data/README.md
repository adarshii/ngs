# Raw Data Directory

This directory contains input FASTQ files for the NGS pipeline.

## Organization

```
raw_data/
├── sample1_R1.fastq.gz       # Read 1 (forward reads)
├── sample1_R2.fastq.gz       # Read 2 (reverse reads)
├── sample2_R1.fastq.gz
├── sample2_R2.fastq.gz
└── ...
```

## File Naming Convention

- **Paired-end reads:** `{sample_id}_R1.fastq.gz` and `{sample_id}_R2.fastq.gz`
- **Single-end reads:** `{sample_id}.fastq.gz`
- Always use `.fastq.gz` (gzip compressed)

## Getting Test Data

To generate example test data:

```bash
bash scripts/generate_example_data.sh
```

This creates small FASTQ files suitable for testing the pipeline.

## File Size Expectations

- **Typical whole genome (30× coverage):** 30-50 GB per sample
- **Exome sequencing:** 2-5 GB per sample
- **Low-coverage:** 5-10 GB per sample

## Quality Checks

Before running the pipeline:

```bash
# Check file integrity
gzip -t *.fastq.gz

# Check file size (should be > 100 MB for typical data)
ls -lh *.fastq.gz

# Validate FASTQ format
head -4 sample1_R1.fastq.gz | gunzip
```

## Sample Sheet Setup

After adding files, create `config/samples.tsv`:

```tsv
sample_id	read1_path				read2_path				platform	sample_name
sample1	data/raw_data/sample1_R1.fastq.gz	data/raw_data/sample1_R2.fastq.gz	ILLUMINA	S001
sample2	data/raw_data/sample2_R1.fastq.gz	data/raw_data/sample2_R2.fastq.gz	ILLUMINA	S002
```

## Troubleshooting

### Files not found in pipeline
- Check file paths in `config/samples.tsv`
- Verify files exist: `ls -l <path>`
- Check for typos in sample names

### Permission denied
```bash
chmod 644 *.fastq.gz
```

### File format issues
- Must be FASTQ format (not FASTA)
- Must be gzip compressed (`.gz`)
- Use `gunzip -c` to verify format

## Notes

⚠️ **Large file handling:**
- Use fast SSD storage for better I/O performance
- Consider data backup before running analysis
- Monitor disk space during processing

✅ **Best practices:**
- Keep raw data read-only: `chmod 444 *.fastq.gz`
- Document data source and sequencing platform
- Record sample metadata
