
import os
import argparse
from config import load_config
from csv_utils import get_csv_files, read_csv, clean_column_names, interactive_choose_file
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

    # Tryb automatyczny – zawsze wszystkie pliki
    selected_files = csv_files
    print("🔁 Przetwarzanie wszystkich plików CSV w trybie automatycznym...")

    for file_path in selected_files:
        print(f"📄 Przetwarzanie: {os.path.basename(file_path)}")
        df = read_csv(file_path)
        df = clean_column_names(df)

        charts_dir = cfg.get("charts_dir", "charts")
        charts = generate_charts(df, charts_dir)

        reports_dir = cfg.get("reports_dir", "reports")
        generate_pdf_report(df, charts, file_path, reports_dir)

    print("✅ Gotowe – wszystkie raporty zostały wygenerowane.")

if __name__ == "__main__":
    main()
