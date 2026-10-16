import unittest
from daisy_toy_piano.controller import Controller, milliseconds
from daisy_toy_piano import config as C

class Transport:
    def __init__(self):
        self.messages = []
        self.closed = False
    def start(self, receiver):
        self.receiver = receiver
    def send(self, message):
        self.messages.append(tuple(message))
    def close(self):
        self.closed = True

class SessionTest(unittest.TestCase):
    def setUp(self):
        self.now = 0
        self.transport = Transport()
        self.c = Controller(self.transport, lambda: self.now, lambda a, b: (a - b + 2**29) % 2**30 - 2**29)
    def connect(self):
        self.c.tick()
        self.transport.receiver((0xB0, C.CC_PONG, C.PING_VALUE))

    def test_handshake_and_all_keys(self):
        self.assertFalse(self.c.press(0))
        self.connect()
        self.assertTrue(self.c.connected)
        for key in range(16):
            self.assertTrue(self.c.press(key))
            self.assertFalse(self.c.press(key))
            self.assertEqual(self.transport.messages[-1], (0x90, C.NOTES[key], 100))
            self.c.release(key)
            self.assertEqual(self.transport.messages[-1], (0x80, C.NOTES[key], 0))
        self.assertFalse(self.c.press(16))

    def test_duplicate_c5_ownership(self):
        self.connect()
        self.c.press(7)
        self.c.press(8)
        self.c.release(7)
        self.assertEqual(self.c.held, {8})
        self.c.release(8)
        self.assertFalse(self.c.held)

    def test_coalescing_and_feedback(self):
        self.connect()
        for value in range(128):
            self.c.set_parameter(C.CC_ATTACK, value)
        before = len(self.transport.messages)
        self.c.tick()
        self.assertEqual(self.transport.messages[before:], [(0xB0, C.CC_ATTACK, 127)])
        self.c.set_parameter(C.CC_DECAY, 100)
        self.now = C.CC_INTERVAL_MS - 1
        self.c.tick()
        self.assertIn(C.CC_DECAY, self.c.pending)
        self.now += 1
        self.c.tick()
        before = len(self.transport.messages)
        self.c.receive((0xB0, C.CC_ATTACK, 20))
        self.assertEqual(self.c.values[C.CC_ATTACK], 20)
        self.c.tick()
        self.assertEqual(before, len(self.transport.messages)) # No echo.
        self.c.editing.add(C.CC_ATTACK)
        self.c.receive((0xB0, C.CC_ATTACK, 99))
        self.assertEqual(self.c.values[C.CC_ATTACK], 20)

    def test_timeout_and_reconnect(self):
        self.connect()
        self.c.press(0)
        self.c.set_parameter(C.CC_ATTACK, 100)
        self.now = C.TIMEOUT_MS
        self.c.tick()
        self.assertFalse(self.c.connected)
        self.assertFalse(self.c.held)
        self.assertFalse(self.c.pending)
        self.assertIn((0x80, 60, 0), self.transport.messages)
        self.connect()
        self.assertTrue(self.c.connected)
        self.assertFalse(self.c.held) # No automatic replay after replug.
        self.c.receive((0xB0, C.CC_ATTACK, 40))
        self.assertEqual(self.c.values[C.CC_ATTACK], 40)

    def test_lifecycle(self):
        self.connect()
        self.c.press(1)
        self.c.deactivate()
        self.assertFalse(self.c.held)
        self.assertFalse(self.c.press(2))
        self.c.activate()
        self.assertTrue(self.c.press(2))
        self.c.close()
        count = len(self.transport.messages)
        self.c.tick()
        self.c.close()
        self.assertFalse(self.c.press(0))
        self.assertTrue(self.transport.closed)
        self.assertEqual(len(self.transport.messages), count)

    def test_filters_and_ranges(self):
        self.c.receive((0xB1, C.CC_PONG, C.PING_VALUE))
        self.c.receive((0xB0, C.CC_PONG, 1))
        self.c.receive((0xB0, C.CC_PONG))
        self.assertFalse(self.c.connected)
        self.assertEqual([milliseconds(0, True), milliseconds(127, True)], [1, 1000])
        self.assertEqual([milliseconds(0, False), milliseconds(127, False)], [20, 3000])

    def test_tick_wrap(self):
        self.now = 2**30 - 100
        self.connect()
        self.now = 200
        self.c.tick()
        self.assertTrue(self.c.connected)
        self.now = C.TIMEOUT_MS
        self.c.tick()
        self.assertFalse(self.c.connected)

if __name__ == '__main__':
    unittest.main()
