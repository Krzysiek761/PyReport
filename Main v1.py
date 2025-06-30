#!/usr/bin/env python3
import os
import argparse
from typing import Any, Dict, List

import yaml
import pandas as pd
import matplotlib.pyplot as plt
from fpdf import FPDF


def load_config(path: str) -> Dict[str, Any]:
    """Load YAML configuration from *path*."""
    with open(path, "r", encoding="utf-8") as file:
        return yaml.safe_load(file) or {}


def discover_csv_files(directory: str) -> List[str]:
    """Return a list of CSV files found in *directory*."""
    return [
        os.path.join(directory, f)
        for f in os.listdir(directory)
        if f.endswith(".csv") and os.path.isfile(os.path.join(directory, f))
    ]


def process_csv_file(path: str, config: Dict[str, Any]) -> Dict[str, Any]:
    """Read *path* and return basic statistics and optionally filtered data."""
    df = pd.read_csv(path)
    summary: Dict[str, Any] = {
        "filename": path,
        "columns": df.columns.tolist(),
        "row_count": len(df),
        "column_types": df.dtypes.astype(str).to_dict(),
        "numerical_summary": {},
        "dataframe": df,
    }

    # Compute basic numerical summaries
    for col in df.select_dtypes(include=["number"]).columns:
        summary["numerical_summary"][col] = {
            "sum": df[col].sum(),
            "mean": df[col].mean(),
            "min": df[col].min(),
            "max": df[col].max(),
        }

    # Optional filtering
    if config.get("filter"):
        filtered_df = df
        for condition in config["filter"]:
            col = condition["column"]
            op = condition["operator"]
            val = condition["value"]
            if op == ">":
                filtered_df = filtered_df[filtered_df[col] > val]
            elif op == "<":
                filtered_df = filtered_df[filtered_df[col] < val]
            elif op == "==":
                filtered_df = filtered_df[filtered_df[col] == val]
        summary["filtered"] = True
        summary["dataframe"] = filtered_df

    # Optional sorting
    if config.get("sort_by"):
        sorted_df = summary["dataframe"].sort_values(by=config["sort_by"])
        summary["dataframe"] = sorted_df

    return summary


def generate_charts(summary: Dict[str, Any], config: Dict[str, Any]) -> List[str]:
    """Create charts based on *summary* according to *config*."""
    df = summary["dataframe"]
    output_paths: List[str] = []
    chart_config = config.get("charts", [])
    charts_dir = config.get("charts_dir", "charts")
    os.makedirs(charts_dir, exist_ok=True)

    for i, chart in enumerate(chart_config):
        chart_type = chart.get("type")
        cols = chart.get("columns", [])

        if chart_type == "bar" and len(cols) == 1:
            col = cols[0]
            # Skip if no data
            if df[col].dropna().empty:
                print(f"[WARN] No data for bar chart on column '{col}', skipping.")
                continue

            plt.figure()
            df[col].value_counts().plot(kind="bar")
            path = os.path.join(charts_dir, f"chart_{i}_{col}_bar.png")
            plt.savefig(path)
            plt.close()
            output_paths.append(path)

        elif chart_type == "line" and len(cols) == 2:
            x, y = cols
            # Skip if no data
            if df[[x, y]].dropna().empty:
                print(f"[WARN] No data for line chart on columns '{x}', '{y}', skipping.")
                continue

            plt.figure()
            df.plot(x=x, y=y, kind="line")
            path = os.path.join(charts_dir, f"chart_{i}_{y}_line.png")
            plt.savefig(path)
            plt.close()
            output_paths.append(path)

    return output_paths


class PDFReport(FPDF):
    def header(self) -> None:
        self.set_font("Helvetica", "B", 16)
        self.cell(0, 10, "Raport danych CSV", ln=True, align="C")
        self.ln(10)

    def add_table(self, dataframe: pd.DataFrame) -> None:
        self.set_font("Helvetica", size=10)
        col_width = self.w / (len(dataframe.columns) + 1)
        # Header
        for col in dataframe.columns:
            self.cell(col_width, 10, str(col), border=1)
        self.ln()
        # Rows
        for _, row in dataframe.iterrows():
            for item in row:
                self.cell(col_width, 10, str(item), border=1)
            self.ln()

    def add_images(self, chart_paths: List[str]) -> None:
        for path in chart_paths:
            if os.path.exists(path):
                self.add_page()
                self.image(path, w=180)


def generate_pdf_report(
    summary: Dict[str, Any], chart_paths: List[str], config: Dict[str, Any]
) -> str:
    """Generate a PDF report and return the output path."""
    pdf = PDFReport()
    pdf.add_page()

    pdf.set_font("Helvetica", size=12)
    pdf.cell(0, 10, f"Plik: {os.path.basename(summary['filename'])}", ln=True)
    pdf.cell(0, 10, f"Wiersze: {summary['row_count']}", ln=True)

    pdf.ln(5)
    pdf.cell(0, 10, "Tabela danych (pierwsze 20 wierszy):", ln=True)
    pdf.add_table(summary['dataframe'].head(20))

    pdf.add_images(chart_paths)

    reports_dir = config.get("reports_dir", "reports")
    os.makedirs(reports_dir, exist_ok=True)
    output_path = os.path.join(
        reports_dir,
        f"report_{os.path.splitext(os.path.basename(summary['filename']))[0]}.pdf",
    )
    pdf.output(output_path)
    return output_path


def main() -> None:
    parser = argparse.ArgumentParser(
        description="CSV to PDF report generator"
    )
    parser.add_argument(
        "-c", "--config", default="config.yaml",
        help="Path to YAML configuration file"
    )
    parser.add_argument(
        "-i", "--input-dir",
        help="Override input directory for CSV files"
    )
    parser.add_argument(
        "--charts-dir",
        help="Override directory to save generated charts"
    )
    parser.add_argument(
        "--reports-dir",
        help="Override directory to save generated PDF reports"
    )
    args = parser.parse_args()

    config = load_config(args.config)
    if args.input_dir:
        config['input_dir'] = args.input_dir
    if args.charts_dir:
        config['charts_dir'] = args.charts_dir
    if args.reports_dir:
        config['reports_dir'] = args.reports_dir

    input_dir = config.get("input_dir", "test_data")
    csv_files = discover_csv_files(input_dir)

    for csv_file in csv_files:
        summary = process_csv_file(csv_file, config)
        chart_paths = generate_charts(summary, config)
        output_pdf = generate_pdf_report(summary, chart_paths, config)
        print(f"Generated report: {output_pdf}")


if __name__ == "__main__":
    main()
