# Instrukcja obsługi pliku `config.yaml` i funkcji programu PyReport

## 1. Czym jest plik `config.yaml`?

Plik `config.yaml` pozwala na **automatyczne, bezobsługowe uruchomienie programu PyReport**. Dzięki niemu możesz:
- wybrać plik lub katalog do analizy,
- ustalić filtrowanie i sortowanie danych,
- automatycznie wygenerować wybrane wykresy,
- zdefiniować ścieżki katalogów do wykresów i raportów,
- pominąć interaktywne pytania i uzyskać pełny raport jednym poleceniem.

---

## 2. Przykładowy plik `config.yaml`

```yaml
# Przykład pliku konfiguracyjnego do PyReport

input_dir: test_data                # katalog z plikami CSV
input_file: sprzedaz_produkty.csv   # pojedynczy plik do przetworzenia (opcjonalnie)
encoding: utf-8

# Automatyczne filtrowanie (opcjonalnie)
filters:
  - column: "Kategoria"
    op: "=="
    value: "Elektronika"

# Automatyczne sortowanie (opcjonalnie)
sort:
  column: "Cena"
  order: "desc"     # "asc" (rosnąco) lub "desc" (malejąco)

# Automatyczne wykresy (opcjonalnie)
charts:
  - type: "bar"
    columns: ["Kategoria"]
  - type: "line"
    columns: ["Produkt", "Sprzedaż"]
  - type: "pie"
    columns: ["Kategoria"]

# Opcje trybu automatycznego
interactive_filter: false
interactive_sort: false
interactive_choose_file: false
interactive_charts: false

# Ścieżki katalogów do zapisów
charts_dir: charts
reports_dir: reports
```

## 3. Opcje dostępne w config.yaml – wyjaśnienie

- ```input_dir``` – katalog, w którym szukane są pliki .csv
- ```input_file``` – pojedynczy plik CSV do przetworzenia (jeśli nie podano, analizowane są wszystkie pliki z katalogu)
- ```encoding``` – wymuszony sposób odczytu pliku (domyślnie program wykrywa automatycznie)
-```filters``` – lista filtrów (każdy filtr: nazwa kolumny, operator, wartość)

        Obsługiwane operatory: ==, !=, >, <, >=, <=

- ```sort``` – sposób sortowania (kolumna, kolejność)
- ```charts``` – lista wykresów do wygenerowania (patrz niżej)

        type: "bar", "line", "pie"

        columns: lista kolumn do użycia w wykresie

- ```interactive_filter``` – wyłączyć pytania o filtr? (false = pełna automatyzacja)
- ```interactive_sort``` – wyłączyć pytania o sortowanie?
- ```interactive_choose_file``` – automatycznie wybrać plik, nie pytać użytkownika?
- ```interactive_charts``` – automatycznie generować wykresy według configa, bez pytań?

## 4. Automatyczne generowanie specjalnych wykresów udziału wartości na tle całości

Od wersji 2024.07, program pozwala na automatyczne utworzenie wykresu kołowego (pie chart), który przedstawia udział wybranych wartości z dowolnej kolumny na tle całości.
Przykład użycia w pliku konfiguracyjnym:
```
special_pie:
  column: "Kategoria"
  values: ["Elektronika", "AGD"]   # te wartości będą wydzielone na wykresie, reszta jako "Inne"
  filename: "chart_udzial_kategorie.png"   # (opcjonalnie)
```

Efektem będzie wykres, na którym widać udział wybranych kategorii (np. "Elektronika", "AGD") na tle wszystkich rekordów.

## 5. Uruchomienie programu z plikiem konfiguracyjnym

Aby uruchomić program w trybie w pełni automatycznym, użyj polecenia:
```
python main.py --config config.yaml
```
lub
```
poetry run python main.py --config config.yaml
```


