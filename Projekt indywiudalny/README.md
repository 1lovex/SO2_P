# Dining Philosophers Problem

## Project Overview

This project implements a solution to the classic concurrency problem known as the "Dining Philosophers," where multiple threads (philosophers) compete for limited resources (chopsticks). The implementation utilizes custom-built synchronization primitives including atomic-based mutexes and semaphores to prevent deadlock and starvation scenarios.

## Problem Description

The Dining Philosophers problem, formulated by E.W. Dijkstra in 1965, is a fundamental example illustrating synchronization issues in concurrent programming:

- N philosophers sit around a circular table
- Each philosopher alternates between thinking and eating
- A philosopher needs two chopsticks (left and right) to eat
- There are exactly N chopsticks on the table, one between each pair of philosophers

The key challenges addressed by this problem:

- **Deadlock**: A situation where all philosophers hold one chopstick and wait indefinitely for another
- **Starvation**: A situation where one or more philosophers never get to eat
- **Progress**: Ensuring that the system as a whole continues to make forward progress
- **Resource Utilization**: Maximizing concurrent resource usage while maintaining safety

## Technical Implementation

### 1. Mutex Implementation (Mutex.hpp)

#### Design

The `Mutex` class implements a spin-lock based mutual exclusion mechanism using atomic operations:

```cpp
class Mutex {
private:
    atomic_flag lockState = ATOMIC_FLAG_INIT;
public:
    void lock();
    void unlock();
};
```

#### Technical Details

- Uses `std::atomic_flag` as the underlying synchronization primitive
- Implements the TATAS (Test-And-Test-And-Set) pattern for efficiency
- Memory ordering constraints:
  - `memory_order_acquire` for lock acquisition
  - `memory_order_release` for lock release
- Uses `this_thread::yield()` to reduce CPU consumption during contention

#### Performance Characteristics

- Low overhead for uncontended locks
- Busy-waiting during contention (mitigated by thread yielding)
- No queue management for waiting threads (potentially unfair under high contention)

### 2. Semaphore Implementation (Semaphore.hpp)

#### Design

The `Semaphore` class implements a counting semaphore using atomic operations:

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

#### Technical Details

- Uses `std::atomic<int>` to track available resources
- Implements atomic decrement with `compare_exchange_weak` for wait operations
- Uses `fetch_add` for signal operations
- Memory ordering constraints:
  - `memory_order_acquire` for resource acquisition
  - `memory_order_release` for resource release
- Busy-waiting with yielding during contention

#### Algorithmic Analysis

- The `wait()` operation uses a lock-free algorithm that avoids traditional mutex-based blocking
- The implementation maintains proper memory ordering guarantees for thread synchronization
- No explicit queue management for waiting threads

### 3. Main Program Implementation (so2_1.cpp)

#### Concurrency Model

The program creates N concurrent philosopher threads, each implementing the following lifecycle:

1. Think (sleep for a random duration)
2. Attempt to acquire table access via semaphore
3. Acquire chopsticks according to resource acquisition protocol
4. Eat (sleep for a random duration)
5. Release chopsticks
6. Release table access via semaphore

#### Deadlock Prevention Mechanisms

1. **Resource Limitation**

   - A semaphore limits table access to at most (N-1) philosophers simultaneously
   - Mathematical proof: With N philosophers and N chopsticks, limiting table access to (N-1) philosophers ensures at least one philosopher can always acquire both chopsticks

   ```cpp
   Semaphore diningTable(NUM_PHILOSOPHERS - 1);
   ```

2. **Asymmetric Resource Acquisition**

   - Even-numbered philosophers acquire left chopstick first, then right
   - Odd-numbered philosophers acquire right chopstick first, then left
   - This breaks the circular wait condition (one of the necessary conditions for deadlock)

   ```cpp
   if (id % 2 == 0) {
       leftChopstick.lock();
       rightChopstick.lock();
   } else {
       rightChopstick.lock();
       leftChopstick.lock();
   }
   ```

3. **Resource Release Order**
   - Resources are always released in the reverse order of acquisition
   - This minimizes the potential for starvation scenarios

#### Thread-Safe Logging

- A dedicated mutex protects console output operations
- Ensures atomic printing of log messages, preventing interleaved output
- Implemented as a critical section with minimal duration

```cpp
void printLog(const string& message) {
    printMutex.lock();
    cout << message << endl;
    printMutex.unlock();
}
```

#### Resource Management

