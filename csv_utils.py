
import os
import sys
import pandas as pd

# Pobiera wszystkie pliki CSV z danego katalogu
def get_csv_files(directory):
    return [os.path.join(directory, f) for f in os.listdir(directory) if f.endswith(".csv")]

# Wczytuje pojedynczy plik CSV jako DataFrame
def read_csv(filepath):
    return pd.read_csv(filepath)

# Czyści nazwy kolumn w DataFrame
def clean_column_names(df):
    df.columns = [col.strip().lower().replace(" ", "_") for col in df.columns]
    return df

# Interaktywny lub automatyczny wybór plików CSV
def interactive_choose_file(files):
    import __main__
    args = getattr(__main__, 'args', None)

    if args and getattr(args, 'auto', False) or not sys.stdin.isatty():
        print("🔁 Tryb automatyczny: przetwarzanie wszystkich plików.")
        return files

    print("\n=== Wybór pliku CSV do przetworzenia ===")
    for i, f in enumerate(files):
        print(f"  {i}: {os.path.basename(f)}")
    choice = input("Wybierz numer pliku (lub ENTER, aby przetworzyć wszystkie): ").strip()
    if not choice:
        return files
    try:
        idx = int(choice)
        return [files[idx]]
    except (ValueError, IndexError):
        print("Nieprawidłowy wybór. Przetwarzanie wszystkich plików.")
        return files
