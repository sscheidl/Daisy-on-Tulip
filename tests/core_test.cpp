#include "strike_queue.h"
#include "midi_control.h"
#include "hid/midi_parser.h"
#include <cassert>
#include <cmath>
#include <iostream>

using namespace piano;

int main() {
    daisy::MidiParser parser;
    parser.Init();
    Controls midi_controls;
    daisy::MidiEvent event;
    unsigned triggered = 0, snapshots = 0;
    const uint8_t input[] = {0x90, 60, 100, 62, 0xf8, 100, // Running status + realtime.
        0x91, 64, 100, // Wrong channel ignored.
        0x90, 60, 0, 0x80, 62, 0,
        0xb0, config::CC_ATTACK, 100, config::CC_DECAY, 80,
        config::CC_PING, config::PING_VALUE};
    for(auto byte : input) if(parser.Parse(byte, &event)) {
        const auto action = ApplyMidi(midi_controls, event, 200);
        triggered += action.strike;
        snapshots += action.snapshot;
    }
    assert(triggered == 2 && snapshots == 1);
    assert(midi_controls.Held(60) == 0 && midi_controls.Held(62) == 0 && midi_controls.Held(64) == 0);
    assert(midi_controls.attack.value == 100 && midi_controls.decay.value == 80);
    assert(midi_controls.attack.pickup && midi_controls.decay.pickup);
    midi_controls.Physical(0, true);
    midi_controls.RemoteNote(60, 100, true, 201);
    const uint8_t panic[] = {0xb0, 123, 0};
    for(auto byte : panic) if(parser.Parse(byte, &event)) ApplyMidi(midi_controls, event, 202);
    assert(midi_controls.Held(60) == 1 && midi_controls.Led(0));
    midi_controls.RemoteNote(62, 100, true, 203);
    const uint8_t sound_off[] = {0xb0, 120, 0};
    for(auto byte : sound_off) if(parser.Parse(byte, &event)) ApplyMidi(midi_controls, event, 204);
    assert(midi_controls.Held(62) == 0 && midi_controls.Led(0));
    assert(config::NOTES[7] == 72 && config::NOTES[8] == 72);
    Controls c;
    assert(c.Physical(7, true));
    assert(!c.Physical(7, true)); // Same debounced press cannot retrigger.
    assert(c.Physical(8, true));
    assert(c.RemoteNote(72, 100, true, 100));
    assert(c.RemoteNote(72, 100, true, 101));
    assert(c.Held(72) == 4);
    c.RemoteNote(72, 0, true, 102); // MIDI Note-On velocity 0 is Note-Off.
    assert(c.Held(72) == 3 && c.Led(7) && c.Led(8));
    c.Physical(7, false);
    assert(c.Led(7)); // Remote C5 still held.
    c.RemoteNote(72, 0, false, 103);
    assert(!c.Led(7) && c.Led(8));
    assert(c.Held(72) == 1);
    c.RemoteNote(72, 0, false, 104); // Stray Note-Off cannot underflow.
    assert(c.Held(72) == 1);
    c.Physical(8, false);
    assert(!c.Led(8));
    assert(!c.Physical(16, true));
    assert(!c.RemoteNote(255, 100, true, 110));
    for(unsigned i = 0; i < 260; ++i) c.RemoteNote(60, 100, true, 200);
    assert(c.Held(60) == 255); // Malformed duplicate flood is bounded.
    c.Physical(0, true);
    c.PanicRemote();
    assert(c.Held(60) == 1 && c.Led(0)); // Panic protects physical source.
    c.RemoteNote(62, 100, true, 0xfffffff0u);
    assert(!c.Watchdog(0x20));
    assert(c.Watchdog(0x20 + config::TIMEOUT_MS)); // Millisecond wrap.
    assert(c.Held(62) == 0 && c.Led(0));

    Parameter p;
    p.Pot(20);
    p.Remote(90);
    assert(!p.Pot(21) && p.value == 90 && p.pickup);
    assert(!p.Pot(60) && p.value == 90);
    assert(p.Pot(95) && p.value == 95 && !p.pickup);
    assert(!p.Pot(96)); // Noise hysteresis.
    assert(p.Pot(127) && p.value == 127);
    p.Remote(40);
    assert(!p.Pot(80));
    assert(p.Pot(35) && !p.pickup); // Downward crossing.
    Parameter early;
    early.Remote(100);
    assert(!early.Pot(0) && early.value == 100 && early.pickup);
    assert(early.Pot(127) && !early.pickup);

    assert(std::abs(Milliseconds(0, true) - 1.f) < .001f);
    assert(std::abs(Milliseconds(127, true) - 1000.f) < .1f);
    assert(std::abs(Milliseconds(0, false) - 20.f) < .001f);
    assert(std::abs(Milliseconds(127, false) - 3000.f) < .1f);
    Envelope env;
    env.Trigger(48000.f, 10.f, 100.f);
    float prev = 0.f;
    for(int i = 0; i < 480; ++i) {
        float v = env.Process();
        assert(v >= prev && v <= 1.00001f);
        prev = v;
    }
    assert(std::abs(env.Level() - 1.f) < .0001f);
    for(int i = 0; i < 2400; ++i) env.Process();
    float before = env.Level();
    env.Trigger(48000.f, 10.f, 100.f);
    assert(env.Process() - before < .003f); // Smooth retrigger from current level.
    for(int i = 0; i < 5400; ++i) env.Process();
    assert(!env.Running() && env.Level() == 0.f);
    env.Trigger(48000.f, 1000.f, 3000.f);
    unsigned duration = 0;
    while(env.Running()) { env.Process(); ++duration; assert(duration <= 192000); }
    assert(duration == 192000); // Exact 4-second bound, no float decay drift.

    Synth synth;
    synth.Init(48000.f);
    for(unsigned n = 60; n < 76; ++n) assert(synth.Trigger({static_cast<uint8_t>(n), 0, 0}));
    assert(synth.Trigger({60, 0, 0})); // Same pitch reuses the running voice.
    assert(!synth.Trigger({90, 0, 0}) && synth.Dropped() == 1);
    float energy = 0.f, peak = 0.f;
    for(unsigned i = 0; i < 1200; ++i) {
        float sample = synth.Process();
        assert(std::isfinite(sample) && std::abs(sample) <= .70001f);
        energy += sample * sample;
        peak = std::max(peak, std::abs(sample));
    }
    assert(energy > .001f && peak > .01f);
    assert(synth.Process() == 0.f); // AD runs out without receiving Note-Off.
    assert(synth.Trigger({90, 0, 0}));

    StrikeQueue queue;
    Strike s{};
    assert(!queue.Pop(s));
    for(unsigned n = 0; n < 63; ++n) assert(queue.Push({static_cast<uint8_t>(n), 1, 2}));
    assert(!queue.Push({99, 1, 2}));
    for(unsigned n = 0; n < 63; ++n) { assert(queue.Pop(s)); assert(s.note == n); }
    assert(!queue.Pop(s));
    for(unsigned i = 0; i < 1000; ++i) { assert(queue.Push({60, 4, 5})); assert(queue.Pop(s)); assert(s.note == 60); }
    std::cout << "PASS: real MIDI parser/protocol, ownership, LEDs, pickup, watchdog/wrap, AD, 16-voice DSP, queue\n";
}
