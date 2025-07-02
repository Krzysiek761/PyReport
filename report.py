import os
from fpdf import FPDF
from typing import Any, Dict, List

class PDFReport(FPDF):
    def __init__(self):
        super().__init__()
        # rejestracja czcionki TrueType dla obsługi UTF-8
        font_path = os.path.join(os.path.dirname(__file__), 'DejaVuSans.ttf')
        self.add_font('DejaVu', '', font_path, uni=True)
        self.set_font('DejaVu', '', 12)

    def header(self):
        # nagłówek raportu
        self.set_font('DejaVu', '', 16)
        self.cell(0, 10, 'Raport danych CSV', ln=True, align='C')
        self.ln(10)

    def add_table(self, df):
        # tabela danych
        self.set_font('DejaVu', '', 10)
        col_width = self.w / (len(df.columns) + 1)
        # nagłówki kolumn
        for col in df.columns:
            self.cell(col_width, 10, str(col), border=1)
        self.ln()
        # wiersze danych
        for _, row in df.iterrows():
            for item in row:
                self.cell(col_width, 10, str(item), border=1)
            self.ln()

    def add_images(self, paths: List[str]):
        # dodawanie wykresów
        for path in paths:
            if os.path.exists(path):
                self.add_page()
                self.image(path, w=180)


def generate_pdf_report(summary: Dict[str, Any], chart_paths: List[str], config: Dict[str, Any]) -> str:
    pdf = PDFReport()
    pdf.add_page()

    # podstawowe informacje
    pdf.cell(0, 10, f"Plik: {os.path.basename(summary['filename'])}", ln=True)
    pdf.cell(0, 10, f"Wiersze: {summary['row_count']}", ln=True)

    pdf.ln(5)
    pdf.cell(0, 10, 'Tabela danych (pierwsze 20 wierszy):', ln=True)
    pdf.add_table(summary['dataframe'].head(20))

    # wykresy
    pdf.add_images(chart_paths)

    # zapisz PDF
    rd = config.get('reports_dir', 'reports')
    os.makedirs(rd, exist_ok=True)
    out = os.path.join(
        rd,
        f"report_{os.path.splitext(os.path.basename(summary['filename']))[0]}.pdf",
    )
    pdf.output(out)
    return out
