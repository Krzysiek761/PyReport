
import os
import argparse
from config import load_config
from csv_utils import get_csv_files, read_csv, clean_column_names
from report import generate_pdf_report
from charts import generate_charts

def main():
    parser = argparse.ArgumentParser(description="Automatyczny generator PDF z plików CSV")
    parser.add_argument("--config", type=str, default="config.yaml", help="Ścieżka do pliku konfiguracyjnego")
    args = parser.parse_args()

    cfg = load_config(args.config)

    input_dir = cfg.get("input_dir", "test_data")
    csv_files = get_csv_files(input_dir)
    print(f"🔍 Znaleziono {len(csv_files)} plików CSV.")

    selected_files = csv_files
    print("🔁 Przetwarzanie wszystkich plików CSV w trybie automatycznym...")

    for file_path in selected_files:
        print(f"📄 Przetwarzanie: {os.path.basename(file_path)}")
        df = read_csv(file_path)
        df = clean_column_names(df)

        summary = {
            "filename": file_path,
            "row_count": len(df),
            "dataframe": df
        }

        charts = generate_charts(summary, cfg)
        generate_pdf_report(summary, charts, cfg)

    print("✅ Gotowe – wszystkie raporty zostały wygenerowane.")

if __name__ == "__main__":
    main()
