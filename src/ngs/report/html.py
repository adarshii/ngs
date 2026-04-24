#!/usr/bin/env python3
"""
ngs.report.html - HTML Report Generator

Generates publication-ready HTML reports from pipeline results.

Usage (CLI):
    ngs-report --stats <stats_json> --output <html_file>

Usage (library):
    from ngs.report.html import HTMLReportGenerator
    gen = HTMLReportGenerator(title="My Report")
    html = gen.generate_full_report(stats_data)
"""

import argparse
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional


def load_stats(stats_file: str) -> Dict:
    """Load statistics from a JSON file."""
    if stats_file.endswith(".json"):
        with open(stats_file, "r") as fh:
            return json.load(fh)
    return {}


class HTMLReportGenerator:
    """Generate an HTML report from NGS pipeline statistics."""

    def __init__(self, title: str = "NGS Pipeline Analysis Report"):
        self.title = title
        self.timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # ── CSS / HTML skeleton ────────────────────────────────────────────────────

    def generate_css(self) -> str:
        """Return inline CSS styles."""
        return """
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                line-height: 1.6; color: #333;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh; padding: 20px;
            }
            .container {
                max-width: 1200px; margin: 0 auto; background: white;
                padding: 40px; border-radius: 8px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.3);
            }
            header { border-bottom: 3px solid #667eea; padding-bottom: 20px; margin-bottom: 30px; }
            h1 { color: #667eea; font-size: 2.5em; margin-bottom: 10px; }
            h2 {
                color: #764ba2; font-size: 1.8em; margin-top: 30px; margin-bottom: 15px;
                border-left: 4px solid #667eea; padding-left: 15px;
            }
            h3 { color: #555; font-size: 1.2em; margin-top: 15px; margin-bottom: 10px; }
            .metadata {
                display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                gap: 15px; margin-top: 20px; padding: 20px;
                background: #f8f9fa; border-radius: 5px;
            }
            .meta-item {
                display: flex; justify-content: space-between;
                padding: 10px 15px; background: white; border-radius: 3px;
                box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            }
            .meta-label { font-weight: bold; color: #667eea; }
            section { margin: 30px 0; padding: 20px; background: #f8f9fa; border-radius: 5px; }
            table { width: 100%; border-collapse: collapse; margin: 15px 0; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }
            th { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 15px; text-align: left; }
            td { padding: 12px 15px; border-bottom: 1px solid #ddd; }
            tr:hover { background: #f0f0f0; }
            tr:nth-child(even) { background: #ffffff; }
            .stat-box { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin: 15px 0; }
            .stat-card {
                background: white; padding: 20px; border-radius: 5px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1); border-top: 4px solid #667eea;
            }
            .stat-value { font-size: 2em; font-weight: bold; color: #667eea; margin: 10px 0; }
            .stat-label { color: #666; font-size: 0.9em; text-transform: uppercase; }
            .stat-unit { color: #999; font-size: 0.8em; }
            .success { color: #28a745; }
            .warning { color: #ffc107; }
            .danger  { color: #dc3545; }
            footer { margin-top: 40px; padding-top: 20px; border-top: 1px solid #ddd; text-align: center; color: #999; font-size: 0.9em; }
        </style>
        """

    def generate_header(self) -> str:
        """Return the HTML header block."""
        return f"""
        <header>
            <h1>🧬 {self.title}</h1>
            <p style="color: #999;">Generated: {self.timestamp}</p>
        </header>
        """

    # ── report sections ────────────────────────────────────────────────────────

    def generate_summary(self, stats_data: Optional[Dict]) -> str:
        """Return the summary statistics section."""
        html = "<section><h2>📊 Summary Statistics</h2>"

        if stats_data:
            total = stats_data.get("total_variants", 0)
            passed = stats_data.get("passed_filter", 0)
            pass_rate = (100 * passed / total) if total > 0 else 0
            ts_tv = stats_data.get("ts_tv_ratio", 0)

            html += f"""
            <div class="stat-box">
                <div class="stat-card">
                    <div class="stat-label">Total Variants</div>
                    <div class="stat-value">{total:,}</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">Passed Filter</div>
                    <div class="stat-value">{passed:,}</div>
                    <div class="stat-unit">({pass_rate:.1f}%)</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">Ts/Tv Ratio</div>
                    <div class="stat-value">{ts_tv:.2f}</div>
                    <div class="stat-unit">Expected: 2.0–2.2</div>
                </div>
            </div>
            """

        html += "</section>"
        return html

    def generate_variant_types(self, stats_data: Optional[Dict]) -> str:
        """Return the variant-types table section."""
        html = "<section><h2>🔬 Variant Types</h2>"

        if stats_data and "variant_types" in stats_data:
            total = stats_data.get("total_variants", 1)
            html += "<table><thead><tr><th>Type</th><th>Count</th><th>Percentage</th></tr></thead><tbody>"

            for vtype, count in sorted(stats_data["variant_types"].items()):
                pct = 100 * count / total if total > 0 else 0
                html += f"<tr><td>{vtype}</td><td>{count:,}</td><td>{pct:.1f}%</td></tr>"

            html += "</tbody></table>"

        html += "</section>"
        return html

    def generate_quality_stats(self, stats_data: Optional[Dict]) -> str:
        """Return the quality-metrics section."""
        html = "<section><h2>📈 Quality Metrics</h2>"

        if stats_data and "quality_stats" in stats_data:
            qs = stats_data["quality_stats"]
            html += f"""
            <div class="stat-box">
                <div class="stat-card">
                    <div class="stat-label">Mean Quality Score</div>
                    <div class="stat-value">{qs.get('mean_quality', 0):.1f}</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">Median Quality Score</div>
                    <div class="stat-value">{qs.get('median_quality', 0):.1f}</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">High Quality (≥30)</div>
                    <div class="stat-value success">{qs.get('high_quality', 0):,}</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">Medium Quality (≥20)</div>
                    <div class="stat-value warning">{qs.get('medium_quality', 0):,}</div>
                </div>
            </div>
            """

        html += "</section>"
        return html

    def generate_depth_stats(self, stats_data: Optional[Dict]) -> str:
        """Return the sequencing-depth section."""
        html = "<section><h2>🔍 Sequencing Depth</h2>"

        if stats_data and "depth_stats" in stats_data:
            ds = stats_data["depth_stats"]
            html += f"""
            <div class="stat-box">
                <div class="stat-card">
                    <div class="stat-label">Mean Depth</div>
                    <div class="stat-value">{ds.get('mean_depth', 0):.1f}</div>
                    <div class="stat-unit">× coverage</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">Median Depth</div>
                    <div class="stat-value">{ds.get('median_depth', 0):.1f}</div>
                    <div class="stat-unit">× coverage</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">Min Depth</div>
                    <div class="stat-value">{ds.get('min_depth', 0):.1f}</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">Max Depth</div>
                    <div class="stat-value">{ds.get('max_depth', 0):.1f}</div>
                </div>
            </div>
            """

        html += "</section>"
        return html

    def generate_footer(self) -> str:
        """Return the HTML footer."""
        return """
        <footer>
            <p>🧬 NGS WGS Variant-Calling Pipeline</p>
            <p>GATK Best Practices • Snakemake Workflow • Reproducible Analysis</p>
            <p>See: <a href="https://github.com/adarshii/ngs">github.com/adarshii/ngs</a></p>
        </footer>
        """

    def generate_full_report(self, stats_data: Optional[Dict] = None) -> str:
        """Assemble and return the complete HTML report as a string."""
        html = (
            "<!DOCTYPE html>\n"
            '<html lang="en">\n'
            "<head>\n"
            '    <meta charset="UTF-8">\n'
            '    <meta name="viewport" content="width=device-width, initial-scale=1.0">\n'
            "    <title>NGS Pipeline Report</title>\n"
        )
        html += self.generate_css()
        html += "</head>\n<body>\n<div class=\"container\">\n"
        html += self.generate_header()
        html += self.generate_summary(stats_data)
        html += self.generate_variant_types(stats_data)
        html += self.generate_quality_stats(stats_data)
        html += self.generate_depth_stats(stats_data)
        html += self.generate_footer()
        html += "\n</div>\n</body>\n</html>\n"
        return html


def main() -> int:
    """CLI entry point."""
    parser = argparse.ArgumentParser(description="Generate HTML report from pipeline statistics")
    parser.add_argument("--stats", help="Statistics JSON file")
    parser.add_argument("--output", default="pipeline_report.html", help="Output HTML file")
    parser.add_argument("--title", default="NGS Pipeline Analysis Report", help="Report title")

    args = parser.parse_args()

    stats_data: Dict = {}
    if args.stats and Path(args.stats).exists():
        stats_data = load_stats(args.stats)

    generator = HTMLReportGenerator(title=args.title)
    html_content = generator.generate_full_report(stats_data)

    with open(args.output, "w") as fh:
        fh.write(html_content)

    print(f"✓ HTML report generated: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
