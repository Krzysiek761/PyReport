import pandas as pd

def load_csv_file(file_path):
    """
    Wczytuje plik CSV z podanej ścieżki i zwraca DataFrame
    """
    return pd.read_csv(file_path)
