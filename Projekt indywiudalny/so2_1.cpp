#include <thread>
#include <atomic>
#include <iostream>
#include <vector>
#include <string>
#include "Mutex.hpp"
#include "Semaphore.hpp"
using namespace std;

Mutex printMutex;

void printLog(const string& message) {
	printMutex.lock();
	cout << message << endl;
	printMutex.unlock();
}

const int NUM_PHILOSOPHERS = 5;

Mutex chopsticks[NUM_PHILOSOPHERS];

Semaphore diningTable(NUM_PHILOSOPHERS - 1);

void philosopher(int id, Mutex* chopsticks, int iterations = -1) {
	for (int i = 0; (iterations == -1 ? i >= 0 : i < iterations); i++) {
		printLog("Philosopher " + to_string(id) + " is thinking.");
		this_thread::sleep_for(chrono::milliseconds(1000));

		diningTable.wait();

		Mutex& leftChopstick = chopsticks[id];
		Mutex& rightChopstick = chopsticks[(id + 1) % NUM_PHILOSOPHERS];

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

		printLog("Philosopher " + to_string(id) + " is eating.");
		this_thread::sleep_for(chrono::milliseconds(1000));

		printLog("Philosopher " + to_string(id) + " is putting down left chopstick (chopstick " + to_string(id) + ").");
		leftChopstick.unlock();
		printLog("Philosopher " + to_string(id) + " is putting down right chopstick (chopstick " + to_string((id + 1) % NUM_PHILOSOPHERS) + ").");
		rightChopstick.unlock();

		diningTable.signal();
	}
}

int main() {
	vector<thread> philosopherThreads;

	for (int i = 0; i < NUM_PHILOSOPHERS; ++i) {
		philosopherThreads.emplace_back(philosopher, i, chopsticks, 2);
	}

	for (auto& thread : philosopherThreads) {
		thread.join();
	}

	return 0;
}