#pragma once
#include <atomic>
#include "synth.h"
namespace piano {
// One foreground producer, one audio ISR consumer. No heap/locks in audio.
class StrikeQueue {
  public:
    bool Push(Strike strike) {
        const unsigned write = write_.load(std::memory_order_relaxed);
        const unsigned next = (write + 1) % 64;
        if(next == read_.load(std::memory_order_acquire)) return false;
        strikes_[write] = strike;
        write_.store(next, std::memory_order_release);
        return true;
    }
    bool Pop(Strike &strike) {
        const unsigned read = read_.load(std::memory_order_relaxed);
        if(read == write_.load(std::memory_order_acquire)) return false;
        strike = strikes_[read];
        read_.store((read + 1) % 64, std::memory_order_release);
        return true;
    }
  private:
    Strike strikes_[64] = {};
    std::atomic<unsigned> read_{0}, write_{0};
};
} // namespace piano