- Explicit thread joining ensures proper cleanup and avoids resource leaks
- Structured synchronization prevents race conditions on shared resources
- Limited iterations per philosopher enables deterministic execution time

## Algorithmic Correctness

### Safety Properties

1. **Mutual Exclusion**: Each chopstick can only be held by one philosopher at a time (enforced by mutex)
2. **Deadlock Freedom**: The system cannot reach a state where all philosophers are blocked indefinitely
3. **Starvation Freedom**: Every philosopher who wants to eat will eventually get to eat

### Liveness Properties

1. **Bounded Waiting**: There is an upper bound on the number of times other philosophers can eat before a hungry philosopher gets to eat
2. **Fairness**: The implementation does not provide strict fairness guarantees but relies on OS thread scheduling fairness

## Performance Considerations

### Atomic Operations

- The implementation relies heavily on atomic operations which provide lock-free concurrency
- Atomic operations have lower overhead than traditional locks but may cause cache-line bouncing under contention

### Busy-Waiting

- Both mutex and semaphore implementations use busy-waiting with yielding
- This approach is efficient for short-lived critical sections but can be CPU-intensive under high contention

### Scalability

- The solution scales reasonably well up to dozens of philosophers
- Beyond that, the busy-waiting approach may lead to increased contention and reduced performance

## Compilation and Execution on Linux

### Build Requirements

- C++11 or later compiler (GCC 4.8+ or Clang 3.3+)
- POSIX-compliant threading support
- Standard library support for atomics
- Linux kernel 2.6 or later

### Compilation

```bash
# Basic compilation with optimization
g++ -std=c++11 -pthread so2_1.cpp -o dining_philosophers -O2

# Verbose compilation with additional warnings
g++ -std=c++11 -pthread so2_1.cpp -o dining_philosophers -O2 -Wall -Wextra -pedantic

# Using Clang instead of GCC
clang++ -std=c++11 -pthread so2_1.cpp -o dining_philosophers -O2
```

### Linking Details

The `-pthread` flag does two things:

1. Adds `-lpthread` to the linker flags to link against the pthread library
2. Defines the preprocessor macro `_REENTRANT` which enables thread-safe variants of standard library functions

For manual linking, you can use:

```bash
g++ -std=c++11 -c so2_1.cpp -O2
g++ so2_1.o -o dining_philosophers -lpthread
```

### Execution

```bash
# Basic execution
./dining_philosophers

# Run with higher priority
nice -n -10 ./dining_philosophers

# Redirect output to a file
./dining_philosophers > execution_log.txt

# Measure execution time
time ./dining_philosophers
```

### Expected Output

The program produces a trace of philosopher activities, showing the following state transitions:

- Thinking
- Picking up chopsticks (left and right)
- Eating
- Putting down chopsticks (left and right)

Example output fragment:

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

**Note**: Due to the concurrent nature of the program, the exact order of operations will vary between runs. This is normal behavior for multithreaded programs, as thread scheduling is managed by the operating system.

The actual output does not explicitly show the "Waiting for table access" or "Releasing table access" states, as these are handled internally by the semaphore without logging. Instead, the visible output focuses on the philosopher's thinking state, chopstick acquisition and release, and eating state.

What's important to observe in the output is that:

1. No deadlocks occur (the program continues to make progress)
2. No philosopher can use chopsticks that are already in use (mutual exclusion is preserved)
3. All philosophers eventually get to eat (no starvation)
4. The asymmetric chopstick acquisition strategy is followed (even-numbered philosophers pick up left chopstick first, odd-numbered pick up right first)

## Theoretical Analysis

### Time Complexity

- Each philosopher has O(1) time complexity for resource acquisition and release operations
- The overall system throughput depends on the contention levels and operating system scheduling

### Space Complexity

- O(N) space for N philosophers and N chopsticks
- Each thread requires O(1) additional space for its stack and local variables

### Contention Analysis

- The semaphore limiting table access to (N-1) philosophers creates a bottleneck
- This bottleneck is a necessary trade-off to prevent deadlock
- Asymmetric resource acquisition helps distribute contention more evenly

## References

1. Dijkstra, E.W. (1965). "Cooperating sequential processes." Technical Report EWD-123.
2. Coffman, E.G., Elphick, M., and Shoshani, A. (1971). "System Deadlocks." Computing Surveys, 3(2).
3. Herlihy, M., and Shavit, N. (2008). "The Art of Multiprocessor Programming." Morgan Kaufmann.
4. C++ Standard, ISO/IEC 14882:2011, Section 29: "Atomic operations library."
