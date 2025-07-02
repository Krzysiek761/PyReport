from fpdf import FPDF
import os
from typing import Any, Dict, List

class PDFReport(FPDF):
    def header(self):
        self.set_font("Helvetica", "B", 16)
        self.cell(0, 10, "Raport danych CSV", ln=True, align="C")
        self.ln(10)

    def add_table(self, df):
        self.set_font("Helvetica", size=10)
        w = self.w / (len(df.columns) + 1)
        for col in df.columns:
            self.cell(w, 10, str(col), border=1)
        self.ln()
        for _, r in df.iterrows():
            for v in r:
                self.cell(w, 10, str(v), border=1)
            self.ln()

    def add_images(self, paths):
        for p in paths:
            if os.path.exists(p):
                self.add_page()
                self.image(p, w=180)

def generate_pdf_report(summary: Dict[str, Any], chart_paths: List[str], config: Dict[str, Any]) -> str:
    pdf = PDFReport()
    pdf.add_page()
    pdf.set_font("Helvetica", size=12)
    pdf.cell(0, 10, f"Plik: {os.path.basename(summary['filename'])}", ln=True)
    pdf.cell(0, 10, f"Wiersze: {summary['row_count']}", ln=True)
    pdf.ln(5)
    pdf.cell(0, 10, "Tabela danych (pierwsze 20 wierszy):", ln=True)
    pdf.add_table(summary['dataframe'].head(20))
    pdf.add_images(chart_paths)
    rd = config.get("reports_dir", "reports")
    os.makedirs(rd, exist_ok=True)
    out = os.path.join(rd, f"report_{os.path.splitext(os.path.basename(summary['filename']))[0]}.pdf")
    pdf.output(out)
    return out
