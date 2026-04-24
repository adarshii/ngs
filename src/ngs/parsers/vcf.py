#!/usr/bin/env python3
"""
ngs.parsers.vcf - VCF Parser and Statistics Extractor

Parses VCF files and extracts comprehensive variant statistics.

Usage (CLI):
    ngs-parse-vcf --vcf <vcf_file> --output <output_json>

Usage (library):
    from ngs.parsers.vcf import VCFParser
    parser = VCFParser("variants.vcf.gz")
    stats = parser.parse_vcf()
"""

import argparse
import gzip
import json
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Optional


class VCFParser:
    """Parse VCF files and extract variant statistics."""

    def __init__(self, vcf_file: str):
        self.vcf_file = vcf_file
        self.variants: List[Dict] = []
        self.stats: Dict = {
            "total_variants": 0,
            "passed_filter": 0,
            "variant_types": defaultdict(int),
            "quality_stats": {},
            "depth_stats": {},
            "chromosome_distribution": defaultdict(int),
        }

    def open_vcf(self):
        """Open VCF file (handles gzip compression)."""
        if self.vcf_file.endswith(".gz"):
            return gzip.open(self.vcf_file, "rt")
        return open(self.vcf_file, "r")

    def parse_vcf(self) -> Dict:
        """Parse VCF file and compute summary statistics."""
        qualities: List[float] = []
        depths: List[int] = []

        try:
            with self.open_vcf() as fh:
                for line in fh:
                    if line.startswith("#"):
                        continue

                    fields = line.strip().split("\t")
                    if len(fields) < 8:
                        continue

                    chrom = fields[0]
                    qual = fields[5]
                    info = fields[7]
                    filter_status = fields[6]

                    try:
                        qual_score = float(qual) if qual != "." else 0.0
                        qualities.append(qual_score)
                    except ValueError:
                        qual_score = 0.0

                    depth = self._extract_depth(info)
                    if depth is not None:
                        depths.append(depth)

                    var_type = self._get_variant_type(fields)

                    self.stats["total_variants"] += 1
                    self.stats["chromosome_distribution"][chrom] += 1
                    self.stats["variant_types"][var_type] += 1

                    if filter_status in ("PASS", "."):
                        self.stats["passed_filter"] += 1

                    self.variants.append(
                        {
                            "chrom": chrom,
                            "pos": int(fields[1]),
                            "ref": fields[3],
                            "alt": fields[4],
                            "qual": qual_score,
                            "depth": depth,
                            "type": var_type,
                            "filter": filter_status,
                        }
                    )

            self._calculate_quality_stats(qualities)
            self._calculate_depth_stats(depths)
            self._calculate_ts_tv_ratio()

            return self.get_statistics()

        except Exception as exc:
            print(f"Error parsing VCF: {exc}")
            return {}

    # ── private helpers ────────────────────────────────────────────────────────

    def _extract_depth(self, info: str) -> Optional[int]:
        """Extract DP (depth) from INFO field."""
        for field in info.split(";"):
            if field.startswith("DP="):
                try:
                    return int(field.split("=")[1])
                except (ValueError, IndexError):
                    return None
        return None

    def _get_variant_type(self, fields: List[str]) -> str:
        """Classify variant as SNP, INDEL, MNV, or MULTI_ALLELIC."""
        ref = fields[3]
        alt = fields[4]

        if "," in alt:
            return "MULTI_ALLELIC"

        if len(ref) == 1 and len(alt) == 1:
            return "SNP"
        if len(ref) > len(alt):
            return "DELETION"
        if len(ref) < len(alt):
            return "INSERTION"
        return "MNV"

    def _calculate_quality_stats(self, qualities: List[float]) -> None:
        """Compute quality score summary statistics."""
        if not qualities:
            self.stats["quality_stats"] = {
                "mean_quality": 0,
                "median_quality": 0,
                "high_quality": 0,
                "medium_quality": 0,
                "low_quality": 0,
            }
            return

        sorted_q = sorted(qualities)
        n = len(sorted_q)

        self.stats["quality_stats"] = {
            "mean_quality": sum(sorted_q) / n,
            "median_quality": sorted_q[n // 2],
            "high_quality": sum(1 for q in sorted_q if q >= 30),
            "medium_quality": sum(1 for q in sorted_q if 20 <= q < 30),
            "low_quality": sum(1 for q in sorted_q if q < 20),
        }

    def _calculate_depth_stats(self, depths: List[int]) -> None:
        """Compute sequencing depth summary statistics."""
        if not depths:
            self.stats["depth_stats"] = {
                "mean_depth": 0,
                "median_depth": 0,
                "min_depth": 0,
                "max_depth": 0,
            }
            return

        sorted_d = sorted(depths)
        n = len(sorted_d)

        self.stats["depth_stats"] = {
            "mean_depth": sum(sorted_d) / n,
            "median_depth": sorted_d[n // 2],
            "min_depth": sorted_d[0],
            "max_depth": sorted_d[-1],
        }

    def _calculate_ts_tv_ratio(self) -> None:
        """Calculate the transition / transversion ratio for SNPs."""
        transitions = 0
        transversions = 0

        for var in self.variants:
            if var["type"] != "SNP":
                continue
            ref, alt = var["ref"], var["alt"]
            if {ref, alt} in ({"A", "G"}, {"C", "T"}):
                transitions += 1
            else:
                transversions += 1

        self.stats["ts_tv_ratio"] = transitions / transversions if transversions > 0 else 0.0

    def get_statistics(self) -> Dict:
        """Return a JSON-serialisable statistics dictionary."""
        stats = dict(self.stats)
        stats["variant_types"] = dict(stats["variant_types"])
        stats["chromosome_distribution"] = dict(stats["chromosome_distribution"])
        return stats


def main() -> int:
    """CLI entry point."""
    parser = argparse.ArgumentParser(description="Parse VCF and extract statistics")
    parser.add_argument("--vcf", required=True, help="Input VCF file path")
    parser.add_argument("--output", default="variant_stats.json", help="Output JSON file")

    args = parser.parse_args()

    if not Path(args.vcf).exists():
        print(f"Error: VCF file not found: {args.vcf}")
        return 1

    vcf_parser = VCFParser(args.vcf)
    stats = vcf_parser.parse_vcf()

    with open(args.output, "w") as fh:
        json.dump(stats, fh, indent=2)

    print(f"✓ Statistics extracted: {args.output}")
    print(f"  Total variants: {stats.get('total_variants', 0):,}")
    print(f"  Passed filter:  {stats.get('passed_filter', 0):,}")
    print(f"  Ts/Tv ratio:    {stats.get('ts_tv_ratio', 0):.2f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
