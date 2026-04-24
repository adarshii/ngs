#!/usr/bin/env python3
"""
NGS Pipeline - VCF Parser and Statistics Extractor
Parses VCF files and extracts comprehensive variant statistics

Usage:
    python parse_vcf.py --vcf <vcf_file> --output <output_json>

Author: Bioinformatics Pipeline
Date: 2026-04-24
"""

import argparse
import json
import gzip
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Tuple


class VCFParser:
    """Parse VCF files and extract variant statistics"""

    def __init__(self, vcf_file: str):
        self.vcf_file = vcf_file
        self.variants = []
        self.stats = {
            'total_variants': 0,
            'passed_filter': 0,
            'variant_types': defaultdict(int),
            'quality_stats': {},
            'depth_stats': {},
            'chromosome_distribution': defaultdict(int)
        }

    def open_vcf(self):
        """Open VCF file (handles gzip)"""
        if self.vcf_file.endswith('.gz'):
            return gzip.open(self.vcf_file, 'rt')
        return open(self.vcf_file, 'r')

    def parse_vcf(self) -> Dict:
        """Parse VCF file and extract statistics"""
        qualities = []
        depths = []

        try:
            with self.open_vcf() as f:
                for line in f:
                    # Skip header
                    if line.startswith('#'):
                        continue

                    # Parse variant line
                    fields = line.strip().split('\t')
                    if len(fields) < 8:
                        continue

                    chrom = fields[0]
                    qual = fields[5]
                    info = fields[7]
                    filter_status = fields[6]

                    # Extract quality score
                    try:
                        qual_score = float(qual) if qual != '.' else 0
                        qualities.append(qual_score)
                    except ValueError:
                        qual_score = 0

                    # Extract depth from INFO field
                    depth = self._extract_depth(info)
                    if depth:
                        depths.append(depth)

                    # Determine variant type
                    var_type = self._get_variant_type(fields)

                    # Count statistics
                    self.stats['total_variants'] += 1
                    self.stats['chromosome_distribution'][chrom] += 1
                    self.stats['variant_types'][var_type] += 1

                    if filter_status == 'PASS' or filter_status == '.':
                        self.stats['passed_filter'] += 1

                    self.variants.append({
                        'chrom': chrom,
                        'pos': int(fields[1]),
                        'ref': fields[3],
                        'alt': fields[4],
                        'qual': qual_score,
                        'depth': depth,
                        'type': var_type,
                        'filter': filter_status
                    })

            # Calculate statistics
            self._calculate_quality_stats(qualities)
            self._calculate_depth_stats(depths)
            self._calculate_ts_tv_ratio()

            return dict(self.stats)

        except Exception as e:
            print(f"Error parsing VCF: {e}")
            return {}

    def _extract_depth(self, info: str) -> int:
        """Extract DP (depth) from INFO field"""
        for field in info.split(';'):
            if field.startswith('DP='):
                try:
                    return int(field.split('=')[1])
                except (ValueError, IndexError):
                    return None
        return None

    def _get_variant_type(self, fields: List[str]) -> str:
        """Determine variant type (SNP, INDEL, MNV, etc.)"""
        ref = fields[3]
        alt = fields[4]

        # Handle multi-allelic
        if ',' in alt:
            return 'MULTI_ALLELIC'

        # Determine type based on ref/alt lengths
        if len(ref) == 1 and len(alt) == 1:
            return 'SNP'
        elif len(ref) > len(alt):
            return 'DELETION'
        elif len(ref) < len(alt):
            return 'INSERTION'
        else:
            return 'MNV'  # Multi-nucleotide variant

    def _calculate_quality_stats(self, qualities: List[float]) -> None:
        """Calculate quality score statistics"""
        if not qualities:
            self.stats['quality_stats'] = {
                'mean_quality': 0,
                'median_quality': 0,
                'high_quality': 0,
                'medium_quality': 0,
                'low_quality': 0
            }
            return

        qualities.sort()
        n = len(qualities)

        high_quality = sum(1 for q in qualities if q >= 30)
        medium_quality = sum(1 for q in qualities if 20 <= q < 30)
        low_quality = sum(1 for q in qualities if q < 20)

        self.stats['quality_stats'] = {
            'mean_quality': sum(qualities) / n,
            'median_quality': qualities[n // 2],
            'high_quality': high_quality,
            'medium_quality': medium_quality,
            'low_quality': low_quality
        }

    def _calculate_depth_stats(self, depths: List[int]) -> None:
        """Calculate depth statistics"""
        if not depths:
            self.stats['depth_stats'] = {
                'mean_depth': 0,
                'median_depth': 0,
                'min_depth': 0,
                'max_depth': 0
            }
            return

        depths.sort()
        n = len(depths)

        self.stats['depth_stats'] = {
            'mean_depth': sum(depths) / n,
            'median_depth': depths[n // 2],
            'min_depth': min(depths),
            'max_depth': max(depths)
        }

    def _calculate_ts_tv_ratio(self) -> None:
        """Calculate transition/transversion ratio"""
        transitions = 0
        transversions = 0

        for var in self.variants:
            if var['type'] != 'SNP':
                continue

            ref = var['ref']
            alt = var['alt']

            # Transition: A↔G or C↔T
            if (ref == 'A' and alt == 'G') or (ref == 'G' and alt == 'A'):
                transitions += 1
            elif (ref == 'C' and alt == 'T') or (ref == 'T' and alt == 'C'):
                transitions += 1
            # Transversion: all other SNPs
            else:
                transversions += 1

        ts_tv = transitions / transversions if transversions > 0 else 0
        self.stats['ts_tv_ratio'] = ts_tv

    def get_statistics(self) -> Dict:
        """Return calculated statistics"""
        stats = dict(self.stats)
        # Convert defaultdict to regular dict for JSON serialization
        stats['variant_types'] = dict(stats['variant_types'])
        stats['chromosome_distribution'] = dict(stats['chromosome_distribution'])
        return stats


def main():
    parser = argparse.ArgumentParser(description='Parse VCF and extract statistics')
    parser.add_argument('--vcf', required=True, help='VCF file path')
    parser.add_argument('--output', default='variant_stats.json', help='Output JSON file')

    args = parser.parse_args()

    # Check file exists
    if not Path(args.vcf).exists():
        print(f"Error: VCF file not found: {args.vcf}")
        return 1

    # Parse VCF
    vcf_parser = VCFParser(args.vcf)
    stats = vcf_parser.parse_vcf()

    # Write output
    with open(args.output, 'w') as f:
        json.dump(stats, f, indent=2)

    print(f"✓ Statistics extracted: {args.output}")
    print(f"  Total variants: {stats['total_variants']:,}")
    print(f"  Passed filter: {stats['passed_filter']:,}")
    print(f"  Ts/Tv ratio: {stats.get('ts_tv_ratio', 0):.2f}")

    return 0


if __name__ == '__main__':
    exit(main())
