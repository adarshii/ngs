#!/usr/bin/env python3
"""
NGS Pipeline - Data Validation Script
Validates FASTQ files, BAM files, and VCF files for quality and format

Usage:
    python validate_data.py --fastq <file> --output <report>
    python validate_data.py --bam <file> --reference <ref.fa>
    python validate_data.py --vcf <file>

Author: Bioinformatics Pipeline
Date: 2026-04-24
"""

import argparse
import gzip
import subprocess
from pathlib import Path


class FastqValidator:
    """Validate FASTQ file format and quality"""
    
    def __init__(self, fastq_file):
        self.fastq_file = fastq_file
        self.errors = []
        self.warnings = []
        self.stats = {}
    
    def validate_format(self):
        """Check FASTQ format validity"""
        try:
            if self.fastq_file.endswith('.gz'):
                f = gzip.open(self.fastq_file, 'rt')
            else:
                f = open(self.fastq_file, 'r')
            
            line_count = 0
            valid_lines = True
            
            for line in f:
                line_count += 1
                if (line_count - 1) % 4 == 0 and not line.startswith('@'):
                    valid_lines = False
                    self.errors.append(f"Invalid header line at {line_count}")
                    break
            
            f.close()
            
            if valid_lines and line_count % 4 == 0:
                self.stats['total_reads'] = line_count // 4
                self.stats['format_status'] = 'VALID'
                return True
            else:
                self.errors.append(f"File has {line_count} lines (not divisible by 4)")
                return False
                
        except Exception as e:
            self.errors.append(f"Error reading file: {str(e)}")
            return False
    
    def validate_quality(self):
        """Check sequence quality scores"""
        try:
            if self.fastq_file.endswith('.gz'):
                f = gzip.open(self.fastq_file, 'rt')
            else:
                f = open(self.fastq_file, 'r')
            
            line_no = 0
            quality_scores = []
            read_lengths = []
            
            for line in f:
                line_no += 1
                if line_no % 4 == 0:
                    quality_scores.extend([ord(c) - 33 for c in line.strip()])
                elif line_no % 4 == 2:
                    read_lengths.append(len(line.strip()))
            
            f.close()
            
            if quality_scores:
                self.stats['mean_quality'] = sum(quality_scores) / len(quality_scores)
                self.stats['min_quality'] = min(quality_scores)
                self.stats['max_quality'] = max(quality_scores)
                self.stats['mean_length'] = sum(read_lengths) / len(read_lengths)
                
                if self.stats['mean_quality'] < 20:
                    self.warnings.append(f"Mean quality {self.stats['mean_quality']:.1f} is low")
                
                return True
            else:
                self.errors.append("No quality data found")
                return False
        
        except Exception as e:
            self.errors.append(f"Error validating quality: {str(e)}")
            return False
    
    def generate_report(self):
        """Generate validation report"""
        report = f"""FASTQ Validation Report
{'='*50}
File: {self.fastq_file}
"""
        
        if self.stats.get('total_reads'):
            report += f"\nTotal reads: {self.stats['total_reads']:,}\n"
            report += f"Mean quality: {self.stats.get('mean_quality', 0):.1f}\n"
            report += f"Quality range: {self.stats.get('min_quality', 0)}-{self.stats.get('max_quality', 0)}\n"
            report += f"Mean read length: {self.stats.get('mean_length', 0):.0f} bp\n"
        
        if self.errors:
            report += f"\nErrors ({len(self.errors)}):\n"
            for err in self.errors:
                report += f"  - {err}\n"
        
        if self.warnings:
            report += f"\nWarnings ({len(self.warnings)}):\n"
            for warn in self.warnings:
                report += f"  - {warn}\n"
        
        status = "VALID" if not self.errors else "INVALID"
        report += f"\nStatus: {status}\n"
        
        return report


