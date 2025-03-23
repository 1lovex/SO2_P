#pragma once
#include <thread>
#include <atomic>
using namespace std;

/**
 * Semaphore class implementing a counting semaphore using atomic operations
 * Used for controlling access to a limited number of resources
 */
class Semaphore {
private:
	/**
	 * Atomic counter that tracks available resources
	 */
	atomic<int> resourceCount;

public:
	/**
	 * Constructor initializes the semaphore with specified count
	 * @param initialCount Number of resources initially available
	 */
	explicit Semaphore(int initialCount) : resourceCount(initialCount) {}

	/**
	 * Wait operation (P/down) decrements the counter if positive
	 * Blocks until a resource becomes available
	 */
	void wait() {
		while (true) {
			int currentCount = resourceCount.load(memory_order_acquire);

			// Try to decrement the counter if it's greater than zero
			if (currentCount > 0 && resourceCount.compare_exchange_weak(currentCount, currentCount - 1, memory_order_acquire)) {
				break;
			}

			// Yield the CPU to avoid busy waiting
			this_thread::yield();
		}
	}

	/**
	 * Signal operation (V/up) increments the counter
	 * Makes a resource available to waiting threads
	 */
	void signal() {
		resourceCount.fetch_add(1, memory_order_release);
	}
};