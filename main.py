import argparse
from config import load_config
from csv_utils import (
    discover_csv_files,
    interactive_choose_file,
    process_csv_file,
    interactive_choose_charts,
)
from charts import generate_charts
from report import generate_pdf_report


def main():
    p = argparse.ArgumentParser("CSV to PDF report")
    p.add_argument("-c", "--config", default="config.yaml")
    p.add_argument("-i", "--input-dir")
    p.add_argument("--charts-dir")
    p.add_argument("--reports-dir")
    args = p.parse_args()

    cfg = load_config(args.config)
    if args.input_dir:
        cfg["input_dir"] = args.input_dir
    if args.charts_dir:
        cfg["charts_dir"] = args.charts_dir
    if args.reports_dir:
        cfg["reports_dir"] = args.reports_dir

    files = discover_csv_files(cfg.get("input_dir", "test_data"))
    if cfg.get("interactive_choose_file", True):
        files = interactive_choose_file(files)

    for f in files:
        print(f"\n=== Przetwarzanie: {f} ===")
        summary = process_csv_file(f, cfg)
        if cfg.get("interactive_charts", True):
            cfg["charts"] = interactive_choose_charts(summary["dataframe"])
        charts = generate_charts(summary, cfg)
        rpt = generate_pdf_report(summary, charts, cfg)
        print(f"Generated: {rpt}")


if __name__ == "__main__":
    main()
