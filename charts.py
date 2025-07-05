import os
import matplotlib.pyplot as plt
from typing import Any, Dict, List

def generate_charts(summary: Dict[str, Any], config: Dict[str, Any]) -> List[str]:
    df = summary["dataframe"]
    paths: List[str] = []
    charts_dir = config.get("charts_dir", "charts")
    os.makedirs(charts_dir, exist_ok=True)

    charts_cfg = config.get("charts", [])
    # Jeśli nie zdefiniowano wykresów w configu – przejdź do trybu interaktywnego!
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
                idx = int(input("Podaj numer kolumny do wykresu słupkowego: "))
                col = df.columns[idx]
                plt.figure()
                df[col].value_counts().plot(kind="bar")
                p = os.path.join(charts_dir, f"chart_{col}_bar.png")
                plt.savefig(p)
                plt.close()
                paths.append(p)
                print(f"Wygenerowano wykres słupkowy: {p}")
            elif typ == "line":
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
        # Tryb automatyczny – wykresy wg config.yaml
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
