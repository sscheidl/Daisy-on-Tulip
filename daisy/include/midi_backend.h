#pragma once
#include "desktop_devkit.h"
#include "protocol_config.h"

namespace piano {
class MidiBackend {
  public:
    void Init(daisy::desktop_devkit::Hardware &hw) {
#if PIANO_MIDI_BACKEND == 0
        uart_ = &hw.midi; // Desktop's USART1, D13 TX / D14 RX, DIN optocoupler.
        uart_->StartReceive();
#else
        (void)hw;
        daisy::MidiUsbHandler::Config cfg;
#if PIANO_MIDI_BACKEND == 1
        cfg.transport_config.periph = daisy::MidiUsbTransport::Config::INTERNAL;
#elif PIANO_MIDI_BACKEND == 2
        cfg.transport_config.periph = daisy::MidiUsbTransport::Config::EXTERNAL;
#else
#error Invalid MIDI backend
#endif
        cfg.transport_config.tx_retry_count = 0;
        usb_.Init(cfg);
        // libDaisy defaults USB and audio DMA to priority 0. Let audio preempt
        // USB parsing; no changes to the pinned library sources are needed.
#if PIANO_MIDI_BACKEND == 1
        NVIC_SetPriority(OTG_FS_IRQn, 1);
        NVIC_SetPriority(OTG_FS_EP1_IN_IRQn, 1);
        NVIC_SetPriority(OTG_FS_EP1_OUT_IRQn, 1);
#else
        NVIC_SetPriority(OTG_HS_IRQn, 1);
        NVIC_SetPriority(OTG_HS_EP1_IN_IRQn, 1);
        NVIC_SetPriority(OTG_HS_EP1_OUT_IRQn, 1);
#endif
        usb_.StartReceive();
#endif
    }
    void Listen() { Handler().Listen(); }
    bool HasEvents() { return Handler().HasEvents(); }
    daisy::MidiEvent PopEvent() { return Handler().PopEvent(); }
    void SendCC(uint8_t cc, uint8_t value) {
        uint8_t msg[3] = {static_cast<uint8_t>(0xb0 | (config::CHANNEL - 1)), cc, value};
        Handler().SendMessage(msg, sizeof(msg));
    }
  private:
#if PIANO_MIDI_BACKEND == 0
    daisy::MidiUartHandler *uart_ = nullptr;
    daisy::MidiUartHandler &Handler() { return *uart_; }
#else
    daisy::MidiUsbHandler usb_;
    daisy::MidiUsbHandler &Handler() { return usb_; }
#endif
};
} // namespace piano
