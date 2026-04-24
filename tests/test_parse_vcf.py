"""
Unit tests for ngs.parsers.vcf.VCFParser.

Uses only the Python standard library so the tests run without installing
pysam or other heavy bioinformatics dependencies.
"""

import gzip
import json
import os
import tempfile

import pytest

from ngs.parsers.vcf import VCFParser


# ── fixtures ──────────────────────────────────────────────────────────────────


@pytest.fixture()
def minimal_vcf(tmp_path):
    """Write a minimal 3-variant VCF file and return its path."""
    content = (
        "##fileformat=VCFv4.2\n"
        "##FILTER=<ID=PASS,Description=\"All filters passed\">\n"
        "#CHROM\tPOS\tID\tREF\tALT\tQUAL\tFILTER\tINFO\n"
        "chr1\t100\t.\tA\tG\t50.0\tPASS\tDP=30\n"   # SNP, high quality, PASS
        "chr1\t200\t.\tC\tT\t25.0\tPASS\tDP=20\n"   # SNP, medium quality, PASS
        "chr2\t300\t.\tAT\tA\t10.0\t.\tDP=5\n"      # DELETION, low quality, '.'
    )
    vcf_file = tmp_path / "test.vcf"
    vcf_file.write_text(content)
    return str(vcf_file)


@pytest.fixture()
def gzip_vcf(tmp_path, minimal_vcf):
    """Gzip-compressed copy of the minimal VCF."""
    gz_path = tmp_path / "test.vcf.gz"
    with open(minimal_vcf, "rb") as src, gzip.open(str(gz_path), "wb") as dst:
        dst.write(src.read())
    return str(gz_path)


# ── parse_vcf ─────────────────────────────────────────────────────────────────


def test_total_variants(minimal_vcf):
    stats = VCFParser(minimal_vcf).parse_vcf()
    assert stats["total_variants"] == 3


def test_passed_filter(minimal_vcf):
    stats = VCFParser(minimal_vcf).parse_vcf()
    # 2 PASS + 1 '.' both count as passed
    assert stats["passed_filter"] == 3


def test_variant_types(minimal_vcf):
    stats = VCFParser(minimal_vcf).parse_vcf()
    assert stats["variant_types"]["SNP"] == 2
    assert stats["variant_types"]["DELETION"] == 1


def test_chromosome_distribution(minimal_vcf):
    stats = VCFParser(minimal_vcf).parse_vcf()
    assert stats["chromosome_distribution"]["chr1"] == 2
    assert stats["chromosome_distribution"]["chr2"] == 1


def test_quality_stats_populated(minimal_vcf):
    stats = VCFParser(minimal_vcf).parse_vcf()
    qs = stats["quality_stats"]
    assert qs["high_quality"] == 1   # 50 >= 30
    assert qs["medium_quality"] == 1  # 25 in [20,30)
    assert qs["low_quality"] == 1    # 10 < 20
    assert round(qs["mean_quality"], 2) == round((50 + 25 + 10) / 3, 2)


def test_depth_stats_populated(minimal_vcf):
    stats = VCFParser(minimal_vcf).parse_vcf()
    ds = stats["depth_stats"]
    assert ds["min_depth"] == 5
    assert ds["max_depth"] == 30


def test_ts_tv_ratio(minimal_vcf):
    """Both SNPs are transitions (A>G, C>T), so Ts/Tv should be inf-guard (0)
    when there are no transversions, or 2 if transversions present."""
    stats = VCFParser(minimal_vcf).parse_vcf()
    # A→G and C→T are both transitions; 0 transversions → ratio = 0 (guard)
    assert stats["ts_tv_ratio"] == 0.0


def test_gzip_vcf(gzip_vcf):
    """Parser should handle gzip-compressed VCF files transparently."""
    stats = VCFParser(gzip_vcf).parse_vcf()
    assert stats["total_variants"] == 3


def test_missing_file_returns_empty():
    """A missing file should return an empty dict, not raise."""
    stats = VCFParser("/tmp/does_not_exist.vcf").parse_vcf()
    assert stats == {}


# ── _get_variant_type ─────────────────────────────────────────────────────────


def test_snp_classification():
    vp = VCFParser.__new__(VCFParser)
    assert vp._get_variant_type(["chr1", "1", ".", "A", "T", ".", ".", "."]) == "SNP"


def test_insertion_classification():
    vp = VCFParser.__new__(VCFParser)
    assert vp._get_variant_type(["chr1", "1", ".", "A", "AT", ".", ".", "."]) == "INSERTION"


def test_deletion_classification():
    vp = VCFParser.__new__(VCFParser)
    assert vp._get_variant_type(["chr1", "1", ".", "AT", "A", ".", ".", "."]) == "DELETION"


def test_mnv_classification():
    vp = VCFParser.__new__(VCFParser)
    assert vp._get_variant_type(["chr1", "1", ".", "AC", "TG", ".", ".", "."]) == "MNV"


def test_multi_allelic_classification():
    vp = VCFParser.__new__(VCFParser)
    assert vp._get_variant_type(["chr1", "1", ".", "A", "T,C", ".", ".", "."]) == "MULTI_ALLELIC"


# ── get_statistics (JSON serialisable) ────────────────────────────────────────


def test_statistics_json_serialisable(minimal_vcf):
    stats = VCFParser(minimal_vcf).parse_vcf()
    # Should not raise
    json.dumps(stats)
