#pragma once
#include "control.h"
#include "Synthesis/oscillator.h"

namespace piano {
// A one-shot, linear AD. Retriggers start at the current level; Note-Off
// changes ownership/LEDs only. Times are captured at the next strike.
class Envelope {
  public:
    void Trigger(float sample_rate, float attack_ms, float decay_ms) {
        attack_left_ = static_cast<unsigned>(sample_rate * attack_ms * .001f);
        if(!attack_left_) attack_left_ = 1;
        decay_samples_ = static_cast<unsigned>(sample_rate * decay_ms * .001f);
        if(!decay_samples_) decay_samples_ = 1;
        decay_left_ = decay_samples_;
        decay_step_ = 1.f / decay_samples_;
        increment_ = (1.f - level_) / attack_left_;
        stage_ = 1;
    }
    float Process() {
        if(stage_ == 1) {
            level_ += increment_;
            if(--attack_left_ == 0) { level_ = 1.f; stage_ = 2; }
        } else if(stage_ == 2) {
            --decay_left_;
            level_ = decay_left_ * decay_step_;
            if(decay_left_ == 0) { level_ = 0.f; stage_ = 0; }
        }
        return level_;
    }
    bool Running() const { return stage_ != 0; }
    float Level() const { return level_; }
  private:
    float level_ = 0.f, increment_ = 0.f, decay_step_ = 1.f;
    unsigned attack_left_ = 0, decay_samples_ = 1, decay_left_ = 0;
    unsigned stage_ = 0;
};

struct Strike { uint8_t note, attack, decay; };

class Synth {
  public:
    void Init(float sample_rate) {
        sample_rate_ = sample_rate;
        for(auto &v : voices_) {
            v.osc.Init(sample_rate);
            v.osc.SetWaveform(daisysp::Oscillator::WAVE_SIN);
            v.osc.SetAmp(1.f);
        }
    }
    bool Trigger(Strike strike) {
        Voice *chosen = nullptr;
        // Repeated pitches share an oscillator and retrigger continuously.
        for(auto &v : voices_)
            if(v.env.Running() && v.note == strike.note) { chosen = &v; break; }
        if(!chosen) for(auto &v : voices_)
            if(!v.env.Running()) { chosen = &v; break; }
        // No discontinuous voice stealing: the 17th distinct tail is dropped.
        if(!chosen) { ++dropped_; return false; }
        chosen->note = strike.note;
        chosen->osc.SetFreq(440.f * std::pow(2.f, (static_cast<int>(strike.note) - 69) / 12.f));
        chosen->env.Trigger(sample_rate_, Milliseconds(strike.attack, true), Milliseconds(strike.decay, false));
        return true;
    }
    float Process() {
        float sum = 0.f;
        for(auto &v : voices_)
            if(v.env.Running()) sum += v.osc.Process() * v.env.Process();
        return sum * (.7f / 16.f);
    }
    unsigned Dropped() const { return dropped_; }
  private:
    struct Voice { daisysp::Oscillator osc; Envelope env; uint8_t note = 0; };
    Voice voices_[16];
    float sample_rate_ = 48000.f;
    unsigned dropped_ = 0;
};
} // namespace piano
