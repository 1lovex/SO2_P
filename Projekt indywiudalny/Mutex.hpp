#pragma once
#include <atomic>
#include <thread>
using namespace std;

/**
 * Mutex class implementing a simple mutual exclusion lock
 * Used to protect critical sections of code from concurrent access
 */
class Mutex {
private:
	/**
	 * Atomic flag used for implementing the spin lock
	 * When set, indicates the mutex is locked
	 */
	atomic_flag lockState = ATOMIC_FLAG_INIT;

public:
	/**
	 * Locks the mutex, blocking until it can be acquired
	 * Uses test-and-set with busy waiting (spinning)
	 */
	void lock() {
		// Spin until we can acquire the lock
		while (lockState.test_and_set(memory_order_acquire)) {
			// Yield to other threads while waiting
			this_thread::yield();
		}
	}

	/**
	 * Unlocks the mutex, allowing other threads to acquire it
	 */
	void unlock() {
		lockState.clear(memory_order_release);
	}
};