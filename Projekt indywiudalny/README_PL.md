# Problem Ucztujących Filozofów

## Przegląd Projektu

Ten projekt implementuje rozwiązanie klasycznego problemu współbieżności znanego jako "Ucztujący Filozofowie", w którym wiele wątków (filozofów) konkuruje o ograniczone zasoby (pałeczki). Implementacja wykorzystuje niestandardowe prymitywy synchronizacji, w tym mutexy i semafory oparte na operacjach atomowych, aby zapobiec sytuacjom zakleszczenia i zagłodzenia.

## Opis Problemu

Problem Ucztujących Filozofów, sformułowany przez E.W. Dijkstrę w 1965 roku, jest fundamentalnym przykładem ilustrującym problemy synchronizacji w programowaniu współbieżnym:

- N filozofów siedzi wokół okrągłego stołu
- Każdy filozof na przemian myśli i je
- Filozof potrzebuje dwóch pałeczek (lewej i prawej) do jedzenia
- Na stole znajduje się dokładnie N pałeczek, po jednej między każdą parą filozofów

Kluczowe wyzwania, które rozwiązuje ten problem:

- **Zakleszczenie (Deadlock)**: Sytuacja, w której wszyscy filozofowie trzymają jedną pałeczkę i czekają w nieskończoność na drugą
- **Zagłodzenie (Starvation)**: Sytuacja, w której jeden lub więcej filozofów nigdy nie ma możliwości jedzenia
- **Postęp**: Zapewnienie, że system jako całość nadal robi postępy
- **Wykorzystanie zasobów**: Maksymalizacja współbieżnego wykorzystania zasobów przy zachowaniu bezpieczeństwa

## Implementacja Techniczna

### 1. Implementacja Mutexa (Mutex.hpp)

#### Projekt

Klasa `Mutex` implementuje mechanizm wzajemnego wykluczania oparty na blokadzie wirującej (spin-lock) przy użyciu operacji atomowych:

```cpp
class Mutex {
private:
    atomic_flag lockState = ATOMIC_FLAG_INIT;
public:
    void lock();
    void unlock();
};
```

#### Szczegóły Techniczne

- Używa `std::atomic_flag` jako podstawowego prymitywu synchronizacji
- Implementuje wzorzec TATAS (Test-And-Test-And-Set) dla zwiększenia wydajności
- Ograniczenia dotyczące porządkowania pamięci:
  - `memory_order_acquire` dla pozyskania blokady
  - `memory_order_release` dla zwolnienia blokady
- Używa `this_thread::yield()` w celu zmniejszenia zużycia CPU podczas rywalizacji o zasób

#### Charakterystyka Wydajności

- Niski narzut dla nieobciążonych blokad
- Aktywne oczekiwanie podczas rywalizacji (łagodzone przez ustępowanie wątku)
- Brak zarządzania kolejką dla oczekujących wątków (potencjalnie nieoptymalne przy wysokiej rywalizacji)

### 2. Implementacja Semafora (Semaphore.hpp)

#### Projekt

Klasa `Semaphore` implementuje semafor licznikowy przy użyciu operacji atomowych:

```cpp
class Semaphore {
private:
    atomic<int> resourceCount;
public:
    explicit Semaphore(int initialCount);
    void wait();
    void signal();
};
```

#### Szczegóły Techniczne

- Używa `std::atomic<int>` do śledzenia dostępnych zasobów
- Implementuje atomowe zmniejszanie z `compare_exchange_weak` dla operacji oczekiwania
- Używa `fetch_add` dla operacji sygnalizujących
- Ograniczenia dotyczące porządkowania pamięci:
  - `memory_order_acquire` dla pozyskania zasobu
  - `memory_order_release` dla zwolnienia zasobu
- Aktywne oczekiwanie z ustępowaniem podczas rywalizacji

#### Analiza Algorytmiczna

- Operacja `wait()` wykorzystuje algorytm bez blokad, który unika tradycyjnego blokowania opartego na mutexach
- Implementacja zachowuje odpowiednie gwarancje porządkowania pamięci dla synchronizacji wątków
- Brak jawnego zarządzania kolejką dla oczekujących wątków

### 3. Implementacja Głównego Programu (so2_1.cpp)

#### Model Współbieżności

Program tworzy N współbieżnych wątków filozofów, z których każdy implementuje następujący cykl życia:

1. Myślenie (uśpienie na pewien czas)
2. Próba uzyskania dostępu do stołu za pomocą semafora
3. Pozyskanie pałeczek zgodnie z protokołem pozyskiwania zasobów
4. Jedzenie (uśpienie na pewien czas)
5. Zwolnienie pałeczek
6. Zwolnienie dostępu do stołu za pomocą semafora

