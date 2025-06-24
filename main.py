import sys
from utils import load_config, discover_csv_files
from processor import process_csv_file
from visualizer import generate_charts
from reporter import generate_pdf_report

def main():
    config_path = sys.argv[1] if len(sys.argv) > 1 else "config.yaml"
    config = load_config(config_path)
    csv_files = discover_csv_files(config.get("input_dir", "data"))

    for file_path in csv_files:
        summary = process_csv_file(file_path, config)
        charts = generate_charts(summary, config)
        generate_pdf_report(file_path, summary, charts, config)

if __name__ == "__main__":
    main()
