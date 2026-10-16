"""1024 x 600 native UIScreen/LVGL 9 app; no audio engine or blocking loop."""
import time
import tulip
import lvgl as lv
from . import config as C
from .controller import Controller, milliseconds
from .transport import TulipMidiTransport

class PianoApp:
    def __init__(self, screen):
        self.screen = screen
        self.closed = False
        self.timer = None
        self.keys = []
        self.sliders = {}
        self.readouts = {}
        self.callbacks = []
        self.syncing = False
        self.status_text = None
        self.controller = Controller(TulipMidiTransport(), time.ticks_ms, time.ticks_diff)
        # Register cleanup before creating widgets, including failed app startup.
        screen.activate_callback = self.activate
        screen.deactivate_callback = self.deactivate
        screen.quit_callback = self.close
        screen.set_bg_color(1)
        screen.group.remove_flag(lv.obj.FLAG.SCROLLABLE)
        screen.offset_x = screen.offset_y = 0
        self.label('DAISY / TULIP', 24, 22, 360, 32, font=lv.font_montserrat_24)
        self.label('TOY PIANO   |   16 voices on Daisy Seed3', 24, 60, 680, 24)
        self.status = self.label('Daisy nicht verbunden', 520, 24, 390, 28)
        self.label('ATTACK', 28, 116, 200, 24)
        self.label('DECAY', 532, 116, 200, 24)
        for cc, x in ((C.CC_ATTACK, 28), (C.CC_DECAY, 532)):
            self.readouts[cc] = self.label('--- ms', x + 260, 116, 180, 24)
            widget = tulip.UISlider(val=0, w=408, h=20, bar_color=151,
                                    unset_bar_color=9, handle_color=255)
            self.add(widget, x + 12, 166, 436, 52)
            widget.slider.set_range(0, 127)
            widget.slider.align(lv.ALIGN.TOP_LEFT, 12, 16)
            self.sliders[cc] = widget
            callback = self.slider_callback(cc)
            self.callbacks.append(callback)
            for event in (lv.EVENT.PRESSED, lv.EVENT.RELEASED, lv.EVENT.PRESS_LOST, lv.EVENT.VALUE_CHANGED):
                widget.slider.add_event_cb(callback, event, None)
        self.label('01  /  C4 - C5', 24, 238, 400, 24)
        self.label('02  /  C5 - C6', 24, 406, 400, 24)
        for key, name in enumerate(C.NOTE_NAMES):
            row, col = divmod(key, 8)
            widget = tulip.UIButton(text=name, w=112, h=112, bg_color=255,
                                    fg_color=0, radius=12, font=lv.font_montserrat_24)
            self.add(widget, 22 + col * 124, 276 + row * 168, 112, 112)
            widget.button.align(lv.ALIGN.TOP_LEFT, 0, 0)
            widget.button.set_style_bg_color(lv.color_hex(0x8de4b2), lv.PART.MAIN | lv.STATE.CHECKED)
            # Capture press and both possible release paths. CLICKED is too late.
            widget.button.remove_flag(lv.obj.FLAG.SCROLLABLE)
            widget.button.remove_flag(lv.obj.FLAG.PRESS_LOCK)
            widget.label.align(lv.ALIGN.CENTER, 0, 0)
            callback = self.key_callback(key)
            self.callbacks.append(callback)
            for event in (lv.EVENT.PRESSED, lv.EVENT.RELEASED, lv.EVENT.PRESS_LOST):
                widget.button.add_event_cb(callback, event, None)
            self.keys.append(widget)
        self.label('Touch: eine Taste  /  Akkorde: Daisy-Taster  /  C5 ist doppelt belegt', 24, 568, 960, 24)
        self.timer = lv.timer_create(self.tick, 20, None)
        screen.present()

    def add(self, widget, x, y, w, h):
        self.screen.add(widget, x=x, y=y)
        widget.group.set_style_pad_all(0, lv.PART.MAIN)
        widget.group.set_style_radius(0, lv.PART.MAIN)
        widget.group.set_size(w, h)
        return widget

    def label(self, text, x, y, w, h, font=None):
        widget = tulip.UILabel(text, fg_color=255, w=w, font=font)
        self.add(widget, x, y, w, h)
        widget.label.set_style_text_align(lv.TEXT_ALIGN.LEFT, lv.PART.MAIN)
        return widget

    def key_callback(self, key):
        def callback(event):
            if self.closed:
                return
            code = event.get_code()
            if code == lv.EVENT.PRESSED:
                self.controller.press(key)
            elif code in (lv.EVENT.RELEASED, lv.EVENT.PRESS_LOST):
                self.controller.release(key)
            else:
                return
            self.highlight()
        return callback

    def slider_callback(self, cc):
        def callback(event):
            if self.closed or self.syncing:
                return
            code = event.get_code()
            if code == lv.EVENT.PRESSED:
                self.controller.editing.add(cc)
            elif code in (lv.EVENT.RELEASED, lv.EVENT.PRESS_LOST):
                self.controller.editing.discard(cc)
            if code == lv.EVENT.VALUE_CHANGED:
                self.controller.set_parameter(cc, self.sliders[cc].slider.get_value())
        return callback

    def highlight(self):
        for key, widget in enumerate(self.keys):
            if key in self.controller.held:
                widget.button.add_state(lv.STATE.CHECKED)
            else:
                widget.button.remove_state(lv.STATE.CHECKED)

    def tick(self, timer):
        if self.closed:
            return
        self.controller.tick()
        text = 'Daisy verbunden / MIDI 1' if self.controller.connected else 'Daisy nicht verbunden / Kabel pruefen'
        if text != self.status_text:
            self.status.label.set_text(text)
            self.status_text = text
        self.syncing = True
        try:
            for cc, widget in self.sliders.items():
                value = self.controller.values[cc]
                if cc not in self.controller.editing:
                    widget.slider.set_value(value, lv.ANIM.OFF)
                self.readouts[cc].label.set_text(('%d ms' % milliseconds(value, cc == C.CC_ATTACK)) if self.controller.connected else '--- ms')
        finally:
            self.syncing = False
        self.highlight()

    def deactivate(self, screen):
        self.controller.deactivate()
        self.highlight()

    def activate(self, screen):
        self.controller.activate()

    def close(self, screen):
        if not self.closed:
            self.controller.close()
            self.closed = True
            if self.timer is not None:
                self.timer.delete()
                self.timer = None
            # UIScreen removes its widget tree and LVGL callbacks after this hook.
