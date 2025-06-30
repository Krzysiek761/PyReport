import os
import sys
from typing import Any, Dict, List

import matplotlib.pyplot as plt
import pandas as pd
import yaml
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
    summary = {
        "filename": path,
        "columns": df.columns.tolist(),
        "row_count": len(df),
        "column_types": df.dtypes.astype(str).to_dict(),
        "numerical_summary": {},
        "dataframe": df,
    }

    numerical_cols = df.select_dtypes(include=["number"]).columns
    for col in numerical_cols:
        summary["numerical_summary"][col] = {
            "sum": df[col].sum(),
            "mean": df[col].mean(),
            "min": df[col].min(),
            "max": df[col].max(),
        }

    if config.get("filter"):
        for condition in config["filter"]:
            col = condition["column"]
            op = condition["operator"]
            val = condition["value"]
            if op == ">":
                df = df[df[col] > val]
            elif op == "<":
                df = df[df[col] < val]
            elif op == "==":
                df = df[df[col] == val]
        summary["filtered"] = True
        summary["dataframe"] = df

    if config.get("sort_by"):
        df = df.sort_values(by=config["sort_by"])
        summary["dataframe"] = df

    return summary


def generate_charts(summary: Dict[str, Any], config: Dict[str, Any]) -> List[str]:
    """Create charts based on *summary* according to *config*."""
    df = summary["dataframe"]
    output_paths: List[str] = []
    chart_config = config.get("charts", [])
    output_dir = config.get("output_dir", "charts")
    os.makedirs(output_dir, exist_ok=True)

    for i, chart in enumerate(chart_config):
        chart_type = chart.get("type")
        columns = chart.get("columns", [])
        if chart_type == "bar" and len(columns) == 1:
            col = columns[0]
            plt.figure()
            df[col].value_counts().plot(kind="bar")
            path = os.path.join(output_dir, f"chart_{i}_{col}_bar.png")
            plt.savefig(path)
            output_paths.append(path)
            plt.close()
        elif chart_type == "line" and len(columns) == 2:
            x, y = columns
            plt.figure()
            df.plot(x=x, y=y, kind="line")
            path = os.path.join(output_dir, f"chart_{i}_{y}_line.png")
            plt.savefig(path)
            output_paths.append(path)
            plt.close()

    return output_paths


class PDFReport(FPDF):
    def header(self) -> None:  # pragma: no cover - simple wrapper
        self.set_font("Helvetica", "B", 16)
        self.cell(0, 10, "Raport danych CSV", ln=True, align="C")
        self.ln(10)

    def add_table(self, dataframe: pd.DataFrame) -> None:
        self.set_font("Helvetica", size=10)
        col_width = self.w / (len(dataframe.columns) + 1)
        for col in dataframe.columns:
            self.cell(col_width, 10, col, border=1)
        self.ln()
        for _, row in dataframe.iterrows():
            for item in row:
                self.cell(col_width, 10, str(item), border=1)
            self.ln()

    def add_images(self, chart_paths: List[str]) -> None:  # pragma: no cover
        for path in chart_paths:
            if os.path.exists(path):
                self.add_page()
                self.image(path, w=180)


def generate_pdf_report(
    filename: str,
    summary: Dict[str, Any],
    chart_paths: List[str],
    config: Dict[str, Any],
) -> str:
    """Generate a PDF report for *filename* and return the output path."""
    pdf = PDFReport()
    pdf.add_page()

    pdf.set_font("Helvetica", size=12)
    pdf.cell(0, 10, f"Plik: {os.path.basename(filename)}", ln=True)
    pdf.cell(0, 10, f"Wiersze: {summary['row_count']}", ln=True)

    pdf.ln(5)
    pdf.cell(0, 10, "Tabela danych:", ln=True)
    df = summary["dataframe"].head(20)
    pdf.add_table(df)

    pdf.add_images(chart_paths)

    output_dir = config.get("output_dir", "reports")
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(
        output_dir,
        f"report_{os.path.splitext(os.path.basename(filename))[0]}.pdf",
    )
    pdf.output(output_path)
    return output_path


def main() -> None:
    config_path = sys.argv[1] if len(sys.argv) > 1 else "config.yaml"
    config = load_config(config_path)
    input_dir = config.get("input_dir", "test_data")
    csv_files = discover_csv_files(input_dir)

    for csv_file in csv_files:
        summary = process_csv_file(csv_file, config)
        chart_source = summary.get("summary", summary)
        chart_paths = generate_charts(chart_source, config)
        generate_pdf_report(csv_file, summary, chart_paths, config)


if __name__ == "__main__":
    main()