class BamValidator:
    """Validate BAM file format and integrity"""
    
    def __init__(self, bam_file):
        self.bam_file = bam_file
        self.errors = []
        self.stats = {}
    
    def validate_integrity(self):
        """Check BAM file integrity using samtools"""
        try:
            result = subprocess.run(
                ['samtools', 'quickcheck', self.bam_file],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                self.stats['integrity'] = 'VALID'
                return True
            else:
                self.errors.append("BAM file failed integrity check")
                return False
        
        except FileNotFoundError:
            self.errors.append("samtools not found. Install with: conda install samtools")
            return False
    
    def get_statistics(self):
        """Get BAM statistics"""
        try:
            result = subprocess.run(
                ['samtools', 'flagstat', self.bam_file],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                self.stats['flagstat'] = lines
                return True
            else:
                self.errors.append("Could not get BAM statistics")
                return False
        
        except FileNotFoundError:
            self.errors.append("samtools not found")
            return False
    
    def validate_index(self):
        """Check if BAM index exists and is valid"""
        bai_file = self.bam_file + '.bai'
        if Path(bai_file).exists():
            self.stats['index'] = 'EXISTS'
            return True
        else:
            self.errors.append(f"Index file not found: {bai_file}")
            return False
    
    def generate_report(self):
        """Generate validation report"""
        report = f"""BAM Validation Report
{'='*50}
File: {self.bam_file}
"""
        
        report += f"\nIntegrity: {self.stats.get('integrity', 'UNKNOWN')}\n"
        report += f"Index: {self.stats.get('index', 'MISSING')}\n"
        
        if self.stats.get('flagstat'):
            report += f"\nAlignment Statistics:\n"
            for line in self.stats['flagstat']:
                report += f"  {line}\n"
        
        if self.errors:
            report += f"\nErrors ({len(self.errors)}):\n"
            for err in self.errors:
                report += f"  - {err}\n"
        
        status = "VALID" if not self.errors else "INVALID"
        report += f"\nStatus: {status}\n"
        
        return report


class VcfValidator:
    """Validate VCF file format"""
    
    def __init__(self, vcf_file):
        self.vcf_file = vcf_file
        self.errors = []
        self.stats = {}
    
    def validate_format(self):
        """Check VCF format validity"""
        try:
            if self.vcf_file.endswith('.gz'):
                f = gzip.open(self.vcf_file, 'rt')
            else:
                f = open(self.vcf_file, 'r')
            
            variant_count = 0
            
            for line in f:
                if line.startswith('##'):
                    continue
                elif line.startswith('#CHROM'):
                    fields = line.strip().split('\t')
                    if len(fields) < 8:
                        self.errors.append("Header missing required columns")
                        return False
                else:
                    variant_count += 1
                    fields = line.strip().split('\t')
                    if len(fields) < 8:
                        self.errors.append(f"Variant line {variant_count} has insufficient columns")
                        return False
            
            f.close()
            
            self.stats['variant_count'] = variant_count
            self.stats['format_status'] = 'VALID' if variant_count > 0 else 'EMPTY'
            return True
        
        except Exception as e:
            self.errors.append(f"Error reading VCF: {str(e)}")
            return False
    
    def validate_index(self):
        """Check if VCF index exists"""
        tbi_file = self.vcf_file + '.tbi'
        if Path(tbi_file).exists():
            self.stats['index'] = 'EXISTS'
            return True
        else:
            self.errors.append(f"Index file not found: {tbi_file}")
            return False
    
    def generate_report(self):
        """Generate validation report"""
        report = f"""VCF Validation Report
{'='*50}
File: {self.vcf_file}
"""
        
        report += f"\nVariants: {self.stats.get('variant_count', 0):,}\n"
        report += f"Index: {self.stats.get('index', 'MISSING')}\n"
        report += f"Format: {self.stats.get('format_status', 'UNKNOWN')}\n"
        
        if self.errors:
            report += f"\nErrors ({len(self.errors)}):\n"
            for err in self.errors:
                report += f"  - {err}\n"
        
        status = "VALID" if not self.errors and self.stats.get('variant_count', 0) > 0 else "INVALID"
        report += f"\nStatus: {status}\n"
        
        return report


def main():
    parser = argparse.ArgumentParser(description='Validate bioinformatics data files')
    parser.add_argument('--fastq', help='FASTQ file to validate')
    parser.add_argument('--bam', help='BAM file to validate')
    parser.add_argument('--vcf', help='VCF file to validate')
    parser.add_argument('--reference', help='Reference FASTA for BAM validation')
    parser.add_argument('--output', help='Output report file')
    
    args = parser.parse_args()
    
    report = ""
    
    if args.fastq:
        validator = FastqValidator(args.fastq)
        validator.validate_format()
        validator.validate_quality()
        report = validator.generate_report()
    
    elif args.bam:
        validator = BamValidator(args.bam)
        validator.validate_integrity()
        validator.validate_index()
        validator.get_statistics()
        report = validator.generate_report()
    
    elif args.vcf:
        validator = VcfValidator(args.vcf)
        validator.validate_format()
        validator.validate_index()
        report = validator.generate_report()
    
    else:
        print("Please specify --fastq, --bam, or --vcf")
        return 1
    
    if args.output:
        with open(args.output, 'w') as f:
            f.write(report)
        print(f"✓ Report written to {args.output}")
    else:
        print(report)
    
    return 0


if __name__ == '__main__':
    exit(main())
