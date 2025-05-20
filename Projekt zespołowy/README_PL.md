# Aplikacja Czatu

## Przegląd Projektu

Ten projekt implementuje prostą aplikację czatową typu klient-serwer z interfejsem graficznym. Umożliwia wielu użytkownikom łączenie się z centralnym serwerem, rejestrację/logowanie oraz wymianę wiadomości w wspólnym "pokoju czatowym". Implementacja wykorzystuje programowanie gniazd (sockets) do komunikacji sieciowej oraz Tkinter do interfejsu graficznego.

## Spis Treści

- [Aplikacja Czatu](#aplikacja-czatu)
  - [Przegląd Projektu](#przegląd-projektu)
  - [Spis Treści](#spis-treści)
  - [Funkcje](#funkcje)
  - [Architektura](#architektura)
  - [Implementacja Techniczna](#implementacja-techniczna)
    - [Implementacja Serwera](#implementacja-serwera)
      - [Kluczowe Komponenty:](#kluczowe-komponenty)
    - [Implementacja Klienta](#implementacja-klienta)
      - [Kluczowe Komponenty:](#kluczowe-komponenty-1)
    - [Wątki i Synchronizacja](#wątki-i-synchronizacja)
      - [Wątki po Stronie Serwera:](#wątki-po-stronie-serwera)
      - [Wątki po Stronie Klienta:](#wątki-po-stronie-klienta)
    - [Protokół Komunikacyjny](#protokół-komunikacyjny)
  - [Interfejs Użytkownika](#interfejs-użytkownika)
  - [Budowanie i Uruchamianie](#budowanie-i-uruchamianie)
    - [Wymagania](#wymagania)
    - [Uruchamianie Serwera](#uruchamianie-serwera)
    - [Uruchamianie Klienta](#uruchamianie-klienta)

## Funkcje

- **Uwierzytelnianie Użytkowników**: System logowania i rejestracji
- **Wiadomości w Czasie Rzeczywistym**: Natychmiastowe dostarczanie wiadomości do wszystkich połączonych użytkowników
- **Nowoczesny Interfejs**: Inspirowany Telegramem/WhatsAppem interfejs z dymkami wiadomości
- **Formatowanie Wiadomości**: Różne style dla wysłanych, odebranych i systemowych wiadomości
- **Status Połączenia**: Powiadomienia o dołączaniu i opuszczaniu czatu przez użytkowników
- **Znaczniki Czasu**: Każda wiadomość wyświetla czas wysłania
- **Wielowątkowość**: Obsługuje wiele połączeń klientów jednocześnie

## Architektura

Aplikacja opiera się na architekturze klient-serwer:

1. **Serwer**:

   - Zarządza połączeniami klientów
   - Obsługuje uwierzytelnianie użytkowników
   - Rozsyła wiadomości do połączonych klientów
   - Utrzymuje informacje o stanie użytkowników

2. **Klient**:
   - Zapewnia interfejs graficzny do interakcji z użytkownikiem
   - Zarządza połączeniem z serwerem
   - Wysyła i odbiera wiadomości
   - Formatuje i wyświetla treść czatu

## Implementacja Techniczna

### Implementacja Serwera

**Plik**: `server.py`

Komponent serwerowy obsługuje wiele połączeń klientów, uwierzytelnianie użytkowników i rozsyłanie wiadomości, wykorzystując wątki do współbieżności.

#### Kluczowe Komponenty:

1. **Zarządzanie Użytkownikami**:

   - Przechowuje dane uwierzytelniające użytkowników w pliku tekstowym (`users.txt`)
   - Implementuje funkcje do wczytywania użytkowników (`load_users()`) i zapisywania nowych użytkowników (`save_user()`)
   - Uwierzytelnia użytkowników na podstawie przechowywanych danych lub rejestruje nowych użytkowników

2. **Obsługa Współbieżności**:

   - Każde połączenie klienta jest obsługiwane w osobnym wątku za pomocą `threading.Thread()`
   - Operacje bezpieczne dla wątków z użyciem blokad mutex (`threading.Lock()`)
   - Wątki demona do automatycznego czyszczenia po zakończeniu głównego programu

3. **Rozsyłanie Wiadomości**:

   - Centralna funkcja `broadcast()` dystrybuuje wiadomości do wszystkich połączonych klientów
   - Zarządzanie listą klientów bezpieczne dla wątków dzięki blokadzie mutex
   - Automatyczne czyszczenie rozłączonych klientów podczas prób rozsyłania

4. **Programowanie Gniazd**:
   - Wykorzystuje gniazda TCP (`socket.SOCK_STREAM`) dla niezawodnego dostarczania wiadomości
   - Wiąże się ze wszystkimi interfejsami sieciowymi (`0.0.0.0`), aby akceptować zdalne połączenia
   - Implementuje blokujące accept() w głównym wątku z obsługą klienta w osobnych wątkach

### Implementacja Klienta

**Plik**: `client.py`

Klient zapewnia interfejs graficzny do interakcji użytkowników z serwerem czatu, obsługując zarówno wysyłanie, jak i odbieranie wiadomości asynchronicznie.

#### Kluczowe Komponenty:

1. **Interfejs Uwierzytelniania**:

   - Implementuje modalne okno logowania za pomocą `Toplevel` z Tkinter
   - Komunikuje się z serwerem w celu weryfikacji danych uwierzytelniających
   - Obsługuje sukces/niepowodzenie logowania z odpowiednim feedbackiem UI

2. **Interfejs Czatu**:

   - Wykorzystuje `Canvas` Tkinter z paskiem przewijania do elastycznego wyświetlania wiadomości
   - Implementuje niestandardowe ramki wiadomości dla różnych typów wiadomości
   - Utrzymuje właściwy układ z dynamicznym zmienianiem rozmiaru

3. **Komunikacja Sieciowa**:

   - Wykorzystuje gniazda TCP dla niezawodnego połączenia z serwerem
   - Implementuje nieblokujące operacje odbierania w wątku działającym w tle
   - Wysyłanie wiadomości sterowane zdarzeniami z wątku UI

4. **Projekt Wizualny**:
   - Niestandardowo stylizowane elementy UI za pomocą widżetów Tkinter
   - Dymki wiadomości o różnych kolorach w zależności od nadawcy
   - Responsywny układ dostosowujący się do zmian rozmiaru okna

### Wątki i Synchronizacja

#### Wątki po Stronie Serwera:

1. **Wątek Główny**:

   - Inicjalizuje gniazdo serwera i wiąże z portem
   - Akceptuje przychodzące połączenia klientów
   - Tworzy wątki obsługujące dla każdego nowego połączenia

2. **Wątki Obsługi Klientów**:

   - Jeden wątek na podłączonego klienta (tworzony przez `threading.Thread()`)
   - Obsługuje uwierzytelnianie, odbieranie wiadomości i rozłączanie klienta
   - Działa jako wątki demona (`daemon=True`) dla automatycznego czyszczenia

3. **Synchronizacja Wątków**:

   - Wykorzystuje globalny obiekt `threading.Lock()` do ochrony współdzielonych zasobów
   - Sekcje krytyczne chronione za pomocą `lock.acquire()` i `lock.release()` (poprzez menedżer kontekstu `with lock:`)
   - Zsynchronizowany dostęp do współdzielonego słownika klientów
   - Bezpieczne dla wątków rozsyłanie wiadomości do wszystkich klientów

4. **Zarządzanie Zasobami**:
   - Bezpieczne usuwanie klienta ze współdzielonego słownika po rozłączeniu
   - Czyszczenie gniazd w obsługach wyjątków i blokach finally
   - Iteracja po kopii słownika klientów, aby uniknąć modyfikacji podczas iteracji

#### Wątki po Stronie Klienta:

1. **Wątek Główny (Wątek UI)**:

   - Obsługuje pętlę zdarzeń Tkinter (`root.mainloop()`)
   - Zarządza aktualizacjami interfejsu użytkownika
   - Przetwarza dane wejściowe użytkownika i wysyła wiadomości

2. **Wątek Odbiorczy**:

   - Dedykowany wątek tła do odbierania wiadomości (`threading.Thread(target=self.receive_messages)`)
   - Nieblokujące odbieranie wiadomości
   - Aktualizuje UI za pomocą operacji Tkinter bezpiecznych dla wątków
   - Działa jako wątek demona, aby uniknąć blokowania wyjścia z aplikacji

3. **Koordynacja Wątków**:
   - Aktualizacje UI wywoływane z wątku odbiorczego wykorzystują metody Tkinter bezpieczne dla wątków
   - Automatyczne przewijanie do najnowszych wiadomości koordynowane między wątkami
   - Obsługa wyjątków w celu eleganckie zarządzania błędami sieciowymi

### Protokół Komunikacyjny

Klient i serwer komunikują się za pomocą prostego protokołu tekstowego:

1. **Proces Uwierzytelniania**:

   - Serwer wysyła zapytanie "Login:"
   - Klient odpowiada nazwą użytkownika
   - Serwer wysyła zapytanie "Hasło:"
   - Klient odpowiada hasłem
   - Serwer odpowiada komunikatem o sukcesie/niepowodzeniu

2. **Format Wiadomości**:

   - Regularne wiadomości: `[HH:MM:SS] username: message`
   - Powiadomienia systemowe: wiadomości zwykłym tekstem

3. **Zarządzanie Połączeniem**:

   - Rozłączenie socketu uruchamia procedury czyszczące
   - Serwer rozsyła wydarzenia dołączania/opuszczania do wszystkich klientów

4. **Przechowywanie Haseł**:

   - Hasła są obecnie przechowywane w formie jawnego tekstu
   - Brak implementacji szyfrowania dla transmisji danych

5. **Walidacja Danych Wejściowych**:

   - Ograniczona walidacja danych wprowadzanych przez użytkownika
   - Brak ochrony przed zalewaniem wiadomościami lub spamem

6. **Obsługa Błędów**:
   - Podstawowe komunikaty błędów dla problemów z połączeniem
   - Ograniczona ochrona przed zniekształconymi wiadomościami

## Interfejs Użytkownika

Aplikacja kliencka oferuje nowoczesny, inspirowany urządzeniami mobilnymi interfejs czatu:

1. **Okno Logowania**:

   - Czysty, prosty formularz z polami na nazwę użytkownika i hasło
   - Informacje zwrotne o błędach dla nieudanych prób uwierzytelniania

2. **Okno Czatu**:
   - Nagłówek pokazujący informacje o pokoju i status użytkownika
   - Obszar wiadomości z różnymi stylami dymków:
     - Wyrównane do prawej zielone dymki dla wysłanych wiadomości
     - Wyrównane do lewej białe dymki dla odebranych wiadomości
     - Wyśrodkowany szary tekst dla powiadomień systemowych
   - Obszar wprowadzania z polem tekstowym i przyciskiem wysyłania
   - Automatyczne przewijanie do najnowszych wiadomości

## Budowanie i Uruchamianie

### Wymagania

- Python 3.6 lub nowszy
- Biblioteka Tkinter (zwykle dołączona do Pythona)
- Łączność sieciowa między serwerem a klientami

### Uruchamianie Serwera

1. Otwórz terminal/wiersz poleceń
2. Przejdź do katalogu projektu
3. Uruchom serwer:
   ```
   python server.py
   ```
4. Serwer uruchomi się i wyświetli komunikat informujący o jego działaniu

### Uruchamianie Klienta

1. Otwórz terminal/wiersz poleceń
2. Przejdź do katalogu projektu
3. Uruchom klienta:
   ```
   python client.py
   ```
4. Pojawi się okno logowania
5. Wprowadź nazwę użytkownika i hasło, aby się zalogować lub zarejestrować
6. Po pomyślnym uwierzytelnieniu pojawi się interfejs czatu

**Uwaga**: Klient jest domyślnie skonfigurowany do łączenia się z `localhost`. Aby połączyć się z zewnętrznym serwerem, zmodyfikuj zmienną `HOST` w kodzie klienta.
