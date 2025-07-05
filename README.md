# PyReport – Interaktywny generator raportów z plików CSV

## Opis projektu

**PyReport** to narzędzie, które pozwala na:
- interaktywne filtrowanie i sortowanie danych z plików `.csv`,
- wybór oraz generowanie wykresów (słupkowych, liniowych i kołowych),
- eksport gotowego raportu do pliku PDF z tabelą i wykresami.

Projekt obsługuje **dowolne dane CSV** – nie wymaga modyfikacji kodu źródłowego dla nowych danych.

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
     - plik czcionki **DejaVuSans.ttf** (w tym samym folderze co `report.py`!)

3. **Przygotuj katalog `test_data` z plikami CSV do analizy.**
   - Każdy plik `.csv` może mieć inne kolumny i kodowanie (obsługa automatyczna).

4. **Uruchom program:**

    ```bash
    python main.py
    ```

   Program przeprowadzi Cię przez wybór pliku, filtrowanie, sortowanie i wybór wykresów w prostym trybie interaktywnym.

---

## Najważniejsze funkcje

- Automatyczne wykrywanie kodowania pliku.
- Unikanie wielokrotnego filtrowania po tej samej kolumnie.
- Automatyczny wybór pliku .csv z katalogu.
- Intuicyjny kreator wykresów.
- Generowanie raportu PDF z poprawnymi polskimi znakami.
- Obsługa zarówno trybu interaktywnego, jak i automatycznego (przez plik `config.yaml`).

---

## Generowanie wykresu udziału wybranych wartości na tle całości

Jedną z kluczowych funkcji PyReport jest **możliwość tworzenia wykresów prezentujących udział dowolnych wybranych wartości z wybranej kolumny na tle wszystkich rekordów**. To pozwala np. zobaczyć udział studentów z Warszawy, Krakowa i Poznania na tle całej bazy.

### Jak skorzystać z tej funkcji?

1. **Uruchom program w trybie interaktywnym:**

    ```bash
    python main.py
    ```

2. **Po załadowaniu danych pojawi się pytanie:**

    ```
    Czy chcesz utworzyć specjalny wykres udziału wybranych wartości na tle wszystkich? (y/n)
    ```

    Wpisz `y` i naciśnij ENTER, aby skorzystać z tej funkcji.

3. **Wybierz kolumnę do analizy** (np. miasto, produkt):

    Zobaczysz listę kolumn, np.:

    ```
    0: nr_indeksu (typ: int64)
    1: miasto (typ: object)
    2: wydział (typ: object)
    3: imię (typ: object)
    ...
    ```

    Podaj **numer kolumny** (np. `1` dla "miasto") i naciśnij ENTER.

4. **Zobaczysz listę unikalnych wartości w tej kolumnie, np.:**

    ```
    0: Warszawa
    1: Kraków
    2: Wrocław
    3: Łódź
    4: Gdańsk
    ...
    ```

    **Podaj numery wybranych wartości oddzielone przecinkami** (np. `0,4,7`), aby wybrać konkretne miasta/produkty/osoby, które mają być wyodrębnione na wykresie.  
    Pozostałe rekordy zostaną automatycznie oznaczone jako "Inne".

5. **Program wygeneruje wykres kołowy** (pie chart) z udziałami wybranych wartości oraz grupą "Inne".  
   Plik z wykresem zostanie zapisany w katalogu `charts/`, np.:

    ```
    charts/chart_udzial_miasto.png
    ```

6. **Po utworzeniu wykresu możesz generować także inne wykresy** (słupkowe, liniowe, kołowe) według standardowych opcji programu.

---

### Przykład użycia

Aby zobaczyć **udział Warszawy, Bydgoszczy, Szczecina, Lublina i Poznania na tle wszystkich studentów**:

- Po wybraniu kolumny `miasto`, podaj numery tych miast, np. `0,4,8,7,5`  
  *(numery mogą się różnić w Twoim pliku!)*.
- Otrzymasz wykres z sześcioma fragmentami: **Warszawa, Bydgoszcz, Szczecin, Lublin, Poznań, Inne**.

---

### Dodatkowe uwagi

- Funkcja działa z każdą kolumną – możesz sprawdzić udział dowolnych wybranych wartości (np. wydziałów, produktów).
- Wygenerowane wykresy zapisują się do katalogu `charts/`.
- Jeśli nie chcesz korzystać z tej funkcji, po prostu wpisz `n` na pierwszym pytaniu.

---

## Kontakt / wsparcie

W razie pytań, błędów lub sugestii – kontaktuj się z zespołem projektu na GitHubie lub przez e-mail.

---

## Autorzy

- Krzysztof Wojtkowiak
- Adam Pajer
