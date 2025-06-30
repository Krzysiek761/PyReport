from csv_pdf_report_tool.csv_loader import load_csv
from csv_pdf_report_tool.chart_generator import generate_bar_chart
from csv_pdf_report_tool.report_generator import generate_pdf_report

if __name__ == '__main__':
    csv_path = 'test_data.csv'
    chart_path = 'chart.png'
    pdf_path = 'report.pdf'

    df = load_csv(csv_path)
    if df is not None:
        generate_bar_chart(df, 'Produkt', 'Sprzedaz', chart_path)
        generate_pdf_report('Sales Report', df, chart_path, pdf_path)
        print(f"Report generated at: {pdf_path}")
