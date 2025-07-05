import os
import tempfile
import pandas as pd
import pytest

from csv_utils import (
    process_csv_file,
    interactive_filter,
    interactive_sort,
    discover_csv_files,
    interactive_choose_file,
)


# 1. Test podstawowy (wczytanie pliku)
def test_process_csv_file_basic():
    df = pd.DataFrame(
        {
            "miasto": ["Warszawa", "Kraków", "Gdańsk"],
            "wiek": [21, 22, 23],
        }
    )
    with tempfile.TemporaryDirectory() as tmpdir:
        csv_path = os.path.join(tmpdir, "sample.csv")
        df.to_csv(csv_path, index=False, encoding="utf-8")
        summary = process_csv_file(
            csv_path, config={"interactive_filter": False, "interactive_sort": False}
        )
        assert summary["row_count"] == 3
        assert "miasto" in summary["columns"]
        assert summary["numerical_summary"]["wiek"]["max"] == 23


# 2. Test filtrowania automatycznego
def test_filtering(monkeypatch):
    df = pd.DataFrame(
        {
            "miasto": ["Warszawa", "Kraków", "Gdańsk"],
            "wiek": [21, 22, 23],
        }
    )
    # Symulujemy wejście użytkownika: wybierz kolumnę 1 ('wiek'), warunek '>21', zakończ
    inputs = iter(
        [
            "y",  # chcesz filtrować? TAK
            "1",  # kolumna 'wiek'
            ">21",  # warunek
            "n",  # nie chcę kolejnego warunku
        ]
    )
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))
    filtered = interactive_filter(df)
    # powinny zostać tylko Kraków i Gdańsk
    assert len(filtered) == 2
    assert set(filtered["miasto"]) == {"Kraków", "Gdańsk"}


# 3. Test sortowania automatycznego
def test_sorting(monkeypatch):
    df = pd.DataFrame(
        {
            "miasto": ["Warszawa", "Kraków", "Gdańsk"],
            "wiek": [22, 23, 21],
        }
    )
    # Symulujemy: wybierz kolumnę 1 ('wiek'), sortuj rosnąco
    inputs = iter(["1", "asc"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))
    sorted_df = interactive_sort(df)
    assert list(sorted_df["wiek"]) == [21, 22, 23]


# 4. Test automatycznego wykrycia plików CSV w katalogu
def test_discover_csv_files():
    with tempfile.TemporaryDirectory() as tmpdir:
        path1 = os.path.join(tmpdir, "test1.csv")
        path2 = os.path.join(tmpdir, "test2.csv")
        pd.DataFrame({"a": [1]}).to_csv(path1, index=False)
        pd.DataFrame({"b": [2]}).to_csv(path2, index=False)
        files = discover_csv_files(tmpdir)
        assert set(os.path.basename(f) for f in files) == {"test1.csv", "test2.csv"}


# 5. Test wyboru pliku (interaktywny, symulowany)
def test_interactive_choose_file(monkeypatch):
    files = ["plik1.csv", "plik2.csv", "plik3.csv"]
    inputs = iter(["1"])  # użytkownik wybiera plik o indeksie 1
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))
    selected = interactive_choose_file(files)
    assert selected == ["plik2.csv"]


# 6. (Opcjonalnie) Możesz dodać testy dla nowych funkcji w przyszłości:
def test_empty_filter(monkeypatch):
    # Użytkownik nie chce filtrować
    df = pd.DataFrame({"a": [1, 2, 3]})
    inputs = iter(["n"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))
    filtered = interactive_filter(df)
    assert filtered.equals(df)


# (Kolejne testy rozbudujesz wg. potrzeb!)
