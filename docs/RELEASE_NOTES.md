# v0.1.0-alpha

Erster Machbarkeitsprototyp für **Seed3 Desktop Dev Kit + Tulip CC**.

- Daisy: 16 Sinusstimmen, AD, alle 16 Taster/LEDs, zwei Potis, Pickup,
  doppelte C5 und getrennte physische/MIDI-Haltezustände.
- Tulip: native 1024×600-UIScreen-App mit 16 Tasten, Press/Release/Press-Lost,
  Attack-/Decay-Slidern, Millisekundenanzeige und Ping/Pong-Status.
- Drei kompilierte Backends: DIN (empfohlen), USB_INTERNAL, USB_EXTERNAL.
- Gepinnte Bibliotheken/Toolchain, Hosttests, MicroPython-Syntaxcheck,
  reproduzierbares Buildskript und GitHub Actions.

**Validierung:** Softwaretests und Crossbuilds sind bestanden; keine reale
Hardwareprüfung. Keine Zusage für USB-Hotplug oder Multi-Touch-Akkorde.
AD ist ein One-Shot, Note-Off beendet den endlichen Ausklang nicht vorzeitig.
7-Bit-Parameter, kein Voice Stealing, keine Velocity-Lautstärke.

Tulips Standardfirmware reicht nach Quellprüfung für den empfohlenen DIN-Aufbau.
USB-MIDI-Deskriptoren passen zusammen; ein unbegrenzter Wait im Tulip-USB-Tx-Pfad
bleibt ein Integrationsrisiko. Richtige Portvariante und Stromplan beachten.

Dateien mit `DIN` verwenden die vorhandenen DIN-Buchsen. `USB_INTERNAL` ist
für USB-C direkt auf Seed3; `USB_EXTERNAL` für Desktop J7. Alle Images sind
BOOT_NONE bei 0x08000000 und für ROM-DFU/Web Programmer vorgesehen.

Der Alpha-Prerelease enthält Firmware und Diagnoseartefakte für alle drei
Backends, die installierbare Tulip-App, Manifest, Prüfsummen und ein vollständiges
Quell-/Artefaktpaket. Das Repository bleibt privat. Hardwaretests stehen aus.
