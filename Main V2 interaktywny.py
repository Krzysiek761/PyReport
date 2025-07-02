#!/usr/bin/env python3
import os
import argparse
from typing import Any, Dict, List

import yaml
import pandas as pd
import matplotlib.pyplot as plt
from fpdf import FPDF
import re


def load_config(path: str) -> Dict[str, Any]:
    """Load YAML configuration from *path*."""
    with open(path, "r", encoding="utf-8") as file:
        return yaml.safe_load(file) or {}


def discover_csv_files(directory: str) -> List[str]:
    """Return a list of CSV files found in *directory*."""
    return [
        os.path.join(directory, f)
        for f in os.listdir(directory)
        if f.endswith(".csv") and os.path.isfile(os.path.join(directory, f))
    ]



def interactive_choose_file(files: List[str]) -> List[str]:
    """Allow user to select one CSV file or process all."""
    print("\n=== Wybór pliku CSV do przetworzenia ===")
    for idx, path in enumerate(files):
        print(f"  {idx}: {os.path.basename(path)}")
    choice = input("Wybierz numer pliku (lub ENTER, aby przetworzyć wszystkie): ").strip()
    if choice.isdigit():
        idx = int(choice)
        if 0 <= idx < len(files):
            print(f"Wybrano: {os.path.basename(files[idx])}")
            return [files[idx]]
        else:
            print("Nieprawidłowy numer, zostaną przetworzone wszystkie pliki.")
    return files


def interactive_filter(df: pd.DataFrame) -> pd.DataFrame:
    """Interactively ask user for filtering conditions and apply them to df."""
    filtered_df = df
    print("\n=== Interaktywne filtrowanie danych ===")
    while True:
        kontynuuj = input("Czy chcesz dodać warunek filtrowania? (y/n): ").strip().lower()
        if kontynuuj != 'y':
            break
        print("Dostępne kolumny do filtrowania:")
        for idx, col in enumerate(df.columns):
            print(f"  {idx}: {col} (typ: {df[col].dtype})")
        try:
            col_idx = int(input("Wybierz numer kolumny: ").strip())
            col = df.columns[col_idx]
        except (ValueError, IndexError):
            print("Nieprawidłowy numer kolumny, spróbuj ponownie.")
            continue
        cond_str = input(
            f"Wprowadź warunek dla '{col}' (np. '> 20' lub '== Warsaw'): "
        ).strip()
        match = re.match(r'^(>=|<=|==|!=|>|<)\s*(.+)$', cond_str)
        if not match:
            print("Niepoprawny format, spróbuj ponownie.")
            continue
        op, val_raw = match.group(1), match.group(2)
        if df[col].dtype.kind in 'iuf':
            try:
                val: Any = float(val_raw)
            except ValueError:
                print("Nieprawidłowa wartość numeryczna, spróbuj ponownie.")
                continue
        else:
            val = val_raw
        expr = {
            '>': df[col] > val,
            '<': df[col] < val,
            '==': df[col] == val,
            '!=': df[col] != val,
            '>=': df[col] >= val,
            '<=': df[col] <= val
        }.get(op)
        if expr is None:
            print("Nieobsługiwany operator.")
            continue
        filtered_df = filtered_df[expr]
        print(f"Liczba wierszy po filtrze: {len(filtered_df)}")
    return filtered_df


def interactive_sort(df: pd.DataFrame) -> pd.DataFrame:
    """Interactively ask user which column to sort by and order."""
    print("\n=== Interaktywne sortowanie danych ===")
    print("Dostępne kolumny do sortowania:")
    for idx, col in enumerate(df.columns):
        if df[col].dtype.kind in 'iuf':
            info = f"(liczbowy, min={df[col].min()}, max={df[col].max()})"
        else:
            uniq = df[col].dropna().unique()[:5]
            info = f"(kategoryczny, przykłady: {', '.join(map(str, uniq))})"
        print(f"  {idx}: {col} {info}")
    choice = input("Wybierz numer kolumny do sortowania (lub ENTER, aby pominąć): ").strip()
    if choice.isdigit():
        idx = int(choice)
        if 0 <= idx < len(df.columns):
            col = df.columns[idx]
            order = input("Kolejność: asc/desc [asc]: ").strip().lower() or 'asc'
            df = df.sort_values(by=col, ascending=(order=='asc'))
            print(f"Dane posortowane według '{col}' ({order})")
        else:
            print("Nieprawidłowy numer, pomijam sortowanie.")
    else:
        print("Pominięto sortowanie.")
    return df


