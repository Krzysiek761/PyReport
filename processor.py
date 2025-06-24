import pandas as pd
from typing import Dict, Any

def process_csv_file(path: str, config: Dict[str, Any]) -> Dict[str, Any]:
    df = pd.read_csv(path)

    summary = {
        "filename": path,
        "columns": df.columns.tolist(),
        "row_count": len(df),
        "column_types": df.dtypes.astype(str).to_dict(),
        "numerical_summary": {},
        "dataframe": df,
    }

    numerical_cols = df.select_dtypes(include=["number"]).columns
    for col in numerical_cols:
        summary["numerical_summary"][col] = {
            "sum": df[col].sum(),
            "mean": df[col].mean(),
            "min": df[col].min(),
            "max": df[col].max(),
        }

    if config.get("filter"):
        for condition in config["filter"]:
            col = condition["column"]
            op = condition["operator"]
            val = condition["value"]
            if op == ">":
                df = df[df[col] > val]
            elif op == "<":
                df = df[df[col] < val]
            elif op == "==":
                df = df[df[col] == val]
        summary["filtered"] = True
        summary["dataframe"] = df

    if config.get("sort_by"):
        df = df.sort_values(by=config["sort_by"])
        summary["dataframe"] = df

    return summary
