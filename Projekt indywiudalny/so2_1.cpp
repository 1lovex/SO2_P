/**
 * Implementation of the Dining Philosophers problem using mutexes and semaphores
 *
 * This program demonstrates a solution to the classic concurrency problem where
 * multiple philosophers (threads) compete for limited resources (chopsticks).
 * The implementation uses two synchronization mechanisms:
 * 1. Mutexes - to ensure exclusive access to each chopstick
 * 2. Semaphore - to limit the number of philosophers at the table, preventing deadlock
 */
#include <thread>
#include <atomic>
#include <iostream>
#include <vector>
#include <string>
#include "Mutex.hpp"
#include "Semaphore.hpp"
using namespace std;

/**
 * Mutex for synchronizing console output to prevent garbled messages
 */
Mutex printMutex;

/**
 * Thread-safe logging function
 * @param message The message to print to the console
 */
void printLog(const string& message) {
	printMutex.lock();
	cout << message << endl;
	printMutex.unlock();
}

/**
 * Number of philosophers (and chopsticks) in the simulation
 */
const int NUM_PHILOSOPHERS = 10;

/**
 * Array of mutexes representing chopsticks
 * Each chopstick can only be held by one philosopher at a time
 */
Mutex chopsticks[NUM_PHILOSOPHERS];

/**
 * Semaphore limiting the number of philosophers that can sit at the table
 * By allowing only N-1 philosophers to sit simultaneously, we prevent deadlock
 */
Semaphore diningTable(NUM_PHILOSOPHERS - 1);

/**
 * Simulates a philosopher's behavior of thinking and eating
 *
 * @param id The philosopher's unique identifier (0 to NUM_PHILOSOPHERS-1)
 * @param chopsticks Array of mutex objects representing the chopsticks
 * @param iterations Number of think-eat cycles (-1 for infinite)
 */
void philosopher(int id, Mutex* chopsticks, int iterations = -1) {
	for (int i = 0; (iterations == -1 ? i >= 0 : i < iterations); i++) {
		// Thinking phase
		printLog("Philosopher " + to_string(id) + " is thinking.");
		this_thread::sleep_for(chrono::milliseconds(1000));

		// Try to sit at the table (prevents deadlock by limiting concurrent philosophers)
		diningTable.wait();

		// Get references to the chopsticks on the left and right
		Mutex& leftChopstick = chopsticks[id];
		Mutex& rightChopstick = chopsticks[(id + 1) % NUM_PHILOSOPHERS];

		// Even-numbered philosophers pick up left chopstick first, odd-numbered pick up right first
		// This asymmetric approach helps prevent circular waiting conditions
		if (id % 2 == 0) {
			printLog("Philosopher " + to_string(id) + " is picking up left chopstick (chopstick " + to_string(id) + ").");
			leftChopstick.lock();
			printLog("Philosopher " + to_string(id) + " is picking up right chopstick (chopstick " + to_string((id + 1) % NUM_PHILOSOPHERS) + ").");
			rightChopstick.lock();
		}
		else {
			printLog("Philosopher " + to_string(id) + " is picking up right chopstick (chopstick " + to_string((id + 1) % NUM_PHILOSOPHERS) + ").");
			rightChopstick.lock();
			printLog("Philosopher " + to_string(id) + " is picking up left chopstick (chopstick " + to_string(id) + ").");
			leftChopstick.lock();
		}

		// Eating phase
		printLog("Philosopher " + to_string(id) + " is eating.");
		this_thread::sleep_for(chrono::milliseconds(1000));

		// Release resources in reverse order of acquisition
		printLog("Philosopher " + to_string(id) + " is putting down left chopstick (chopstick " + to_string(id) + ").");
		leftChopstick.unlock();
		printLog("Philosopher " + to_string(id) + " is putting down right chopstick (chopstick " + to_string((id + 1) % NUM_PHILOSOPHERS) + ").");
		rightChopstick.unlock();

		// Leave the table
		diningTable.signal();
	}
}

/**
 * Main function creates philosopher threads and waits for them to complete
 */
int main() {
	vector<thread> philosopherThreads;

	// Create threads for each philosopher
	for (int i = 0; i < NUM_PHILOSOPHERS; ++i) {
		philosopherThreads.emplace_back(philosopher, i, chopsticks, 2);
	}

	// Wait for all philosopher threads to complete
	for (auto& thread : philosopherThreads) {
		thread.join();
	}

	return 0;
}