#### Mechanizmy Zapobiegania Zakleszczeniom

1. **Ograniczenie Zasobów**

   - Semafor ogranicza dostęp do stołu do co najwyżej (N-1) filozofów jednocześnie
   - Dowód matematyczny: Przy N filozofach i N pałeczkach, ograniczenie dostępu do stołu do (N-1) filozofów zapewnia, że co najmniej jeden filozof zawsze może pozyskać obie pałeczki

   ```cpp
   Semaphore diningTable(NUM_PHILOSOPHERS - 1);
   ```

2. **Asymetryczne Pozyskiwanie Zasobów**

   - Filozofowie o parzystych numerach najpierw pozyskują lewą pałeczkę, a następnie prawą
   - Filozofowie o nieparzystych numerach najpierw pozyskują prawą pałeczkę, a następnie lewą
   - To przerywa warunek cyklicznego oczekiwania (jeden z niezbędnych warunków zakleszczenia)

   ```cpp
   if (id % 2 == 0) {
       leftChopstick.lock();
       rightChopstick.lock();
   } else {
       rightChopstick.lock();
       leftChopstick.lock();
   }
   ```

3. **Kolejność Zwalniania Zasobów**
   - Zasoby są zawsze zwalniane w odwrotnej kolejności do pozyskiwania
   - Minimalizuje to potencjał sytuacji zagłodzenia

#### Bezpieczne Logowanie Wątków

- Dedykowany mutex chroni operacje wyjścia na konsolę
- Zapewnia atomowe drukowanie komunikatów dziennika, zapobiegając przeplataniu wyjścia
- Zaimplementowane jako sekcja krytyczna o minimalnym czasie trwania

```cpp
void printLog(const string& message) {
    printMutex.lock();
    cout << message << endl;
    printMutex.unlock();
}
```

#### Zarządzanie Zasobami

- Jawne łączenie wątków zapewnia właściwe czyszczenie i unika wycieków zasobów
- Ustrukturyzowana synchronizacja zapobiega warunkom wyścigu na współdzielonych zasobach
- Ograniczone iteracje na filozofa umożliwiają deterministyczny czas wykonania

## Poprawność Algorytmiczna

### Właściwości Bezpieczeństwa

1. **Wzajemne Wykluczanie**: Każda pałeczka może być trzymana tylko przez jednego filozofa na raz (wymuszane przez mutex)
2. **Wolność od Zakleszczenia**: System nie może osiągnąć stanu, w którym wszyscy filozofowie są zablokowani bezterminowo
3. **Wolność od Zagłodzenia**: Każdy filozof, który chce jeść, ostatecznie będzie mógł jeść

### Właściwości Żywotności

1. **Ograniczone Oczekiwanie**: Istnieje górne ograniczenie liczby przypadków, kiedy inni filozofowie mogą jeść, zanim głodny filozof będzie mógł jeść
2. **Sprawiedliwość**: Implementacja nie zapewnia ścisłych gwarancji sprawiedliwości, ale opiera się na sprawiedliwości planowania wątków przez system operacyjny

## Względy Wydajnościowe

### Operacje Atomowe

- Implementacja opiera się głównie na operacjach atomowych, które zapewniają współbieżność bez blokad
- Operacje atomowe mają mniejszy narzut niż tradycyjne blokady, ale mogą powodować odbijanie linii pamięci podręcznej podczas rywalizacji

### Aktywne Oczekiwanie

- Obie implementacje mutexa i semafora wykorzystują aktywne oczekiwanie z ustępowaniem
- To podejście jest wydajne dla krótkotrwałych sekcji krytycznych, ale może być intensywne dla CPU przy wysokiej rywalizacji

### Skalowalność

- Rozwiązanie dobrze skaluje się do kilkudziesięciu filozofów
- Powyżej tego, podejście aktywnego oczekiwania może prowadzić do zwiększonej rywalizacji i zmniejszonej wydajności

## Kompilacja i Wykonanie na Linuxie

### Wymagania Budowy

- Kompilator C++11 lub nowszy (GCC 4.8+ lub Clang 3.3+)
- Wsparcie wątków zgodne z POSIX
- Wsparcie biblioteki standardowej dla operacji atomowych
- Jądro Linux 2.6 lub nowsze

### Kompilacja

