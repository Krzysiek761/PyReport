import os
import matplotlib.pyplot as plt
from typing import Any, Dict, List


def generate_charts(summary: Dict[str, Any], config: Dict[str, Any]) -> List[str]:
    df = summary["dataframe"]
    paths: List[str] = []
    charts_dir = config.get("charts_dir", "charts")
    os.makedirs(charts_dir, exist_ok=True)
    for i, chart in enumerate(config.get("charts", [])):
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
