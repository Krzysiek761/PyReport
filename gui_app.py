import streamlit as st
import os
import pandas as pd
from report import generate_pdf_report  # zakładam, że masz taką funkcję
from csv_utils import load_csv_file  # zakładam, że masz taką funkcję

DATA_DIR = "test_data"
REPORT_DIR = "reports"

st.set_page_config(page_title="Generator Raportów", layout="centered")
st.title("📄 Generator Raportów z Plików CSV")

# Wczytaj pliki CSV z katalogu lub od użytkownika
uploaded_file = st.file_uploader("Lub prześlij własny plik CSV:", type="csv")

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    file_name = uploaded_file.name
else:
    csv_files = [f for f in os.listdir(DATA_DIR) if f.endswith(".csv")]
    file_choice = st.selectbox("Wybierz plik CSV:", csv_files)
    file_path = os.path.join(DATA_DIR, file_choice)
    df = load_csv_file(file_path)
    file_name = file_choice

if df is not None:
    st.subheader("Podgląd danych:")
    st.dataframe(df.head())

    # Filtrowanie danych
    st.markdown("### 🔍 Filtrowanie danych")
    filter_column = st.selectbox("Wybierz kolumnę do filtrowania:", df.columns)
    unique_vals = df[filter_column].dropna().unique()
    filter_value = st.selectbox("Wybierz wartość:", unique_vals)
    filtered_df = df[df[filter_column] == filter_value]

    # Wybór kolumn do analizy
    st.markdown("### 📊 Wybór kolumn do analizy")
    selected_columns = st.multiselect("Zaznacz kolumny do uwzględnienia:", df.columns.tolist(), default=df.columns.tolist())
    analysis_df = filtered_df[selected_columns]

    # Wybór typu wykresu
    st.markdown("### 📈 Wybór typu wykresu")
    chart_type = st.radio("Typ wykresu:", ["Bar", "Line", "Pie"])

    if st.button("Generuj raport PDF"):
        report_path = generate_pdf_report(analysis_df, file_name, chart_type)
        st.success(f"Raport zapisany jako: {report_path}")
        with open(report_path, "rb") as f:
            st.download_button("Pobierz raport", f, file_name=os.path.basename(report_path))
