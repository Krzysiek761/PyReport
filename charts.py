import os
import matplotlib.pyplot as plt
from typing import Any, Dict, List

def generate_charts(summary: Dict[str, Any], config: Dict[str, Any]) -> List[str]:
    df = summary["dataframe"]
    paths = []
    for i, chart in enumerate(config.get("charts", [])):
        t = chart.get("type")
        cols = chart.get("columns", [])
        charts_dir = config.get("charts_dir", "charts")
        os.makedirs(charts_dir, exist_ok=True)
        if t == "bar" and len(cols) == 1:
            c = cols[0]
            plt.figure(); df[c].value_counts().plot(kind="bar")
            p = os.path.join(charts_dir, f"chart_{i}_{c}_bar.png")
            plt.savefig(p); plt.close(); paths.append(p)
        if t == "line" and len(cols) == 2:
            x, y = cols
            plt.figure(); df.plot(x=x, y=y, kind="line")
            p = os.path.join(charts_dir, f"chart_{i}_{y}_line.png")
            plt.savefig(p); plt.close(); paths.append(p)
    return paths