def process_csv_file(path: str, config: Dict[str, Any]) -> Dict[str, Any]:
    """Read *path* and return basic statistics and optionally filtered and sorted data."""
    df = pd.read_csv(path)
    print(f"\nŁaduję plik: {os.path.basename(path)} | wiersze: {len(df)} | kolumny: {list(df.columns)}")
    if config.get("interactive_filter", True):
        df = interactive_filter(df)
    if config.get("interactive_sort", True):
        df = interactive_sort(df)
    summary: Dict[str, Any] = {
        "filename": path,
        "columns": df.columns.tolist(),
        "row_count": len(df),
        "column_types": df.dtypes.astype(str).to_dict(),
        "numerical_summary": {},
        "dataframe": df,
    }
    for col in df.select_dtypes(include=["number"]).columns:
        summary["numerical_summary"][col] = {
            "sum": df[col].sum(),
            "mean": df[col].mean(),
            "min": df[col].min(),
            "max": df[col].max(),
        }
    return summary


def generate_charts(summary: Dict[str, Any], config: Dict[str, Any]) -> List[str]:
    """Create charts based on *summary* according to *config*."""
    df = summary["dataframe"]
    paths: List[str] = []
    for i, chart in enumerate(config.get("charts", [])):
        t = chart.get("type")
        cols = chart.get("columns", [])
        charts_dir = config.get("charts_dir", "charts")
        os.makedirs(charts_dir, exist_ok=True)
        if t=="bar" and len(cols)==1:
            c=cols[0]
            if df[c].dropna().empty: continue
            plt.figure(); df[c].value_counts().plot(kind="bar")
            p=os.path.join(charts_dir,f"chart_{i}_{c}_bar.png");plt.savefig(p);plt.close();paths.append(p)
        if t=="line" and len(cols)==2:
            x,y=cols
            if df[[x,y]].dropna().empty: continue
            plt.figure(); df.plot(x=x,y=y,kind="line")
            p=os.path.join(charts_dir,f"chart_{i}_{y}_line.png");plt.savefig(p);plt.close();paths.append(p)
    return paths


class PDFReport(FPDF):
    def header(self):
        self.set_font("Helvetica","B",16); self.cell(0,10,"Raport danych CSV",ln=True,align="C"); self.ln(10)
    def add_table(self,df):
        self.set_font("Helvetica",size=10);w=self.w/(len(df.columns)+1)
        for col in df.columns: self.cell(w,10,str(col),border=1)
        self.ln()
        for _,r in df.iterrows():
            for v in r: self.cell(w,10,str(v),border=1)
            self.ln()
    def add_images(self,paths):
        for p in paths:
            if os.path.exists(p): self.add_page();self.image(p,w=180)


def generate_pdf_report(summary:Dict[str,Any],chart_paths:List[str],config:Dict[str,Any])->str:
    pdf=PDFReport();pdf.add_page()
    pdf.set_font("Helvetica",size=12)
    pdf.cell(0,10,f"Plik: {os.path.basename(summary['filename'])}",ln=True)
    pdf.cell(0,10,f"Wiersze: {summary['row_count']}",ln=True)
    pdf.ln(5);pdf.cell(0,10,"Tabela danych (pierwsze 20 wierszy):",ln=True)
    pdf.add_table(summary['dataframe'].head(20));pdf.add_images(chart_paths)
    rd=config.get("reports_dir","reports");os.makedirs(rd,exist_ok=True)
    out=os.path.join(rd,f"report_{os.path.splitext(os.path.basename(summary['filename']))[0]}.pdf")
    pdf.output(out);return out


def main():
    p=argparse.ArgumentParser("CSV to PDF report")
    p.add_argument("-c","--config",default="config.yaml");p.add_argument("-i","--input-dir");p.add_argument("--charts-dir");p.add_argument("--reports-dir")
    args=p.parse_args();cfg=load_config(args.config)
    if args.input_dir: cfg['input_dir']=args.input_dir
    if args.charts_dir: cfg['charts_dir']=args.charts_dir
    if args.reports_dir: cfg['reports_dir']=args.reports_dir

    files=discover_csv_files(cfg.get("input_dir","test_data"))
    if cfg.get("interactive_choose_file",True): files=interactive_choose_file(files)
    for f in files:
        print(f"\n=== Przetwarzanie: {f} ===")
        sumry=process_csv_file(f,cfg)
        charts=generate_charts(sumry,cfg)
        rpt=generate_pdf_report(sumry,charts,cfg)
        print(f"Generated: {rpt}")

if __name__=="__main__": main()
