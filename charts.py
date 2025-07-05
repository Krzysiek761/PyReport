import os
import matplotlib.pyplot as plt
from typing import Any, Dict, List

def input_column_number(prompt: str, df_columns) -> int:
    """Bezpieczne pobieranie numeru kolumny od użytkownika."""
    while True:
        val = input(prompt)
        if val == "":
            return None  # Pozwala na opcjonalność, np. dla liczebności
        try:
            idx = int(val)
            if 0 <= idx < len(df_columns):
                return idx
            else:
                print(f"Błąd: Podaj numer od 0 do {len(df_columns)-1}.")
        except ValueError:
            print("Błąd: Podaj numer kolumny (liczbę), a nie jej nazwę!")

def generate_charts(summary: Dict[str, Any], config: Dict[str, Any]) -> List[str]:
    df = summary["dataframe"]
    paths: List[str] = []
    charts_dir = config.get("charts_dir", "charts")
    os.makedirs(charts_dir, exist_ok=True)

    charts_cfg = config.get("charts", [])

    # === Kreator interaktywny ===
    if not charts_cfg:
        print("\n=== Kreator interaktywnego generowania wykresów ===")
        print("Dostępne kolumny:")
        for i, col in enumerate(df.columns):
            print(f"  {i}: {col} (typ: {df[col].dtype})")
        while True:
            chce_wykres = input("\nCzy chcesz utworzyć wykres? (y/n): ").strip().lower()
            if chce_wykres != "y":
                break
            print("Dostępne typy wykresów: bar (słupkowy), pie (okrągły)")
            typ = input("Wybierz typ wykresu: ").strip().lower()
            if typ not in ["bar", "pie"]:
                print("Nieznany typ wykresu.")
                continue
            idx_cat = input_column_number("Podaj numer kolumny kategorii (np. 'Miasto', 'Produkt'): ", df.columns)
            if idx_cat is None:
                print("Przerwano wybór wykresu.")
                continue
            col_cat = df.columns[idx_cat]
            # Opcjonalny filtr na wybrane wartości kategorii
            unikalne = df[col_cat].unique()
            print(f"Unikalne wartości w '{col_cat}': {', '.join(map(str, unikalne))}")
            filtruj = input(f"Czy chcesz pokazać tylko wybrane wartości z '{col_cat}'? (y/n): ").strip().lower()
            if filtruj == "y":
                wybrane = input("Podaj wartości oddzielone przecinkiem (np. Kraków,Warszawa): ").strip()
                wartosci = [w.strip() for w in wybrane.split(",") if w.strip()]
                df_filt = df[df[col_cat].isin(wartosci)]
            else:
                df_filt = df
            if typ == "bar":
                print("Podpowiedź: Możesz policzyć sumę wartości (np. Sprzedaż) lub liczebność rekordów.")
                val_in = input("Podaj numer kolumny z wartościami liczbowymi (np. 'Sprzedaż', 'nr_indeksu') lub ENTER dla liczebności: ").strip()
                plt.figure()
                if val_in:
                    try:
                        idx_val = int(val_in)
                        if 0 <= idx_val < len(df.columns):
                            col_val = df.columns[idx_val]
                            data = df_filt.groupby(col_cat)[col_val].sum()
                            data.plot(kind="bar")
                        else:
                            print(f"Błąd: Numer spoza zakresu (0–{len(df.columns)-1}), pomijam wykres.")
                            plt.close()
                            continue
                    except ValueError:
                        print("Błąd: Podaj numer kolumny z wartościami liczbowymi (liczbę) lub ENTER.")
                        plt.close()
                        continue
                else:
                    df_filt[col_cat].value_counts().plot(kind="bar")
                p = os.path.join(charts_dir, f"chart_{col_cat}_bar.png")
                plt.savefig(p)
                plt.close()
                paths.append(p)
                print(f"Wygenerowano wykres słupkowy: {p}")
            elif typ == "pie":
                # Pie wykres tylko liczebność kategorii (w filtrze)
                plt.figure()
                df_filt[col_cat].value_counts().plot(kind="pie", autopct='%1.1f%%')
                plt.ylabel("")
                p = os.path.join(charts_dir, f"chart_{col_cat}_pie.png")
                plt.savefig(p)
                plt.close()
                paths.append(p)
                print(f"Wygenerowano wykres okrągły: {p}")
    else:
        # === Tryb automatyczny (config.yaml) ===
        for i, chart in enumerate(charts_cfg):
            t = chart.get("type")
            cols = chart.get("columns", [])
            # verify columns exist
            if any(c not in df.columns for c in cols):
                print(f"[WARN] Niektóre kolumny {cols} nie istnieją, pomijam wykres.")
                continue
            if t == "bar" and len(cols) == 1:
                c = cols[0]
                if df[c].dropna().empty:
                    continue
                plt.figure()
                df[c].value_counts().plot(kind="bar")
                p = os.path.join(charts_dir, f"chart_{i}_{c}_bar.png")
                plt.savefig(p)
                plt.close()
                paths.append(p)
            elif t == "bar" and len(cols) == 2:
                # bar z sumą wartości liczbowych względem kategorii
                cat_col, val_col = cols
                if df[[cat_col, val_col]].dropna().empty:
                    continue
                plt.figure()
                df.groupby(cat_col)[val_col].sum().plot(kind="bar")
                p = os.path.join(charts_dir, f"chart_{i}_{cat_col}_{val_col}_bar.png")
                plt.savefig(p)
                plt.close()
                paths.append(p)
            elif t == "pie" and len(cols) == 1:
                c = cols[0]
                if df[c].dropna().empty:
                    continue
                plt.figure()
                df[c].value_counts().plot(kind="pie", autopct='%1.1f%%')
                plt.ylabel("")
                p = os.path.join(charts_dir, f"chart_{i}_{c}_pie.png")
                plt.savefig(p)
                plt.close()
                paths.append(p)
            elif t == "line" and len(cols) == 2:
                x, y = cols
                if df[[x, y]].dropna().empty:
                    continue
                plt.figure()
                df.plot(x=x, y=y, kind="line")
                p = os.path.join(charts_dir, f"chart_{i}_{y}_line.png")
                plt.savefig(p)
                plt.close()
                paths.append(p)
    return paths
