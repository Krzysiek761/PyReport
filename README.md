# PyReport – Interaktywny generator raportów z plików CSV

## Opis projektu

**PyReport** to rozbudowane narzędzie do analizy danych, które umożliwia:
- interaktywne filtrowanie i sortowanie danych z plików `.csv`,
- generowanie wykresów (słupkowych, liniowych i kołowych) zarówno manualnie, jak i na podstawie pliku konfiguracyjnego,
- eksport gotowego raportu do pliku PDF (z tabelą i wykresami, z obsługą polskich znaków),
- automatyzację pracy dzięki obsłudze konfiguracji oraz integracji z narzędziami do CI/CD.

Projekt obsługuje **dowolne pliki CSV** – nie wymaga modyfikacji kodu przy analizie nowych danych.

---

## Technologie i automatyzacje

- **Python 3.8+**
- **Zarządzanie zależnościami i środowiskiem:** [Poetry](https://python-poetry.org/)
- **Formatowanie kodu:** [black](https://black.readthedocs.io/en/stable/)
- **Testy automatyczne:** pytest
- **Automatyzacja CI/CD:** GitHub Actions – automatyczne testowanie kodu przy każdym commicie/pull request (w pliku `.github/workflows/python-app.yml`)
- **Automatyzacja działania:** Możliwość uruchamiania programu z poziomu pliku konfiguracyjnego `config.yaml` (praca manualna i w pełni automatyczna)
- **Uruchamianie w chmurze:** Program działa na serwerze AWS EC2 (Ubuntu) – możliwość obsługi przez terminal SSH lub automatyczne zadania (np. CRON)

---

## Instalacja

1. **Klonowanie repozytorium i instalacja zależności przez Poetry:**

    ```bash
    git clone https://github.com/TWOJA-NAZWA-REPO/PyReport.git
    cd PyReport
    poetry install
    ```

    *(Alternatywnie: `pip install pandas matplotlib fpdf` dla instalacji ręcznej.)*

2. **Przygotowanie środowiska:**
   - Upewnij się, że w katalogu projektu znajdują się pliki:
     - `main.py`
     - `csv_utils.py`
     - `charts.py`
     - `report.py`
     - `config.yaml` (opcjonalnie – do pracy automatycznej)
     - plik czcionki **DejaVuSans.ttf** (w tym samym folderze co `report.py`!)

3. **Przygotuj katalog `test_data` z plikami CSV do analizy.**
   - Każdy plik `.csv` może mieć inne kolumny i kodowanie (obsługa automatyczna).

---

## Uruchomienie programu

- W trybie interaktywnym (manualnym):

    ```bash
    poetry run python main.py
    ```
    lub
    ```bash
    python main.py
    ```

- W trybie automatycznym (po przygotowaniu `config.yaml`):

    ```bash
    poetry run python main.py --config config.yaml
    ```
    *(wspiera automatyczną analizę, generowanie wykresów i raportów bez pytań do użytkownika)*

---

## Formatowanie kodu

Aby zapewnić jednolity styl kodu, używaj narzędzia [black](https://black.readthedocs.io/en/stable/):

```bash
poetry run black
``` 

## Testy Automatyczne

Testy jednostkowe uruchomisz komendą:
````
poetry run pytest
````

## CI/CD – GitHub Actions
Repozytorium posiada skonfigurowany plik workflow (.github/workflows/python-app.yml), który:

- automatycznie formatuje i testuje kod po każdym commicie/pull request,

- ułatwia kontrolę jakości oraz wdrożenia.

## Automatyzacja na AWS EC2

PyReport może być uruchamiany na serwerze Ubuntu (np. AWS EC2) zarówno manualnie (po SSH), jak i w pełni automatycznie (np. przez CRON, w połączeniu z ```config.yaml```).
Dzięki temu możliwe jest automatyczne generowanie raportów cyklicznych.

## Kontakt/Wsparcie 
Kontakt / wsparcie

W razie pytań, błędów lub sugestii – skontaktuj się z zespołem projektu na GitHubie lub przez e-mail.

## Autorzy 
- Krzysztof Wojtkowiak 
- Adam Pajer