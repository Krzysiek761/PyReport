import os
import tempfile
import pandas as pd
from report import generate_pdf_report


def get_font_path():
    # Szukaj czcionki w tym samym folderze co report.py
    return os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "..", "DejaVuSans.ttf"
    )


def test_generate_pdf_report_creates_pdf():
    # Przygotuj przykładowe dane
    df = pd.DataFrame({"kol1": ["A", "B", "C"], "kol2": [1, 2, 3]})
    summary = {
        "filename": "dane.csv",
        "columns": ["kol1", "kol2"],
        "row_count": 3,
        "column_types": {"kol1": "object", "kol2": "int64"},
        "numerical_summary": {"kol2": {"sum": 6, "mean": 2, "min": 1, "max": 3}},
        "dataframe": df,
    }
    font_path = get_font_path()
    assert os.path.exists(font_path), f"Brakuje czcionki {font_path} do testu!"
    with tempfile.TemporaryDirectory() as tmpdir:
        config = {"reports_dir": tmpdir}
        out_path = generate_pdf_report(summary, chart_paths=[], config=config)
        assert os.path.exists(out_path)
        assert out_path.endswith(".pdf")
        # Plik powinien być niepusty
        assert os.path.getsize(out_path) > 0


def test_generate_pdf_with_chart():
    # Przygotuj dane i "fałszywy wykres" (obrazek)
    df = pd.DataFrame({"A": [1, 2, 3], "B": ["x", "y", "z"]})
    summary = {
        "filename": "dane2.csv",
        "columns": ["A", "B"],
        "row_count": 3,
        "column_types": {"A": "int64", "B": "object"},
        "numerical_summary": {"A": {"sum": 6, "mean": 2, "min": 1, "max": 3}},
        "dataframe": df,
    }
    font_path = get_font_path()
    assert os.path.exists(font_path), f"Brakuje czcionki {font_path} do testu!"
    with tempfile.TemporaryDirectory() as tmpdir:
        # Utwórz przykładowy wykres (jako plik PNG)
        chart_path = os.path.join(tmpdir, "dummy_chart.png")
        import matplotlib.pyplot as plt

        plt.figure()
        plt.plot([1, 2, 3])
        plt.savefig(chart_path)
        plt.close()

        config = {"reports_dir": tmpdir}
        out_path = generate_pdf_report(summary, chart_paths=[chart_path], config=config)
        assert os.path.exists(out_path)
        assert out_path.endswith(".pdf")
        assert os.path.getsize(out_path) > 0
