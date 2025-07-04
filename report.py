
from fpdf import FPDF
import os
import matplotlib.pyplot as plt

def generate_pdf_report(df, file_name, chart_type="Bar"):
    pdf = FPDF()
    pdf.add_page()

    # Dodaj font z obsługą polskich znaków
    pdf.add_font("DejaVu", "", "DejaVuSans.ttf", uni=True)
    pdf.set_font("DejaVu", '', 16)
    pdf.cell(0, 10, "Raport danych", ln=True, align='C')

    pdf.set_font("DejaVu", '', 12)
    if 'filename' in df.columns:
        pdf.cell(0, 10, f"Plik: {os.path.basename(df['filename'].iloc[0])}", ln=True)
    else:
        pdf.cell(0, 10, f"Plik: {file_name}", ln=True)

    pdf.ln(10)

    # Wstaw dane jako tekst
    for col in df.columns:
        value_str = ', '.join(map(str, df[col].unique()[:5]))
        pdf.cell(0, 10, f"{col}: {value_str}", ln=True)

    # Wykres
    if len(df.columns) >= 2:
        x = df[df.columns[0]]
        y = df[df.columns[1]]

        plt.figure()
        if chart_type == "Bar":
            plt.bar(x, y)
        elif chart_type == "Line":
            plt.plot(x, y)
        elif chart_type == "Pie":
            plt.pie(y, labels=x, autopct='%1.1f%%')

        plt.title(f"{chart_type} Chart")
        chart_file = "temp_chart.png"
        plt.savefig(chart_file)
        plt.close()

        # Dodaj wykres do PDF
        pdf.image(chart_file, x=10, y=None, w=180)
        os.remove(chart_file)

    # Zapisz PDF
    output_path = os.path.join("reports", f"report_{os.path.splitext(file_name)[0]}.pdf")
    pdf.output(output_path)
    return output_path
