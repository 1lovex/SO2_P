#pragma once
#include <thread>
#include <atomic>
using namespace std;

class Semaphore {
private:
	atomic<int> resourceCount;

public:
	explicit Semaphore(int initialCount) : resourceCount(initialCount) {}

	void wait() {
		while (true) {
			int currentCount = resourceCount.load(memory_order_acquire);

			if (currentCount > 0 && resourceCount.compare_exchange_weak(currentCount, currentCount - 1, memory_order_acquire)) {
				break;
			}

			this_thread::yield();
		}
	}

	void signal() {
		resourceCount.fetch_add(1, memory_order_release);
	}
};