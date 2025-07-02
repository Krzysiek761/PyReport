import os
import pandas as pd
import re
from typing import Any, Dict, List

def discover_csv_files(directory: str) -> List[str]:
    return [
        os.path.join(directory, f)
        for f in os.listdir(directory)
        if f.endswith(".csv") and os.path.isfile(os.path.join(directory, f))
    ]

def interactive_choose_file(files: List[str]) -> List[str]:
    print("\n=== Wybór pliku CSV do przetworzenia ===")
    for idx, path in enumerate(files):
        print(f"  {idx}: {os.path.basename(path)}")
    choice = input("Wybierz numer pliku (lub ENTER, aby przetworzyć wszystkie): ").strip()
    if choice.isdigit():
        idx = int(choice)
        if 0 <= idx < len(files):
            print(f"Wybrano: {os.path.basename(files[idx])}")
            return [files[idx]]
        else:
            print("Nieprawidłowy numer, zostaną przetworzone wszystkie pliki.")
    return files

def interactive_filter(df: pd.DataFrame) -> pd.DataFrame:
    filtered_df = df
    print("\n=== Interaktywne filtrowanie danych ===")
    while True:
        kontynuuj = input("Czy chcesz dodać warunek filtrowania? (y/n): ").strip().lower()
        if kontynuuj != 'y':
            break
        print("Dostępne kolumny do filtrowania:")
        for idx, col in enumerate(df.columns):
            print(f"  {idx}: {col} (typ: {df[col].dtype})")
        try:
            col_idx = int(input("Wybierz numer kolumny: ").strip())
            col = df.columns[col_idx]
        except (ValueError, IndexError):
            print("Nieprawidłowy numer kolumny, spróbuj ponownie.")
            continue
        cond_str = input(f"Wprowadź warunek dla '{col}' (np. '> 20' lub '== Warsaw'): ").strip()
        match = re.match(r'^(>=|<=|==|!=|>|<)\s*(.+)$', cond_str)
        if not match:
            print("Niepoprawny format, spróbuj ponownie.")
            continue
        op, val_raw = match.group(1), match.group(2)
        if df[col].dtype.kind in 'iuf':
            try:
                val: Any = float(val_raw)
            except ValueError:
                print("Nieprawidłowa wartość numeryczna, spróbuj ponownie.")
                continue
        else:
            val = val_raw
        expr = {
            '>': df[col] > val,
            '<': df[col] < val,
            '==': df[col] == val,
            '!=': df[col] != val,
            '>=': df[col] >= val,
            '<=': df[col] <= val
        }.get(op)
        if expr is None:
            print("Nieobsługiwany operator.")
            continue
        filtered_df = filtered_df[expr]
        print(f"Liczba wierszy po filtrze: {len(filtered_df)}")
    return filtered_df

def interactive_sort(df: pd.DataFrame) -> pd.DataFrame:
    print("\n=== Interaktywne sortowanie danych ===")
    print("Dostępne kolumny do sortowania:")
    for idx, col in enumerate(df.columns):
        print(f"  {idx}: {col}")
    choice = input("Wybierz numer kolumny do sortowania (lub ENTER, aby pominąć): ").strip()
    if choice.isdigit():
        idx = int(choice)
        if 0 <= idx < len(df.columns):
            col = df.columns[idx]
            order = input("Kolejność: asc/desc [asc]: ").strip().lower() or 'asc'
            df = df.sort_values(by=col, ascending=(order == 'asc'))
    return df

def process_csv_file(path: str, config: Dict[str, Any]) -> Dict[str, Any]:
    df = pd.read_csv(path)
    print(f"\nŁaduję plik: {os.path.basename(path)} | wiersze: {len(df)}")
    if config.get("interactive_filter", True):
        df = interactive_filter(df)
    if config.get("interactive_sort", True):
        df = interactive_sort(df)
    summary = {
        "filename": path,
        "columns": df.columns.tolist(),
        "row_count": len(df),
        "column_types": df.dtypes.astype(str).to_dict(),
        "numerical_summary": {},
        "dataframe": df,
    }
    for col in df.select_dtypes(include=["number"]).columns:
        summary["numerical_summary"][col] = {
            "sum": df[col].sum(),
            "mean": df[col].mean(),
            "min": df[col].min(),
            "max": df[col].max(),
        }
    return summary
