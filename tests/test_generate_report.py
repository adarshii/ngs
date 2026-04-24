"""
Unit tests for ngs.report.html.HTMLReportGenerator and load_stats.
"""

import json
import tempfile
from pathlib import Path

import pytest

from ngs.report.html import HTMLReportGenerator, load_stats


# ── fixtures ──────────────────────────────────────────────────────────────────


@pytest.fixture()
def sample_stats():
    return {
        "total_variants": 1000,
        "passed_filter": 850,
        "ts_tv_ratio": 2.1,
        "variant_types": {"SNP": 800, "INSERTION": 100, "DELETION": 100},
        "quality_stats": {
            "mean_quality": 45.0,
            "median_quality": 48.0,
            "high_quality": 750,
            "medium_quality": 100,
            "low_quality": 150,
        },
        "depth_stats": {
            "mean_depth": 35.0,
            "median_depth": 33.0,
            "min_depth": 10,
            "max_depth": 120,
        },
        "chromosome_distribution": {"chr1": 500, "chr2": 500},
    }


@pytest.fixture()
def stats_json_file(tmp_path, sample_stats):
    """Write sample_stats to a JSON file and return the path string."""
    p = tmp_path / "stats.json"
    p.write_text(json.dumps(sample_stats))
    return str(p)


@pytest.fixture()
def generator():
    return HTMLReportGenerator(title="Test Report")


# ── load_stats ────────────────────────────────────────────────────────────────


def test_load_stats_json(stats_json_file, sample_stats):
    loaded = load_stats(stats_json_file)
    assert loaded["total_variants"] == sample_stats["total_variants"]


def test_load_stats_non_json_returns_empty(tmp_path):
    txt_file = tmp_path / "stats.txt"
    txt_file.write_text("not json")
    result = load_stats(str(txt_file))
    assert result == {}


# ── HTMLReportGenerator ───────────────────────────────────────────────────────


def test_generate_full_report_contains_doctype(generator, sample_stats):
    html = generator.generate_full_report(sample_stats)
    assert "<!DOCTYPE html>" in html


def test_report_title_in_html(generator, sample_stats):
    html = generator.generate_full_report(sample_stats)
    assert "Test Report" in html


def test_report_total_variants(generator, sample_stats):
    html = generator.generate_full_report(sample_stats)
    assert "1,000" in html  # formatted with comma


def test_report_ts_tv_ratio(generator, sample_stats):
    html = generator.generate_full_report(sample_stats)
    assert "2.10" in html


def test_report_variant_types_listed(generator, sample_stats):
    html = generator.generate_full_report(sample_stats)
    assert "SNP" in html
    assert "INSERTION" in html
    assert "DELETION" in html


def test_report_no_stats(generator):
    """Report generation should not crash when stats_data is empty."""
    html = generator.generate_full_report({})
    assert "<!DOCTYPE html>" in html


def test_report_none_stats(generator):
    """Report generation should not crash when stats_data is None."""
    html = generator.generate_full_report(None)
    assert "<!DOCTYPE html>" in html


def test_report_written_to_file(generator, sample_stats, tmp_path):
    """main() helper: generator writes valid HTML to disk."""
    out = tmp_path / "report.html"
    html = generator.generate_full_report(sample_stats)
    out.write_text(html)
    content = out.read_text()
    assert "<html" in content
    assert "</html>" in content
