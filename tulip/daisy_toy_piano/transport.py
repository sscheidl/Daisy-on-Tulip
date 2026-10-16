"""Tulip transport adapter. No GUI dependencies; MIDI bytes in/out only."""

class TulipMidiTransport:
    def __init__(self):
        import tulip
        import midi
        self._tulip = tulip
        self._midi = midi
        self._receiver = None
        self._callback = self._receive

    def start(self, receiver):
        self._receiver = receiver
        self._midi.add_callback(self._callback)

    def _receive(self, message):
        if self._receiver is not None:
            self._receiver(message)

    def send(self, message):
        # Standard firmware sends to TRS and any connected USB MIDI device.
        self._tulip.midi_out(bytes(message))

    def close(self):
        if self._receiver is not None:
            self._midi.remove_callback(self._callback)
            self._receiver = None
