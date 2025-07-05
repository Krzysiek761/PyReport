import os
import matplotlib.pyplot as plt
from typing import Any, Dict, List

def generate_charts(summary: Dict[str, Any], config: Dict[str, Any]) -> List[str]:
    df = summary["dataframe"]
    paths: List[str] = []
    charts_dir = config.get("charts_dir", "charts")
    os.makedirs(charts_dir, exist_ok=True)

    charts_cfg = config.get("charts", [])

    # === Tryb interaktywny ===
    if not charts_cfg:
        print("\n=== Interaktywne generowanie wykresów ===")
        print("Dostępne kolumny:")
        for i, col in enumerate(df.columns):
            print(f"  {i}: {col} (typ: {df[col].dtype})")
        while True:
            print("\nTypy wykresów: bar, line")
            typ = input("Podaj typ wykresu (ENTER aby zakończyć): ").strip()
            if not typ:
                break
            if typ == "bar":
                print("Podpowiedź: Wykres słupkowy najlepiej pokazuje sumy lub liczebność dla wybranej kategorii.")
                idx_cat = int(input("Podaj numer kolumny kategorii (np. 'Kategoria'): "))
                col_cat = df.columns[idx_cat]
                val_in = input("Podaj numer kolumny z wartościami liczbowymi (np. 'Sprzedaż') lub ENTER aby policzyć tylko liczebność: ").strip()
                plt.figure()
                if val_in:
                    col_val = df.columns[int(val_in)]
                    data = df.groupby(col_cat)[col_val].sum()
                    data.plot(kind="bar")
                else:
                    df[col_cat].value_counts().plot(kind="bar")
                p = os.path.join(charts_dir, f"chart_{col_cat}_bar.png")
                plt.savefig(p)
                plt.close()
                paths.append(p)
                print(f"Wygenerowano wykres słupkowy: {p}")
            elif typ == "line":
                print("Podpowiedź: Wykres liniowy ma sens, gdy oś X to liczby lub daty, a Y to wartości liczbowe.")
                idx_x = int(input("Podaj numer kolumny X: "))
                idx_y = int(input("Podaj numer kolumny Y: "))
                col_x = df.columns[idx_x]
                col_y = df.columns[idx_y]
                plt.figure()
                df.plot(x=col_x, y=col_y, kind="line")
                p = os.path.join(charts_dir, f"chart_{col_y}_line.png")
                plt.savefig(p)
                plt.close()
                paths.append(p)
                print(f"Wygenerowano wykres liniowy: {p}")
            else:
                print("Nieznany typ wykresu.")
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
