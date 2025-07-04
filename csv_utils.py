import os
import pandas as pd
import re
from typing import Any, Dict, List

def discover_csv_files(directory: str) -> List[str]:
    """Return a list of CSV files found in *directory*."""
    return [
        os.path.join(directory, f)
        for f in os.listdir(directory)
        if f.endswith(".csv") and os.path.isfile(os.path.join(directory, f))
    ]

def interactive_choose_file(files: List[str]) -> List[str]:
    """Allow user to select one CSV file or process all."""
    print("\n=== Wybór pliku CSV do przetworzenia ===")
    for idx, path in enumerate(files):
        print(f"  {idx}: {os.path.basename(path)}")
    choice = input("Wybierz numer pliku (lub ENTER, aby przetworzyć wszystkie): ").strip()
    if choice.isdigit():
        idx = int(choice)
        if 0 <= idx < len(files):
            print(f"Wybrano: {os.path.basename(files[idx])}")
            return [files[idx]]
        print("Nieprawidłowy numer, zostaną przetworzone wszystkie pliki.")
    return files

def interactive_filter(df: pd.DataFrame) -> pd.DataFrame:
    """Interactively ask user for filtering conditions and apply them to df."""
    filtered_df = df
    print("\n=== Interaktywne filtrowanie danych ===")
    used_columns = set()
    while True:
        available_cols = [col for col in filtered_df.columns if col not in used_columns]
        if not available_cols:
            print("Wszystkie kolumny zostały już użyte do filtrowania.")
            break
        choice = input("Czy chcesz dodać warunek filtrowania? (y/n): ").strip().lower()
        if choice != 'y':
            break
        print("Dostępne kolumny do filtrowania:")
        for idx, col in enumerate(available_cols):
            print(f"  {idx}: {col} (typ: {filtered_df[col].dtype})")
        try:
            col_idx = int(input("Wybierz numer kolumny: ").strip())
            col = available_cols[col_idx]
        except (ValueError, IndexError):
            print("Nieprawidłowy numer kolumny, spróbuj ponownie.")
            continue
        used_columns.add(col)
        cond_str = input(
            f"Wprowadź warunek dla '{col}' (np. '> 20' lub '== Warsaw'): "
        ).strip()
        m = re.match(r'^(>=|<=|==|!=|>|<)\s*(.+)$', cond_str)
        if not m:
            print("Niepoprawny format, spróbuj ponownie.")
            continue
        op, val_raw = m.group(1), m.group(2)
        if filtered_df[col].dtype.kind in 'iuf':
            try:
                val: Any = float(val_raw)
            except ValueError:
                print("Nieprawidłowa wartość numeryczna, spróbuj ponownie.")
                continue
        else:
            val = val_raw
        expr = {
            '>': filtered_df[col] > val,
            '<': filtered_df[col] < val,
            '==': filtered_df[col] == val,
            '!=': filtered_df[col] != val,
            '>=': filtered_df[col] >= val,
            '<=': filtered_df[col] <= val
        }[op]
        filtered_df = filtered_df.loc[expr]
        print(f"Liczba wierszy po filtrze: {len(filtered_df)}")
    return filtered_df

def interactive_sort(df: pd.DataFrame) -> pd.DataFrame:
    """Interactively ask user which column to sort by and order."""
    print("\n=== Interaktywne sortowanie danych ===")
    for idx, col in enumerate(df.columns):
        print(f"  {idx}: {col}")
    choice = input("Wybierz numer kolumny do sortowania (ENTER aby pominąć): ").strip()
    if choice.isdigit():
        idx = int(choice)
        if 0 <= idx < len(df.columns):
            col = df.columns[idx]
            order = input("asc/desc [asc]: ").strip().lower() or 'asc'
            df = df.sort_values(by=col, ascending=(order=='asc'))
            print(f"Dane posortowane według '{col}' ({order})")
    return df

def process_csv_file(path: str, config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Read *path* with encoding fallback and return summary including filtering and sorting.
    Obsługuje polskie znaki i pliki z Excela (cp1250, iso-8859-2).
    """
    encodings: List[str] = []
    if config.get("encoding"):
        encodings.append(config["encoding"])
    # Najpierw najbardziej prawdopodobne, na końcu latin-1 (do łapania wyjątków)
    encodings += ["utf-8", "cp1250", "iso-8859-2", "latin2", "latin-1"]

    df = None
    for enc in encodings:
        try:
            df = pd.read_csv(path, encoding=enc)
            if enc != "utf-8":
                print(f"[INFO] Wczytano plik przy użyciu kodowania '{enc}'.")
            break
        except UnicodeDecodeError:
            print(f"[WARN] Kodowanie '{enc}' nie zadziałało, próbuję kolejnego.")
        except Exception as e:
            print(f"[WARN] Kodowanie '{enc}' nie zadziałało ({e}), próbuję kolejnego.")
    if df is None:
        raise UnicodeDecodeError(
            f"Nie udało się odczytać pliku {path} przy użyciu kodowań: {encodings}"
        )

    print(f"\nŁaduję plik: {os.path.basename(path)} | wiersze: {len(df)} | kolumny: {list(df.columns)}")
    if config.get("interactive_filter", True):
        df = interactive_filter(df)
    if config.get("interactive_sort", True):
        df = interactive_sort(df)

    summary: Dict[str, Any] = {
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

def interactive_choose_charts(df: pd.DataFrame) -> List[Dict[str, Any]]:
    """
    Simple interactive input with validation: user enters chart specs in one line, re-prompt on error.
    """
    cols = list(df.columns)
    print("\n=== Prosty wybór wykresów ===")
    for idx, col in enumerate(cols):
        print(f"  {idx}: {col} ({df[col].dtype})")

    prompt = (
        "Podaj wykresy w formacie 'bar:kolumna' lub 'line:kolumna1,kolumna2',\n"
        "oddzielone ';', np.: bar:department; line:date,revenue"
    )
    print(prompt)

    while True:
        spec = input("Wykresy (ENTER = brak): ").strip()
        if not spec:
            return []
        parts = [p.strip() for p in spec.split(';') if p.strip()]
        charts: List[Dict[str, Any]] = []
        valid = True

        for part in parts:
            if ':' not in part:
                print(f"Błędny format '{part}', brak ':' separatora.")
                valid = False
                break
            t, cols_str = part.split(':', 1)
            t = t.strip().lower()
            if t not in ('bar', 'line'):
                print(f"Nieznany typ '{t}', użyj 'bar' lub 'line'.")
                valid = False
                break
            cols_list = [c.strip() for c in cols_str.split(',')]

            if t == 'bar':
                if len(cols_list) != 1:
                    print(f"Bar wymaga jednej kolumny, '{part}' pomijam.")
                    valid = False
                    break
                c = cols_list[0]
                if c not in cols or df[c].dropna().empty:
                    print(f"Brak danych dla '{c}', wybierz inną.")
                    valid = False
                    break
                charts.append({'type': 'bar', 'columns': [c]})

            else:  # line
                if len(cols_list) != 2:
                    print(f"Line wymaga dwóch kolumn, '{part}' pomijam.")
                    valid = False
                    break
                x, y = cols_list
                if x not in cols or y not in cols or df[[x, y]].dropna().empty:
                    print(f"Nieprawidłowe lub puste kolumny '{x},{y}'.")
                    valid = False
                    break
                charts.append({'type': 'line', 'columns': [x, y]})

        if valid:
            return charts
        print("Proszę ponownie wprowadzić prawidłową specyfikację.")