"""Exercise actual app callbacks with event/transport doubles, not a render test."""
import importlib
import sys
import types
import unittest
from unittest.mock import Mock, patch
from test_controller import Transport
from daisy_toy_piano.controller import Controller
from daisy_toy_piano import config as C

events = types.SimpleNamespace(PRESSED=1, RELEASED=2, PRESS_LOST=3, VALUE_CHANGED=4, CLICKED=5)
with patch.dict(sys.modules, {"tulip": types.ModuleType("tulip"), "lvgl": types.SimpleNamespace(EVENT=events)}):
    PianoApp = importlib.import_module('daisy_toy_piano.app').PianoApp

class UiEventTest(unittest.TestCase):
    def setUp(self):
        self.transport = Transport()
        self.controller = Controller(self.transport, lambda: 0, lambda a, b: a-b)
        self.controller.receive((0xB0, C.CC_PONG, C.PING_VALUE))
        self.app = PianoApp.__new__(PianoApp)
        self.app.controller = self.controller
        self.app.closed = False
        self.app.highlight = Mock()
        self.app.syncing = False
        self.app.sliders = {C.CC_ATTACK: types.SimpleNamespace(slider=types.SimpleNamespace(get_value=lambda: 60))}

    def event(self, code):
        return types.SimpleNamespace(get_code=lambda: code)

    def test_press_release_lost_and_ignore_click(self):
        callback = self.app.key_callback(0)
        before = len(self.transport.messages)
        callback(self.event(events.CLICKED))
        self.assertEqual(before, len(self.transport.messages))
        callback(self.event(events.PRESSED))
        callback(self.event(events.PRESSED))
        self.assertEqual(self.transport.messages[-1], (0x90, 60, 100))
        callback(self.event(events.PRESS_LOST))
        callback(self.event(events.RELEASED))
        self.assertEqual(self.transport.messages[-1], (0x80, 60, 0))
        self.assertEqual(len(self.transport.messages), before + 2)

    def test_slider_drag_and_programmatic_update(self):
        callback = self.app.slider_callback(C.CC_ATTACK)
        callback(self.event(events.PRESSED))
        self.assertIn(C.CC_ATTACK, self.controller.editing)
        callback(self.event(events.VALUE_CHANGED))
        self.assertEqual(self.controller.pending[C.CC_ATTACK], 60)
        callback(self.event(events.PRESS_LOST))
        self.assertNotIn(C.CC_ATTACK, self.controller.editing)
        self.controller.pending.clear()
        self.app.syncing = True
        callback(self.event(events.VALUE_CHANGED))
        self.assertFalse(self.controller.pending)

    def test_close_timer_callback_cleanup(self):
        self.app.timer = Mock()
        timer = self.app.timer
        self.controller.press(1)
        self.app.close(None)
        self.app.close(None)
        self.assertFalse(self.controller.held)
        self.assertTrue(self.transport.closed)
        timer.delete.assert_called_once()
        self.app.key_callback(2)(self.event(events.PRESSED))
        self.assertFalse(self.controller.held)

    def test_cleanup_after_partial_startup(self):
        self.app.timer = None
        self.app.close(None)
        self.assertTrue(self.transport.closed)

if __name__ == '__main__':
    unittest.main()
