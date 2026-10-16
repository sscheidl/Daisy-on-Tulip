# Alpha-Builds

`scripts/build.sh` erzeugt hier die drei Varianten mit `.bin`, `.elf`, `.map`,
`SHA256SUMS`, `manifest.json` und Buildlogs. Die Binärdateien sind im
Komplett-ZIP vorhanden und werden als Release-Assets vorbereitet; das Quell-Git
enthält hier Anleitung und Manifest. Der geprüfte Alpha-Satz ist außerdem
unter `release-assets/v0.1.0-alpha/` versioniert.

| Dateistamm | MIDI-Anschluss |
|---|---|
| `daisy_toy_piano_DIN` | Vorhandene Desktop-DIN-Buchsen, empfohlen |
| `daisy_toy_piano_USB_INTERNAL` | USB-C direkt auf Seed3 |
| `daisy_toy_piano_USB_EXTERNAL` | Externer Desktop-USB-C J7 |

Alle Images: Seed3 Desktop Dev Kit, BOOT_NONE, `0x08000000`, STM32-ROM-DFU.
Keine Hardwareprüfung erfolgt. Anschlüsse und Versorgung vor dem Flashen
anhand `docs/HARDWARE_CONNECTION.md` prüfen. Keine Images für Field, Pod oder Patch.

`host-tests.log` und `micropython-tests.log` dokumentieren lokal bestandene
Softwareprüfungen. Die Dateien entstehen erneut durch die angegebenen Befehle.
