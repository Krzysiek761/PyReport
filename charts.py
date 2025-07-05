import os
import matplotlib.pyplot as plt
from typing import Any, Dict, List
import pandas as pd


def generate_special_pie_chart(
    df: pd.DataFrame, column: str, values: List[str], charts_dir: str
) -> str:
    """
    Generuje wykres udziału wybranych wartości na tle wszystkich (pie chart z grupą "Inne")
    """
    wybrane_counts = [(df[column] == v).sum() for v in values]
    inne = len(df) - sum(wybrane_counts)
    labels = list(values) + ["Inne"]
    sizes = wybrane_counts + [inne]
    plt.figure()
    plt.pie(sizes, labels=labels, autopct="%1.1f%%")
    plt.title(f"Udział wybranych wartości z kolumny '{column}' na tle całości")
    path = os.path.join(charts_dir, f"chart_udzial_{column}.png")
    plt.savefig(path)
    plt.close()
    print(f"[AUTO] Wygenerowano wykres udziału: {path}")
    return path


def generate_charts(summary: Dict[str, Any], config: Dict[str, Any]) -> List[str]:
    df = summary["dataframe"]
    paths: List[str] = []
    charts_dir = config.get("charts_dir", "charts")
    os.makedirs(charts_dir, exist_ok=True)

    # AUTOMATYCZNE GENEROWANIE WYKRESÓW Z CONFIG
    if config and "charts" in config and not config.get("interactive_charts", True):
        for i, chart in enumerate(config["charts"]):
            t = chart.get("type")
            if t == "pie_special":
                # Nowość: specjalny wykres udziału (pie_special)
                col = chart.get("column")
                values = chart.get("values")
                if col and values and col in df.columns:
                    try:
                        pie_path = generate_special_pie_chart(
                            df, col, values, charts_dir
                        )
                        if pie_path:
                            paths.append(pie_path)
                    except Exception as e:
                        print("[AUTO][WARN] Błąd przy generowaniu wykresu udziału:", e)
                else:
                    print("[AUTO][WARN] Nieprawidłowa konfiguracja pie_special.")
            elif t == "bar" and "columns" in chart and len(chart["columns"]) == 1:
                c = chart["columns"][0]
                if c in df.columns:
                    try:
                        plt.figure()
                        df[c].value_counts().plot(kind="bar")
                        plt.title(f"Wykres słupkowy: {c}")
                        p = os.path.join(charts_dir, f"chart_{i}_{c}_bar.png")
                        plt.savefig(p)
                        plt.close()
                        paths.append(p)
                        print(f"[AUTO] Wygenerowano wykres słupkowy: {p}")
                    except Exception as e:
                        print("[AUTO][WARN] Błąd przy generowaniu bar:", e)
                else:
                    print(f"[AUTO][WARN] Kolumna '{c}' nie istnieje w danych.")
            elif t == "line" and "columns" in chart and len(chart["columns"]) == 2:
                x, y = chart["columns"]
                if x in df.columns and y in df.columns:
                    try:
                        plt.figure()
                        df.plot(x=x, y=y, kind="line")
                        plt.title(f"Wykres liniowy: {y} wg {x}")
                        p = os.path.join(charts_dir, f"chart_{i}_{y}_line.png")
                        plt.savefig(p)
                        plt.close()
                        paths.append(p)
                        print(f"[AUTO] Wygenerowano wykres liniowy: {p}")
                    except Exception as e:
                        print("[AUTO][WARN] Błąd przy generowaniu line:", e)
                else:
                    print(f"[AUTO][WARN] Kolumna '{x}' lub '{y}' nie istnieje.")
            elif t == "pie" and "columns" in chart and len(chart["columns"]) == 1:
                c = chart["columns"][0]
                if c in df.columns:
                    try:
                        plt.figure()
                        df[c].value_counts().plot(kind="pie", autopct="%1.1f%%")
                        plt.title(f"Wykres kołowy: {c}")
                        p = os.path.join(charts_dir, f"chart_{i}_{c}_pie.png")
                        plt.savefig(p)
                        plt.close()
                        paths.append(p)
                        print(f"[AUTO] Wygenerowano wykres kołowy: {p}")
                    except Exception as e:
                        print("[AUTO][WARN] Błąd przy generowaniu pie:", e)
                else:
                    print(f"[AUTO][WARN] Kolumna '{c}' nie istnieje.")
            else:
                print("[AUTO][WARN] Nieobsługiwany lub błędny typ wykresu.")
        return paths

    # === TRYB INTERAKTYWNY ===
    print("\n=== Interaktywne generowanie wykresów ===")
    # 1. Specjalny wykres udziału
    while True:
        try:
            print(
                "Czy chcesz utworzyć specjalny wykres udziału wybranych wartości na tle wszystkich? (y/n)"
            )
            resp = input().strip().lower()
            if resp != "y":
                break
            print("Dostępne kolumny:")
            for i, col in enumerate(df.columns):
                print(f"  {i}: {col} (typ: {df[col].dtype})")
            idx_cat = int(
                input(
                    "Podaj numer kolumny, z której wybierzesz wartości (np. miasto): "
                )
            )
            if idx_cat < 0 or idx_cat >= len(df.columns):
                print("Niepoprawny numer kolumny.")
                continue
            col_cat = df.columns[idx_cat]
            unique_vals = sorted(df[col_cat].dropna().unique())
            if not unique_vals:
                print("Brak unikalnych wartości w tej kolumnie.")
                continue
            print("Dostępne wartości (np. miasta):")
            for i, val in enumerate(unique_vals):
                print(f"  {i}: {val}")
            idxs = input(
                "Podaj numery wybranych wartości oddzielone przecinkiem (np. 0,2,5): "
            )
            idxs = [
                int(i)
                for i in idxs.split(",")
                if i.strip().isdigit() and int(i) < len(unique_vals)
            ]
            if not idxs:
                print("Nie wybrano wartości.")
                continue
            wybrane = [unique_vals[i] for i in idxs]
            chart_path = generate_special_pie_chart(df, col_cat, wybrane, charts_dir)
            paths.append(chart_path)
            break  # domyślnie 1 raz, jeśli chcesz możliwość kilku, usuń break
        except Exception as e:
            print("Błąd podczas generowania specjalnego wykresu:", e)

    # 2. Standardowe wykresy bar/line/pie
    while True:
        try:
            print("\nTypy wykresów: bar, line, pie")
            chart_type = (
                input("Podaj typ wykresu (ENTER aby zakończyć): ").strip().lower()
            )
            if chart_type == "":
                break
            print("Dostępne kolumny:")
            for i, col in enumerate(df.columns):
                print(f"  {i}: {col} (typ: {df[col].dtype})")
            if chart_type == "bar":
                idx = int(input("Podaj numer kolumny do wykresu słupkowego: "))
                if idx < 0 or idx >= len(df.columns):
                    print("Niepoprawny numer kolumny.")
                    continue
                col = df.columns[idx]
                plt.figure()
                df[col].value_counts().plot(kind="bar")
                plt.title(f"Wykres słupkowy: {col}")
                path = os.path.join(charts_dir, f"chart_{col}_bar.png")
                plt.savefig(path)
                plt.close()
                print(f"Wygenerowano wykres słupkowy: {path}")
                paths.append(path)
            elif chart_type == "line":
                idx_x = int(input("Podaj numer kolumny X: "))
                idx_y = int(input("Podaj numer kolumny Y: "))
                if (
                    idx_x < 0
                    or idx_x >= len(df.columns)
                    or idx_y < 0
                    or idx_y >= len(df.columns)
                ):
                    print("Niepoprawne numery kolumn.")
                    continue
                col_x = df.columns[idx_x]
                col_y = df.columns[idx_y]
                plt.figure()
                df.plot(x=col_x, y=col_y, kind="line")
                plt.title(f"Wykres liniowy: {col_y} wg {col_x}")
                path = os.path.join(charts_dir, f"chart_{col_y}_line.png")
                plt.savefig(path)
                plt.close()
                print(f"Wygenerowano wykres liniowy: {path}")
                paths.append(path)
            elif chart_type == "pie":
                idx = int(input("Podaj numer kolumny do wykresu kołowego: "))
                if idx < 0 or idx >= len(df.columns):
                    print("Niepoprawny numer kolumny.")
                    continue
                col = df.columns[idx]
                plt.figure()
                df[col].value_counts().plot(kind="pie", autopct="%1.1f%%")
                plt.title(f"Wykres kołowy: {col}")
                path = os.path.join(charts_dir, f"chart_{col}_pie.png")
                plt.savefig(path)
                plt.close()
                print(f"Wygenerowano wykres kołowy: {path}")
                paths.append(path)
            else:
                print("Nieznany typ wykresu.")
        except Exception as e:
            print("Błąd podczas generowania wykresu:", e)
    return paths
