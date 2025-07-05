import os
import matplotlib.pyplot as plt
from typing import Any, Dict, List
import pandas as pd

def generate_charts(summary: Dict[str, Any], config: Dict[str, Any]) -> List[str]:
    df = summary["dataframe"]
    paths: List[str] = []
    charts_dir = config.get("charts_dir", "charts")
    os.makedirs(charts_dir, exist_ok=True)

    # --- Interaktywny wykres udziału wybranych kategorii na tle całości ---
    print("\n=== Interaktywne generowanie wykresów ===")
    while True:
        print("Czy chcesz utworzyć specjalny wykres udziału wybranych wartości na tle wszystkich? (y/n)")
        resp = input().strip().lower()
        if resp != "y":
            break

        print("Dostępne kolumny:")
        for i, col in enumerate(df.columns):
            print(f"  {i}: {col} (typ: {df[col].dtype})")
        try:
            idx_cat = int(input("Podaj numer kolumny, z której wybierzesz wartości (np. miasto): "))
            col_cat = df.columns[idx_cat]
        except Exception:
            print("Błąd wyboru kolumny.")
            continue

        unique_vals = sorted(df[col_cat].dropna().unique())
        print("Dostępne wartości (np. miasta):")
        for i, val in enumerate(unique_vals):
            print(f"  {i}: {val}")
        idxs = input("Podaj numery wybranych wartości oddzielone przecinkiem (np. 0,2,5): ")
        try:
            idxs = [int(i) for i in idxs.split(",") if i.strip().isdigit()]
            wybrane = [unique_vals[i] for i in idxs]
        except Exception:
            print("Błąd w podaniu wartości.")
            continue

        # zliczanie udziału
        wybrane_counts = [ (df[col_cat] == v).sum() for v in wybrane ]
        inne = len(df) - sum(wybrane_counts)
        labels = wybrane + ["Inne"]
        sizes = wybrane_counts + [inne]

        plt.figure()
        plt.pie(sizes, labels=labels, autopct='%1.1f%%')
        plt.title(f"Udział wybranych wartości z kolumny '{col_cat}' na tle całości")
        chart_path = os.path.join(charts_dir, f"chart_udzial_{col_cat}.png")
        plt.savefig(chart_path)
        plt.close()
        print(f"Wygenerowano wykres udziału: {chart_path}")
        paths.append(chart_path)
        break  # domyślnie 1 raz, jeśli chcesz możliwość kilku, usuń break

    # --- Standardowe wykresy interaktywne (np. bar/line/pie) ---
    while True:
        print("\nTypy wykresów: bar, line, pie")
        chart_type = input("Podaj typ wykresu (ENTER aby zakończyć): ").strip().lower()
        if chart_type == "":
            break
        print("Dostępne kolumny:")
        for i, col in enumerate(df.columns):
            print(f"  {i}: {col} (typ: {df[col].dtype})")
        try:
            if chart_type == "bar":
                idx = int(input("Podaj numer kolumny do wykresu słupkowego: "))
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
                col = df.columns[idx]
                plt.figure()
                df[col].value_counts().plot(kind="pie", autopct='%1.1f%%')
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
