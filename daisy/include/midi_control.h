#pragma once
#include "control.h"
#include "hid/midi_parser.h"

namespace piano {
struct MidiAction { bool strike = false; bool snapshot = false; uint8_t note = 0; };

// Application protocol, shared by the target and host tests using libDaisy's
// real MIDI parser. Audio, widgets and transport details stay outside it.
inline MidiAction ApplyMidi(Controls &controls, const daisy::MidiEvent &event, uint32_t now) {
    MidiAction result;
    if(event.channel != config::CHANNEL - 1) return result;
    if(event.type == daisy::NoteOn || event.type == daisy::NoteOff) {
        result.strike = controls.RemoteNote(event.data[0], event.data[1], event.type == daisy::NoteOn, now);
        result.note = event.data[0];
    } else if(event.type == daisy::ControlChange) {
        const uint8_t cc = event.data[0], value = event.data[1];
        if(cc == config::CC_ATTACK) { controls.attack.Remote(value); controls.Touch(now); }
        else if(cc == config::CC_DECAY) { controls.decay.Remote(value); controls.Touch(now); }
        else if(cc == config::CC_PING && value == config::PING_VALUE) {
            controls.Touch(now);
            result.snapshot = true;
        }
    } else if(event.type == daisy::ChannelMode
              && (event.cm_type == daisy::AllSoundOff || event.cm_type == daisy::AllNotesOff)) {
        // libDaisy exposes CC >= 120 as ChannelMode, not ControlChange.
        controls.PanicRemote();
    }
    return result;
}
} // namespace piano