```bash
# Podstawowa kompilacja z optymalizacją
g++ -std=c++11 -pthread so2_1.cpp -o dining_philosophers -O2

# Szczegółowa kompilacja z dodatkowymi ostrzeżeniami
g++ -std=c++11 -pthread so2_1.cpp -o dining_philosophers -O2 -Wall -Wextra -pedantic

# Używanie Clang zamiast GCC
clang++ -std=c++11 -pthread so2_1.cpp -o dining_philosophers -O2
```

### Szczegóły Linkowania

Flaga `-pthread` robi dwie rzeczy:

1. Dodaje `-lpthread` do flag linkera, aby linkować z biblioteką pthread
2. Definiuje makro preprocesora `_REENTRANT`, które włącza warianty funkcji biblioteki standardowej bezpieczne dla wątków

Do ręcznego linkowania możesz użyć:

```bash
g++ -std=c++11 -c so2_1.cpp -O2
g++ so2_1.o -o dining_philosophers -lpthread
```

### Wykonanie

```bash
# Podstawowe wykonanie
./dining_philosophers

# Uruchomienie z wyższym priorytetem
nice -n -10 ./dining_philosophers

# Przekierowanie wyjścia do pliku
./dining_philosophers > execution_log.txt

# Pomiar czasu wykonania
time ./dining_philosophers
```

### Oczekiwane Wyjście

Program generuje ślad działań filozofów, pokazując następujące przejścia stanów:

- Myślenie
- Podnoszenie pałeczek (lewej i prawej)
- Jedzenie
- Odkładanie pałeczek (lewej i prawej)

Przykładowy fragment wyjścia:

```
Philosopher 6 is thinking.
Philosopher 1 is thinking.
Philosopher 2 is thinking.
Philosopher 3 is thinking.
Philosopher 9 is thinking.
Philosopher 5 is thinking.
Philosopher 7 is thinking.
Philosopher 4 is thinking.
Philosopher 0 is thinking.
Philosopher 8 is thinking.
Philosopher 4 is picking up left chopstick (chopstick 4).
Philosopher 6 is picking up left chopstick (chopstick 6).
Philosopher 8 is picking up left chopstick (chopstick 8).
...
```

**Uwaga**: Ze względu na współbieżny charakter programu, dokładna kolejność operacji będzie się różnić między uruchomieniami. Jest to normalne zachowanie dla programów wielowątkowych, ponieważ planowanie wątków jest zarządzane przez system operacyjny.

Rzeczywiste wyjście nie pokazuje jawnie stanów "Oczekiwanie na dostęp do stołu" lub "Zwalnianie dostępu do stołu", ponieważ są one obsługiwane wewnętrznie przez semafor bez logowania. Zamiast tego, widoczne wyjście koncentruje się na stanie myślenia filozofa, pozyskiwaniu i zwalnianiu pałeczek oraz stanie jedzenia.

Ważne jest, aby zaobserwować w wyjściu, że:

1. Nie występują zakleszczenia (program nadal robi postępy)
2. Żaden filozof nie może używać pałeczek, które są już w użyciu (wzajemne wykluczanie jest zachowane)
3. Wszyscy filozofowie ostatecznie mogą jeść (brak zagłodzenia)
4. Asymetryczna strategia pozyskiwania pałeczek jest przestrzegana (filozofowie o parzystych numerach najpierw podnoszą lewą pałeczkę, o nieparzystych najpierw prawą)

## Analiza Teoretyczna

### Złożoność Czasowa

- Każdy filozof ma złożoność czasową O(1) dla operacji pozyskiwania i zwalniania zasobów
- Ogólna przepustowość systemu zależy od poziomów rywalizacji i planowania systemu operacyjnego

### Złożoność Przestrzenna

- O(N) przestrzeni dla N filozofów i N pałeczek
- Każdy wątek wymaga dodatkowej przestrzeni O(1) na stos i zmienne lokalne

### Analiza Rywalizacji

- Semafor ograniczający dostęp do stołu do (N-1) filozofów tworzy wąskie gardło
- To wąskie gardło jest niezbędnym kompromisem, aby zapobiec zakleszczeniu
- Asymetryczne pozyskiwanie zasobów pomaga bardziej równomiernie rozłożyć rywalizację

## Bibliografia

1. Dijkstra, E.W. (1965). "Cooperating sequential processes." Raport Techniczny EWD-123.
2. Coffman, E.G., Elphick, M., and Shoshani, A. (1971). "System Deadlocks." Computing Surveys, 3(2).
3. Herlihy, M., and Shavit, N. (2008). "The Art of Multiprocessor Programming." Morgan Kaufmann.
4. C++ Standard, ISO/IEC 14882:2011, Sekcja 29: "Atomic operations library."
