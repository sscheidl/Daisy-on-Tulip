#include "desktop_devkit.h"
#include "control.h"
#include "midi_backend.h"
#include "midi_control.h"
#include "strike_queue.h"

using namespace daisy;
using namespace piano;
desktop_devkit::Hardware hw;
Controls controls;
MidiBackend midi;
Synth synth;
StrikeQueue strikes;
volatile unsigned queue_overflows = 0; // Read with debugger; never print in audio.
bool dirty_attack = true, dirty_decay = true, pong = false;

void Trigger(uint8_t note) {
    if(!strikes.Push({note, controls.attack.value, controls.decay.value})) ++queue_overflows;
}

void Audio(AudioHandle::InputBuffer, AudioHandle::OutputBuffer out, size_t size) {
    Strike strike;
    for(unsigned i = 0; i < 32 && strikes.Pop(strike); ++i) synth.Trigger(strike);
    for(size_t i = 0; i < size; ++i) out[0][i] = out[1][i] = synth.Process();
}

void Receive(MidiEvent event, uint32_t now) {
    const auto action = ApplyMidi(controls, event, now);
    if(action.strike) Trigger(action.note);
    if(action.snapshot) pong = dirty_attack = dirty_decay = true;
}

int main() {
    hw.Init(); // Seed3 runtime codec detection; exact Desktop Dev Kit peripherals.
    hw.seed.SetAudioBlockSize(48);
    hw.seed.SetAudioSampleRate(SaiHandle::Config::SampleRate::SAI_48KHZ);
    synth.Init(hw.seed.AudioSampleRate());
    midi.Init(hw);
    hw.seed.StartAudio(Audio);
    uint32_t last_controls = System::GetNow(), last_led = last_controls, last_tx = last_controls;
    while(true) {
        const uint32_t now = System::GetNow();
        midi.Listen();
        for(unsigned i = 0; i < 32 && midi.HasEvents(); ++i) Receive(midi.PopEvent(), now);
        controls.Watchdog(now);
        if(static_cast<uint32_t>(now - last_controls) >= 1) {
            last_controls = now;
            hw.UpdateAllControls();
            for(unsigned i = 0; i < 16; ++i) {
                if(hw.button[i].RisingEdge() && controls.Physical(i, true)) Trigger(config::NOTES[i]);
                if(hw.button[i].FallingEdge()) controls.Physical(i, false);
            }
            dirty_attack |= controls.attack.Pot(static_cast<uint8_t>(hw.pot[0].Value() * 127.f + .5f));
            dirty_decay |= controls.decay.Pot(static_cast<uint8_t>(hw.pot[1].Value() * 127.f + .5f));
        }
        if(static_cast<uint32_t>(now - last_led) >= 10) {
            last_led = now;
            for(unsigned i = 0; i < 16; ++i) hw.SetLed(i, controls.Led(i) ? 1.f : 0.f);
            hw.UpdateLeds();
        }
        // Only foreground transmits. Coalesce pots; never build a CC backlog.
        if(static_cast<uint32_t>(now - last_tx) >= 5) {
            last_tx = now;
            if(pong) { midi.SendCC(config::CC_PONG, config::PING_VALUE); pong = false; }
            else if(dirty_attack) { midi.SendCC(config::CC_ATTACK, controls.attack.value); dirty_attack = false; }
            else if(dirty_decay) { midi.SendCC(config::CC_DECAY, controls.decay.value); dirty_decay = false; }
        }
    }
}
