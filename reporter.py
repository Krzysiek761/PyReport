from fpdf import FPDF
import os
from typing import Dict, Any, List

class PDFReport(FPDF):
    def header(self):
        self.set_font("Helvetica", "B", 16)
        self.cell(0, 10, "Raport danych CSV", ln=True, align="C")
        self.ln(10)

    def add_table(self, dataframe):
        self.set_font("Helvetica", size=10)
        col_width = self.w / (len(dataframe.columns) + 1)
        for col in dataframe.columns:
            self.cell(col_width, 10, col, border=1)
        self.ln()
        for _, row in dataframe.iterrows():
            for item in row:
                self.cell(col_width, 10, str(item), border=1)
            self.ln()

    def add_images(self, chart_paths: List[str]):
        for path in chart_paths:
            if os.path.exists(path):
                self.add_page()
                self.image(path, w=180)

def generate_pdf_report(filename: str, summary: Dict[str, Any], chart_paths: List[str], config: Dict[str, Any]):
    pdf = PDFReport()
    pdf.add_page()

    pdf.set_font("Helvetica", size=12)
    pdf.cell(0, 10, f"Plik: {os.path.basename(filename)}", ln=True)
    pdf.cell(0, 10, f"Wiersze: {summary['row_count']}", ln=True)

    pdf.ln(5)
    pdf.cell(0, 10, "Tabela danych:", ln=True)
    df = summary["dataframe"].head(20)  # ogranicz do 20 wierszy
    pdf.add_table(df)

    pdf.add_images(chart_paths)

    output_dir = config.get("output_dir", "reports")
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, f"report_{os.path.splitext(os.path.basename(filename))[0]}.pdf")
    pdf.output(output_path)
