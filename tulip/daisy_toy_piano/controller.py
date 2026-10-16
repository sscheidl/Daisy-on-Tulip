"""UI-independent MIDI session, note ownership and coalesced parameters."""
from . import config as C

def milliseconds(value, attack):
    lo = C.ATTACK_MIN_MS if attack else C.DECAY_MIN_MS
    hi = C.ATTACK_MAX_MS if attack else C.DECAY_MAX_MS
    return round(lo * ((hi / lo) ** (value / 127)))

class Controller:
    def __init__(self, transport, ticks_ms, ticks_diff):
        self.transport = transport
        self.ticks_ms = ticks_ms
        self.ticks_diff = ticks_diff
        self.connected = False
        self.enabled = True
        self.closed = False
        self.last_pong = None
        self.last_ping = None
        self.last_cc = None
        self.values = {C.CC_ATTACK: 0, C.CC_DECAY: 0}
        self.pending = {}
        self.editing = set()
        self.held = set()  # Key IDs, so the two C5s have independent ownership.
        self.transport.start(self.receive)

    def _send(self, status, first, second):
        self.transport.send((status | (C.CHANNEL - 1), first, second))

    def press(self, key):
        if self.closed or not self.enabled or not self.connected or key in self.held:
            return False
        if not 0 <= key < len(C.NOTES):
            return False
        self.held.add(key)
        self._send(0x90, C.NOTES[key], 100)
        return True

    def release(self, key):
        if key in self.held:
            self.held.remove(key)
            self._send(0x80, C.NOTES[key], 0)

    def release_all(self):
        for key in tuple(self.held):
            self.release(key)
        # Remote source only on Daisy. Physical buttons are unaffected.
        self._send(0xB0, 123, 0)

    def set_parameter(self, cc, value):
        if cc not in self.values or self.closed or not self.enabled or not self.connected:
            return
        value = max(0, min(127, int(value)))
        self.values[cc] = value
        self.pending[cc] = value

    def receive(self, message):
        if self.closed or len(message) < 3 or message[0] != (0xB0 | (C.CHANNEL - 1)):
            return
        cc, value = message[1], message[2]
        if not 0 <= value <= 127:
            return
        if cc == C.CC_PONG and value == C.PING_VALUE:
            if not self.connected:
                self.pending.clear()
                self.editing.clear()
                self.held.clear()
            self.connected = True
            self.last_pong = self.ticks_ms()
        elif cc in self.values and cc not in self.pending and cc not in self.editing:
            # Never echo feedback. Daisy's snapshot is authoritative when idle.
            self.values[cc] = value

    def tick(self):
        if self.closed:
            return
        now = self.ticks_ms()
        if self.connected and self.ticks_diff(now, self.last_pong) >= C.TIMEOUT_MS:
            self.release_all()
            self.connected = False
            self.pending.clear()
            self.editing.clear()
        if self.last_ping is None or self.ticks_diff(now, self.last_ping) >= C.HEARTBEAT_MS:
            self._send(0xB0, C.CC_PING, C.PING_VALUE)
            self.last_ping = now
        if self.connected and self.pending and (self.last_cc is None or self.ticks_diff(now, self.last_cc) >= C.CC_INTERVAL_MS):
            # Both parameters get one update each per interval at most.
            for cc, value in tuple(self.pending.items()):
                self._send(0xB0, cc, value)
                del self.pending[cc]
            self.last_cc = now

    def deactivate(self):
        if self.closed:
            return
        self.enabled = False
        self.release_all()
        self.pending.clear()
        self.editing.clear()

    def activate(self):
        if self.closed:
            return
        self.enabled = True
        self.last_ping = None  # Request fresh authoritative values.

    def close(self):
        if not self.closed:
            self.deactivate()
            self.transport.close()
            self.closed = True
