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
    p.add_argument(
        "-c", "--config", default="config.yaml", help="Plik konfiguracyjny YAML"
    )
    args = p.parse_args()

    # Sprawdź, czy config istnieje i go wczytaj
    config = load_config(args.config) if os.path.exists(args.config) else {}

    # Przygotuj listę plików do przetworzenia
    files = []

    if config:
        # Tryb automatyczny (config)
        if "input_file" in config:
            files = [os.path.join(config.get("input_dir", "."), config["input_file"])]
        else:
            files = discover_csv_files(config.get("input_dir", "test_data"))
    else:
        # Tryb interaktywny
        files = discover_csv_files("test_data")
        if not files:
            print("Brak plików CSV w katalogu test_data/")
            return
        print("\nDostępne pliki CSV:")
        for i, f in enumerate(files):
            print(f"  {i}: {f}")
        try:
            choice = int(input("Podaj numer pliku do przetworzenia: "))
            if choice < 0 or choice >= len(files):
                print("Niepoprawny numer pliku, przerywam.")
                return
            files = [files[choice]]
        except Exception:
            print("Niepoprawny wybór, przerywam.")
            return

    # Przetwarzanie wybranego pliku/pliku z configa
    for f in files:
        print(f"\n=== Przetwarzanie: {f} ===")
        summary = process_csv_file(f, config)

        # Generowanie wykresów: automatycznie jeśli są zdefiniowane, interaktywnie jeśli nie
        charts = generate_charts(summary, config)
        rpt = generate_pdf_report(summary, charts, config)
        print(f"Generated: {rpt}")


if __name__ == "__main__":
    main()
