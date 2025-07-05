import argparse
import os
from config import load_config
from csv_utils import (
    discover_csv_files,
    process_csv_file,
)
from charts import generate_charts
from report import generate_pdf_report

def main():
    p = argparse.ArgumentParser("CSV to PDF report")
    p.add_argument("-c", "--config", default="config.yaml", help="Plik konfiguracyjny YAML")
    args = p.parse_args()

    # Załaduj config
    config = load_config(args.config) if os.path.exists(args.config) else {}

    # Ustal pliki do przetworzenia
    files = []
    if "input_file" in config:
        files = [os.path.join(config.get("input_dir", "."), config["input_file"])]
    else:
        files = discover_csv_files(config.get("input_dir", "test_data"))
        # Jeśli tryb interaktywny, poprosi o wybór pliku (domyślnie w csv_utils.py)

    for f in files:
        print(f"\n=== Przetwarzanie: {f} ===")
        # process_csv_file rozpoznaje, czy ma działać interaktywnie, czy na podstawie configu
        summary = process_csv_file(f, config)

        # Automatyczny wybór wykresów lub interaktywny, zależnie od configu
        charts = []
        if "charts" in config:
            # charts.py obsłuży listę wykresów z configu (trzeba mieć odpowiednią obsługę)
            charts = generate_charts(summary, config)
        else:
            # domyślnie, jeśli nie ma wykresów w configu, obsługa interaktywna w csv_utils/charts.py
            charts = generate_charts(summary, config)

        rpt = generate_pdf_report(summary, charts, config)
        print(f"Generated: {rpt}")

if __name__ == "__main__":
    main()
