# PyReport - Interaktywny generator raportów z plików CSV

## Opis projektu

**PyReport** to narzędzie pozwalające na:
- interaktywne filtrowanie i sortowanie danych z plików `.csv`,
- wybór oraz generowanie wykresów (słupkowych i liniowych),
- eksport gotowego raportu do pliku PDF z tabelą i wykresami.

Projekt pozwala obsłużyć **dowolne dane CSV** - bez potrzeby zmiany kodu źródłowego.

---

## Instrukcja uruchomienia

1. **Wymagania:**
   - Python 3.8+  
   - Zainstalowane biblioteki:  
     ```
     pip install pandas matplotlib fpdf
     ```

2. **Przygotowanie środowiska:**
   - Upewnij się, że w katalogu projektu znajdują się pliki:
     - `main.py`
     - `csv_utils.py`
     - `charts.py`
     - `report.py`
     - `config.yaml` (opcjonalnie)
     - Plik czcionki **DejaVuSans.ttf** (w tym samym folderze co `report.py`!)

3. **Przygotuj katalog `test_data` z plikami CSV do analizy.**
   - Każdy plik `.csv` może mieć inne kolumny i kodowanie (obsługa automatyczna).

4. **Uruchomienie programu:**

- Program poprowadzi Cię przez wybór pliku, filtrowanie, sortowanie i wybór wykresów.

---

## Najważniejsze funkcje

- Automatyczne wykrywanie kodowania pliku.
- Nie pozwala na wielokrotne filtrowanie po tej samej kolumnie.
- Automatyczny wybór pliku .csv z katalogu.
- Prosty kreator wyboru wykresów.
- Generowanie raportu PDF z poprawnymi polskimi znakami.

---

## Kontakt / wsparcie

W razie pytań, błędów lub sugestii – kontaktuj się z zespołem projektu na GitHubie lub przez e-mail.

---

## Autorzy
- [Krzysztof Wojtkowiak]
- [Adam Pajer]
