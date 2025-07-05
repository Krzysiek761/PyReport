import os
import pandas as pd
import re
from typing import Any, Dict, List

def discover_csv_files(directory: str) -> List[str]:
    """Zwraca listę plików CSV w katalogu."""
    return [
        os.path.join(directory, f)
        for f in os.listdir(directory)
        if f.endswith(".csv") and os.path.isfile(os.path.join(directory, f))
    ]

def interactive_choose_file(files: List[str]) -> List[str]:
    """Pozwala wybrać jeden plik CSV albo przetworzyć wszystkie."""
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
    """Interaktywnie pozwala użytkownikowi filtrować dane."""
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
            f"Wprowadź warunek dla '{col}' (np. '> 20' lub '== Warszawa'): "
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
    """Interaktywnie pozwala sortować dane według wybranej kolumny."""
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
    Wczytuje plik z obsługą różnych kodowań i zwraca podsumowanie oraz DataFrame.
    """
    encodings: List[str] = []
    if config.get("encoding"):
        encodings.append(config["encoding"])
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
    Idiotoodporny kreator wykresów: pozwala wybrać tylko sensowne kolumny.
    """
    charts: List[Dict[str, Any]] = []
    print("\n=== Interaktywny wybór wykresów ===")

    # Sensowne kolumny dla wykresu słupkowego: kategoryczne o małej liczbie wartości
    bar_candidates = [c for c in df.columns if df[c].dtype == "object" and df[c].nunique() <= 30]
    # Sensowne kolumny na X do wykresu liniowego: liczby, daty, ewentualnie krótkie kategorie
    line_x_candidates = [
        c for c in df.columns if pd.api.types.is_numeric_dtype(df[c])
        or pd.api.types.is_datetime64_any_dtype(df[c])
        or (df[c].dtype == "object" and df[c].nunique() <= 20)
    ]
    # Sensowne kolumny na Y do wykresu liniowego: liczby!
    line_y_candidates = [c for c in df.columns if pd.api.types.is_numeric_dtype(df[c])]

    if not bar_candidates and not line_y_candidates:
        print("Brak kolumn, które można zobrazować wykresem.")
        return []

    while True:
        ile_str = input("Ile wykresów chcesz wygenerować? [0=żaden]: ").strip()
        if ile_str == '':
            ile = 0
            break
        try:
            ile = int(ile_str)
            if ile < 0:
                raise ValueError
            break
        except ValueError:
            print("Podaj liczbę wykresów lub ENTER.")
    if ile == 0:
        return charts

    for nr in range(1, ile+1):
        print(f"\n=== Definiujesz wykres #{nr} ===")
        typ = ""
        while typ not in ("bar", "line"):
            typ = input("Wybierz typ wykresu ('bar' = słupkowy, 'line' = liniowy): ").strip().lower()
            if typ not in ("bar", "line"):
                print("Do wyboru jest tylko: 'bar' (słupkowy) lub 'line' (liniowy)!")
        if typ == "bar":
            if not bar_candidates:
                print("Brak kolumn kategorycznych do wykresu słupkowego.")
                continue
            print("Dostępne kolumny do wykresu słupkowego:")
            for idx, col in enumerate(bar_candidates):
                print(f"  {idx}: {col} (unikalne: {df[col].nunique()})")
            try:
                idx = int(input("Numer kolumny: "))
                c = bar_candidates[idx]
            except (ValueError, IndexError):
                print("Nieprawidłowy numer. Wykres zostanie pominięty.")
                continue
            charts.append({"type": "bar", "columns": [c]})
        elif typ == "line":
            if not line_x_candidates or not line_y_candidates:
                print("Brak odpowiednich kolumn do wykresu liniowego.")
                continue
            print("Dostępne kolumny na oś X (pozioma):")
            for idx, col in enumerate(line_x_candidates):
                print(f"  {idx}: {col} (typ: {df[col].dtype}, unikalnych: {df[col].nunique()})")
            try:
                x_idx = int(input("Numer kolumny X: "))
                x = line_x_candidates[x_idx]
            except (ValueError, IndexError):
                print("Nieprawidłowy numer. Wykres zostanie pominięty.")
                continue
            print("Dostępne kolumny na oś Y (pionowa, tylko liczby):")
            for idx, col in enumerate(line_y_candidates):
                print(f"  {idx}: {col} (typ: {df[col].dtype})")
            try:
                y_idx = int(input("Numer kolumny Y: "))
                y = line_y_candidates[y_idx]
            except (ValueError, IndexError):
                print("Nieprawidłowy numer. Wykres zostanie pominięty.")
                continue
            charts.append({"type": "line", "columns": [x, y]})
    return charts
