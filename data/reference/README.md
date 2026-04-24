# Reference Genome Directory

This directory contains the reference genome and associated indexes required for sequence alignment and variant calling.

## Files Expected

```
reference/
├── GRCh38.fa              # Reference FASTA (created by script)
├── GRCh38.fa.fai          # FASTA index (samtools)
├── GRCh38.dict            # Sequence dictionary (GATK)
├── GRCh38.fa.bwt          # BWA index
├── GRCh38.fa.pac
├── GRCh38.fa.ann
├── GRCh38.fa.amb
└── GRCh38.fa.sa
```

## Setup Reference Genome

**First time setup (automatic):**

```bash
bash scripts/prepare_reference.sh
```

This script:
1. Downloads GRCh38 reference from NCBI
2. Creates FASTA index (samtools faidx)
3. Creates sequence dictionary (GATK)
4. Creates BWA indexes
5. Verifies all indexes

**Manual setup:**

```bash
# Download reference (GRCh38)
cd data/reference

wget ftp://ftp.ncbi.nlm.nih.gov/genomes/all/GCA/000/001/405/GCA_000001405.39_GRCh38.p13/GCA_000001405.39_GRCh38.p13_genomic.fna.gz

gunzip GCA_000001405.39_GRCh38.p13_genomic.fna.gz
mv GCA_000001405.39_GRCh38.p13_genomic.fna GRCh38.fa

# Create indexes
samtools faidx GRCh38.fa
gatk CreateSequenceDictionary -R GRCh38.fa
bwa index GRCh38.fa
```

## Genome Sizes

| Assembly | File Size | Compressed | Build Info |
|----------|-----------|------------|------------|
| GRCh38   | 3.2 GB    | ~900 MB    | Current human reference |
| GRCh37   | 3.1 GB    | ~890 MB    | Legacy (used in older studies) |
| T2T-CHM13| 3.3 GB    | ~950 MB    | Telomere-to-telomere complete |

## Available Reference Genomes

### Human Genomes

**GRCh38 (Recommended)**
- Latest primary assembly
- Most annotations available
- Standard for research
- FTP: `ftp://ftp.ncbi.nlm.nih.gov/genomes/all/GCA/000/001/405/GCA_000001405.39_GRCh38.p13/`

**GRCh37/hg19**
- Older reference (legacy)
- Still used in some studies
- More historical data available
- FTP: `ftp://ftp.ncbi.nlm.nih.gov/genomes/all/GCA/000/001/405/GCA_000001405.14_GRCh37.p13/`

**T2T-CHM13**
- Complete telomere-to-telomere reference
- Includes previously missing regions
- Research/specialized use

### Other Organisms

For non-human genomes, modify the config to use appropriate reference:

```yaml
reference:
  genome: "data/reference/custom_genome.fa"
  download_url: "<your_genome_url>"
```

## Verify Reference Setup

```bash
# Check FASTA file
ls -lh GRCh38.fa
head -2 GRCh38.fa

# Check indexes exist
ls -l GRCh38.fa.*

# Validate indexes
samtools faidx GRCh38.fa | head -5

# Test BWA index
bwa index -a bwtsw GRCh38.fa (already done, just verify no errors)
```

## Troubleshooting

### Download Failed
```bash
# Retry with curl
curl -O ftp://ftp.ncbi.nlm.nih.gov/.../GRCh38.fa.gz

# Or use Ensembl mirror
wget ftp://ftp.ensembl.org/pub/release-latest/fasta/homo_sapiens/dna/Homo_sapiens.GRCh38.dna.primary_assembly.fa.gz
```

### Index Creation Failed
```bash
# Check if FASTA is valid
gzip -t GRCh38.fa.gz  # if compressed

# Recreate indexes
samtools faidx GRCh38.fa
gatk CreateSequenceDictionary -R GRCh38.fa -O GRCh38.dict
bwa index -a bwtsw GRCh38.fa
```

### Disk Space Issues
- Full GRCh38 setup requires ~15 GB temporary space
- Downloaded file is compressed; decompression expands to 3.2 GB
- BWA indexes add ~500 MB
- Consider moving to faster SSD

## Storage Optimization

If disk space is limited:

```bash
# Keep only essential files (saves ~1 GB)
rm GRCh38.fa.amb GRCh38.fa.ann GRCh38.fa.bwt GRCh38.fa.pac GRCh38.fa.sa

# Note: This breaks BWA; only do if using alternative aligner
```

## Quality Control

```bash
# Check reference statistics
samtools faidx GRCh38.fa | awk '{sum+=$2; count++} END {print "Total bases:", sum; print "Chromosomes:", count}'

# Expected for GRCh38: ~3.2 billion bases, 195 sequences
```

## Documentation

- **NCBI FTP:** ftp://ftp.ncbi.nlm.nih.gov/genomes/
- **Ensembl:** https://www.ensembl.org/
- **UCSC Genome Browser:** https://genome.ucsc.edu/
- **GATK Reference:** https://gatk.broadinstitute.org/hc/en-us/articles/360035890811

## Notes

⚠️ **Important:**
- All downstream analyses depend on reference genome choice
- Changing reference requires re-alignment
- Always document which reference version was used
- Keep reference read-only: `chmod 444 GRCh38.fa*`
