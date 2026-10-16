# Testprotokoll v0.1.0-alpha

Datum: **16.10.2026**. Umgebung: Codex Cloud, Linux x86_64.
Es waren **keine echten Daisy-/Tulip-Geräte angeschlossen**. Alle nachfolgenden
„BESTANDEN“-Aussagen beziehen sich ausschließlich auf Software-/Buildprüfungen.
Hardwareabnahme A–D ist **OFFEN**.

## Softwareprüfungen

| Prüfung | Ergebnis | Beleg / Grenze |
|---|---|---|
| libDaisy und DaisySP | BESTANDEN | Echte gepinnte offizielle Quellen mit ARM-GCC gebaut, keine Ersatz-Hardwarebibliothek |
| Firmware DIN | BESTANDEN | Vollständiger Crossbuild/Link; `.bin`, `.elf`, `.map` vorhanden |
| Firmware USB_INTERNAL | BESTANDEN | Vollständiger Crossbuild/Link für internen Seed3-Port |
| Firmware USB_EXTERNAL | BESTANDEN | Vollständiger Crossbuild/Link für Desktop J7 |
| C++-Kern mit ASan/UBSan | BESTANDEN | Echter DaisySP-Oszillator und echter libDaisy-MIDI-Parser, kein gemeldeter Sanitizerfehler |
| MIDI-Routing | BESTANDEN | Kanalfilter, Running Status mit eingestreutem Realtime-Byte, Velocity-0-Note-Off, CC20/21, Ping, CC120/123 als ChannelMode |
| Haltezustände / LEDs | BESTANDEN | Zwei physische C5 plus überlappende MIDI-C5, kein Fremd-Note-Off, kein Unterlauf, Sättigung bei 255 |
| Pickup | BESTANDEN | Auf-/Abwärtskreuzen, Rauschhysterese und Remote-Wert vor erster Poti-Abtastung |
| AD / DSP | BESTANDEN | Stetiger Retrigger, 16 verschiedene Stimmen, begrenzter Summenpegel, endliche AD, genau 192.000 Samples bei 1000+3000 ms |
| Anschlag-Warteschlange | BESTANDEN | FIFO, volle Queue, Ringumlauf; kein Last-/Race-Stresstest auf MCU |
| Python-Controller und UI-Events | BESTANDEN | 11 unittest-Fälle; Session, alle 16 Tasten, Rate Limit, Feedback, Timeout/Reconnect, Zeitüberlauf, Cleanup |
| MicroPython-App | BESTANDEN (Syntax) | Alle fünf Dateien mit `mpy-cross` aus Tulips MicroPython-Commit übersetzt, `.mpy` v6.3 |
| LVGL-API-Prüfung | BESTANDEN (Quellprüfung) | Aktuellen Binding-C-Code aus Referenzheadern generiert; Timer-Create/Delete und verwendete native APIs vorhanden. Kein Render-/Touchtest |
| Wiederholter Firmwarebuild | BESTANDEN | Alle neun `.bin`-/`.elf`-/`.map`-Prüfsummen im selben Workspace unverändert nach sauberem Firmware-Rebuild |
| GitHub Actions | BESTANDEN | [Build and test #38962782176](https://github.com/sscheidl/Daisy-on-Tulip/actions/runs/38962782176): Hosttests, MicroPython, alle drei Firmwarebuilds und Artefakt-Upload erfolgreich |
| GitHub Repository | ZUGRIFF BESTÄTIGT | `sscheidl/Daisy-on-Tulip` ist privat; Pull-/Push-Rechte nach Freigabe bestätigt |
| GitHub Release | VERÖFFENTLICHT | [Privater Alpha-Prerelease](https://github.com/sscheidl/Daisy-on-Tulip/releases/tag/v0.1.0-alpha), 14 hochgeladene Assets; Firmware-/Manifest-Prüfsummen bestätigt |
| GitHub Release-Upload | BESTANDEN | [Publish alpha release #38963692445](https://github.com/sscheidl/Daisy-on-Tulip/actions/runs/38963692445): Upload über Repository-Token erfolgreich |
| Vergleich lokaler / GitHub-BINs | BESTANDEN | Alle drei aus dem Actions-Artefakt geladenen BIN-Dateien sind SHA-256-identisch mit den lokalen Release-Images |

Logs liegen im Komplettpaket unter `artifacts/host-tests.log`,
`micropython-tests.log`, `build-*.log`, `crossbuild-summary.log` und
`reproducibility.log`. `manifest.json` enthält die Quellen-/Artefakt-Prüfsummen
und exakten Abhängigkeits-Commits. `github-ci-verification.log` dokumentiert den
Abgleich der drei CI-Binärdateien. Der GitHub-Lauf prüfte Code-Commit
`b75f584d45b871598c3437ef59b19ba20b952575`; nachfolgende Änderungen betreffen Dokumentation, die Release-Automatisierung
und die Ablage der bereits geprüften Artefakte. Firmware- und App-Quellen sind
unverändert.

## Speicherbedarf der fertigen Images

| Backend | `.bin` / Flash | Anteil von 128 KiB | SRAM laut Linker | RAM_D2 |
|---|---:|---:|---:|---:|
| DIN | 99.716 Byte | 76,08 % | 55.548 Byte | 17.096 Byte |
| USB_INTERNAL | 112.852 Byte | 86,10 % | 106.984 Byte | 18.084 Byte |
| USB_EXTERNAL | 112.860 Byte | 86,11 % | 106.984 Byte | 18.084 Byte |

Alle passen in den offiziellen BOOT_NONE-Linkerbereich des STM32H750.
Die USB-Variante enthält zusätzlich die USB-MIDI-Handlerdaten. Es wird kein
QSPI-/SDRAM-Bootloader benötigt. Künftige größere Engines werden das interne
128-KiB-Fenster wahrscheinlich überschreiten; dann ist die normale Daisy-
Bootloader-/QSPI-Strategie eine spätere Buildentscheidung.

Toolchain: **xPack ARM GCC 14.2.1-1.1**, Cortex-M7, FPv5-D16 Hard Float,
C++14. Die Enum-ABI wurde an App-, MIDI-Parser- und Desktop-Hardware-Objekten
gegengeprüft: überall ARM-EABI `enum_size: small`.
Der identische Wiederholungsbuild gilt für denselben Workspace/Toolchainstand;
ELF-/Map-Debugpfade können sich auf anderen Rechnern unterscheiden.

## Bekannte Buildhinweise

Die unveränderten offiziellen Bibliotheken/Newlib/Linkerskripte erzeugen unter
diesem GCC einige Hinweise: nicht implementierte `nosys`-Datei-I/O-Stubs,
RWX-LOAD-Segment im Standard-Linkerskript und ein Hinweis zu FP-Registern in
einem libDaisy-Interrupt-Handler. Die Firmware benutzt keine Datei-I/O im
Audiopfad. Diese Hinweise wurden nicht versteckt oder als Fehlerfreiheit der
Hardware interpretiert. In den eigenen Hosttest-Dateien gilt `-Werror`.

## Noch nicht nachgewiesen

| Hardwarestufe | Status | Was fehlt |
|---|---|---|
| A – Standalone Daisy | OFFEN | Alle 16 Taster/LEDs am realen Kit, beide Potis, tatsächliches Stereo-/Kopfhörersignal, Audiostabilität |
| B – MIDI | OFFEN | Elektrische DIN-Kommunikation; USB-Enumeration am richtigen Port; reale CC-/Notenausgabe; Audio unter MIDI-Last |
| C – Tulip GUI | OFFEN | `mpremote resume` auf vorhandenem Gerät, App-Start in Standardfirmware, echtes Layout, Tap-/Release-Latenz, Taskwechsel/Beenden |
| D – Integration | OFFEN | Gemeinsames Spiel, tatsächliches Pickup, Rückmeldungen, Kabelabbruch in beiden Richtungen, Replug, Langzeittest |
| Strom / USB | OFFEN | Tatsächlicher Revisionsstand, Netzteil-/Host-Strombudget und Messungen zur Rückspeisung |

Die ausführbaren manuellen Schritte stehen in `TEST_PLAN.md` und der CSV-
Checkliste. Benötigt werden beide Geräte, zwei Type-A-Adapter, zwei DIN-Kabel,
separate geeignete Netzteile, Daisy-Abhöre und ein Rechner nur für Installation/
Messung. Für USB zusätzlich richtige Datenkabel/Hostadapter und gegebenenfalls
ein geeigneter aktiver Hub sowie Strommessmöglichkeit.

## Wesentliche Einschränkungen

- **Kein Hardware-Kompatibilitätsnachweis** in dieser Cloud-Sitzung.
- DIN ist bevorzugt; USB-MIDI hat ein dokumentiertes natives Tulip-Wait-/
  Hotplug-Risiko. Keine Tulip-Firmware wurde geändert.
- Native LVGL-Pointeranbindung verwendet einen Finger; keine unabhängigen
  Mehrfinger-Akkorde. Daisy-Hardware und Touch können sich ergänzen.
- 7-Bit-CCs, One-Shot-AD, keine Velocity-Dynamik, keine Effekte oder Presets.
- Gleiche Tonhöhen teilen eine Stimme; die 17. neue Tonhöhe während 16
  laufender Ausklänge wird verworfen. Queue-Überlast verwirft Anschläge.
- Ping/Pong identifiziert nur die antwortende Anwendung auf Kanal 1, keinen
  eindeutigen USB-Gerätetyp. Keine automatische Transportwahl.
- Physisches Tastenspiel wird nicht als MIDI-Note an Tulip zurückgespiegelt;
  GUI-Hervorhebung zeigt eigene Touch-Tasten. Parameter werden bidirektional
  synchronisiert; Daisy-LEDs zeigen beide Eingabearten.

Die Software ist als Alpha-Prototyp und Grundlage für modulare Synthparameter
bereit. Der vollständige Abnahmestatus bleibt bis zu den echten Gerätetests offen.
