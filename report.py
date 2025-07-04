# report.py
import os
from fpdf import FPDF
import fpdf.ttfonts
from typing import Any, Dict, List

# Wyczyść cache czcionek TTFontFile, aby usunąć stare ścieżki
if hasattr(fpdf.ttfonts.TTFontFile, '_cache'):
    fpdf.ttfonts.TTFontFile._cache.clear()

class PDFReport(FPDF):
    def __init__(self):
        super().__init__()
        # Dynamiczna lokalizacja pliku czcionki obok modułu
        current_dir = os.path.abspath(os.path.dirname(__file__))
        font_path = os.path.join(current_dir, 'DejaVuSans.ttf')
        if not os.path.isfile(font_path):
            raise FileNotFoundError(
                f"Nie znaleziono pliku czcionki: {font_path}. "
                "Upewnij się, że DejaVuSans.ttf jest obok report.py"
            )
        # Rejestrujemy TrueType font z unikalną nazwą i obsługą Unicode
        self.add_font('DejaVuSansLocal', '', font_path, uni=True)
        self.set_font('DejaVuSansLocal', '', 12)

    def header(self):
        # Nagłówek raportu
        self.set_font('DejaVuSansLocal', '', 16)
        self.cell(0, 10, 'Raport danych CSV', ln=True, align='C')
        self.ln(10)

    def add_table(self, df):
        # Tabela danych: nagłówki + pierwsze 20 wierszy
        self.set_font('DejaVuSansLocal', '', 10)
        col_width = self.w / (len(df.columns) + 1)
        # Nagłówki kolumn
        for col in df.columns:
            self.cell(col_width, 10, str(col), border=1)
        self.ln()
        # Wiersze danych
        for _, row in df.iterrows():
            for item in row:
                self.cell(col_width, 10, str(item), border=1)
            self.ln()

    def add_images(self, paths: List[str]):
        # Dodanie wykresów
        for p in paths:
            if os.path.exists(p):
                self.add_page()
                self.image(p, w=180)


def generate_pdf_report(summary: Dict[str, Any], chart_paths: List[str], config: Dict[str, Any]) -> str:
    pdf = PDFReport()
    pdf.add_page()

    # Informacje o pliku
    pdf.cell(0, 10, f"Plik: {os.path.basename(summary['filename'])}", ln=True)
    pdf.cell(0, 10, f"Wiersze: {summary['row_count']}", ln=True)

    # Tabela danych (pierwsze 20 wierszy)
    pdf.ln(5)
    pdf.cell(0, 10, "Tabela danych (pierwsze 20 wierszy):", ln=True)
    pdf.add_table(summary['dataframe'].head(20))

    # Wykresy
    pdf.add_images(chart_paths)

    # Zapis raportu
    rd = config.get('reports_dir', 'reports')
    os.makedirs(rd, exist_ok=True)
    out = os.path.join(
        rd,
        f"report_{os.path.splitext(os.path.basename(summary['filename']))[0]}.pdf",
    )
    pdf.output(out)
    return out
