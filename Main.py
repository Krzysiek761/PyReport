# src/processor.py
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


# tests/test_processor.py
import pytest
import pandas as pd
import tempfile
import os
from src.processor import process_csv_file

@pytest.fixture
def sample_csv_file():
    data = """A,B,C
1,2,3
4,5,6
7,8,9
"""
    with tempfile.NamedTemporaryFile(delete=False, mode='w', suffix=".csv") as f:
        f.write(data)
        temp_path = f.name
    yield temp_path
    os.unlink(temp_path)

def test_basic_summary(sample_csv_file):
    config = {}
    result = process_csv_file(sample_csv_file, config)

    assert result["row_count"] == 3
    assert set(result["columns"]) == {"A", "B", "C"}
    assert "numerical_summary" in result
    assert result["numerical_summary"]["A"]["sum"] == 12


def test_filter_and_sort(sample_csv_file):
    config = {
        "filter": [{"column": "A", "operator": ">", "value": 2}],
        "sort_by": "B"
    }
    result = process_csv_file(sample_csv_file, config)
    df = result["dataframe"]

    assert result["filtered"] is True
    assert df.iloc[0]["A"] == 4  # after filtering and sorting
