#pragma once
#include <atomic>
#include <thread>
using namespace std;

class Mutex {
private:
	atomic_flag lockState = ATOMIC_FLAG_INIT;

public:
	void lock() {
		while (lockState.test_and_set(memory_order_acquire)) {
			this_thread::yield();
		}
	}

	void unlock() {
		lockState.clear(memory_order_release);
	}
};