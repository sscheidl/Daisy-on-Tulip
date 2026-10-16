#pragma once
#include "protocol_config.h"
#include <cmath>
#include <cstdint>

namespace piano {
inline float Milliseconds(unsigned value, bool attack) {
    const float lo = attack ? config::ATTACK_MIN_MS : config::DECAY_MIN_MS;
    const float hi = attack ? config::ATTACK_MAX_MS : config::DECAY_MAX_MS;
    return lo * std::pow(hi / lo, static_cast<float>(value) / 127.f);
}

// Foreground only. Pickup waits until the pot crosses the remote target.
struct Parameter {
    uint8_t value = 0;
    uint8_t previous = 0;
    bool initialized = false;
    bool pickup = false;
    void Remote(uint8_t v) { value = v; pickup = true; }
    bool Pot(uint8_t v) {
        if(!initialized) {
            initialized = true;
            previous = v;
            if(pickup) return false;
            value = v;
            return true;
        }
        const int delta = static_cast<int>(v) - value;
        const bool crosses = (previous <= value && v >= value)
                             || (previous >= value && v <= value);
        previous = v;
        if(pickup) {
            if(std::abs(delta) <= 2 || crosses) pickup = false;
            else return false;
        }
        // Two CC steps of hysteresis, but endpoints are always reachable.
        if(std::abs(delta) >= 2 || (delta != 0 && (v == 0 || v == 127))) {
            value = v;
            return true;
        }
        return false;
    }
};

class Controls {
  public:
    Parameter attack, decay;
    bool Physical(unsigned key, bool down) {
        if(key >= 16 || physical_[key] == down) return false;
        physical_[key] = down;
        return down;
    }
    bool RemoteNote(uint8_t note, uint8_t velocity, bool down, uint32_t now) {
        if(note > 127) return false;
        Touch(now);
        if(down && velocity) {
            if(remote_[note] == 255) return false;
            ++remote_[note];
            return true;
        }
        if(remote_[note]) --remote_[note];
        return false;
    }
    void Touch(uint32_t now) { last_rx_ = now; remote_alive_ = true; }
    void PanicRemote() { for(auto &n : remote_) n = 0; remote_alive_ = false; }
    bool Watchdog(uint32_t now) {
        if(remote_alive_ && static_cast<uint32_t>(now - last_rx_) >= config::TIMEOUT_MS) {
            PanicRemote();
            return true;
        }
        return false;
    }
    unsigned Held(uint8_t note) const {
        if(note > 127) return 0;
        unsigned count = remote_[note];
        for(unsigned i = 0; i < 16; ++i)
            if(config::NOTES[i] == note && physical_[i]) ++count;
        return count;
    }
    bool Led(unsigned key) const {
        // Physical keys light individually; a remote C5 lights both matching keys.
        return key < 16 && (physical_[key] || remote_[config::NOTES[key]] > 0);
    }
  private:
    bool physical_[16] = {};
    uint8_t remote_[128] = {};
    bool remote_alive_ = false;
    uint32_t last_rx_ = 0;
};
} // namespace piano
