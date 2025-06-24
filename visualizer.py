import matplotlib.pyplot as plt
from typing import List, Dict, Any
import os

def generate_charts(summary: Dict[str, Any], config: Dict[str, Any]) -> List[str]:
    df = summary["dataframe"]
    output_paths = []
    chart_config = config.get("charts", [])
    output_dir = config.get("output_dir", "charts")
    os.makedirs(output_dir, exist_ok=True)

    for i, chart in enumerate(chart_config):
        chart_type = chart.get("type")
        columns = chart.get("columns")

        if chart_type == "bar" and len(columns) == 1:
            col = columns[0]
            plt.figure()
            df[col].value_counts().plot(kind="bar")
            path = os.path.join(output_dir, f"chart_{i}_{col}_bar.png")
            plt.savefig(path)
            output_paths.append(path)
            plt.close()

        elif chart_type == "line" and len(columns) == 2:
            x, y = columns
            plt.figure()
            df.plot(x=x, y=y, kind="line")
            path = os.path.join(output_dir, f"chart_{i}_{y}_line.png")
            plt.savefig(path)
            output_paths.append(path)
            plt.close()

    return output_paths
