# Daisy on Tulip – Touchscreen Control for Daisy Seed3

Ein Machbarkeitsprototyp für das **Electro-Smith Seed3 Desktop Development Kit**
und den **Tulip Creative Computer**. Daisy erzeugt den gesamten Klang; Tulip
ist eine native MIDI-Bedienoberfläche. Version: **v0.1.0-alpha**.

**Stand:** Drei Firmware-Varianten sind kompiliert, C++-DSP und Python-Steuerlogik
sind automatisiert getestet. Ein Test an echten Geräten steht aus. Es gibt
noch keinen belegten Hardware-Kompatibilitätsnachweis. Siehe [Testprotokoll](docs/TEST_RESULTS.md).

**Empfehlung für den ersten Aufbau:** bidirektionales **TRS-Type-A/DIN-MIDI**.
Tulips Standardfirmware genügt nach Quellprüfung. USB-MIDI ist als Alternative
implementiert und auf Deskriptor-/Portebene geprüft; Hotplug im aktuellen Tulip-
USB-Sendepfad bleibt ein Risiko. Native LVGL-Tasten arbeiten mit einem Touchpunkt;
Mehrfinger-Akkorde sind in dieser App nicht verfügbar. Hardware-Akkorde funktionieren
in der implementierten 16-stimmigen Engine. [Machbarkeitsstudie](docs/FEASIBILITY_DE.md).

## Schnellstart mit fertigen Dateien

1. Beide Geräte ausschalten. Zwei **3,5-mm-TRS-Type-A-auf-DIN-Adapter** und zwei
   DIN-MIDI-Kabel verbinden: Tulip OUT → Daisy IN und Daisy OUT → Tulip IN.
2. Daisy über den **externen Desktop-USB-C-Port** mit einem geeigneten 5-V-Netzteil
   versorgen. Tulip separat am PWR/Charge/Program-Port versorgen. Audio oder
   Kopfhörer ausschließlich an Daisy anschließen; Lautstärke zunächst niedrig.
3. Mit dem [Daisy Web Programmer](https://flash.daisy.audio/) die Datei
   `artifacts/daisy_toy_piano_DIN.bin` im STM32-ROM-DFU-Modus über den
   **internen Seed3-USB-C-Port** laden. BOOT halten, RESET kurz drücken,
   dann BOOT loslassen. Diese BOOT_NONE-Datei beginnt bei `0x08000000` und benötigt
   keinen zusätzlichen Daisy-Bootloader. Der Rechner ist danach entbehrlich.
4. Tulip per Datenkabel am PWR/Charge/Program-Port mit dem Rechner verbinden:

   ```sh
   python3 -m pip install mpremote
   python3 scripts/install_tulip.py --port auto
   ```

5. Im Tulip-REPL starten:

   ```python
   import tulip
   tulip.run('daisy_toy_piano')
   ```

6. Nach spätestens etwa zwei Sekunden sollte „Daisy verbunden / MIDI 1“ erscheinen.
   Ohne Antwort bleiben die virtuellen Tasten gesperrt und die Meldung
   „Daisy nicht verbunden / Kabel pruefen“ sichtbar. Physische Taster funktionieren
   unabhängig von Tulip. Zum Beenden das native Power-Symbol oder Ctrl-Q verwenden.

Details: [Anschluss und Flashen](docs/HARDWARE_CONNECTION.md),
[USB-Installation der Tulip-App](docs/TULIP_INSTALL.md), [Tests A–D](docs/TEST_PLAN.md).
WLAN, AMYboard, Browser-GUI und eine Tulip-Neuinstallation werden nicht benötigt.

## Instrument

- 16 Taster: `C4 D4 E4 F4 G4 A4 B4 C5 | C5 D5 E5 F5 G5 A5 B5 C6`.
  `B` bezeichnet das deutsche `H`. C5 ist zweimal erreichbar.
- 16 Sinusstimmen bei 48 kHz, gleiches Monosignal auf beiden Daisy-Ausgängen.
- Poti 1: Attack 1–1000 ms; Poti 2: Decay 20–3000 ms; logarithmische Kennlinie.
- AD läuft pro Anschlag einmal aus. Loslassen löscht die gehaltene Note/LED;
  der endliche Klang läuft weiter. Erneutes Anschlagen startet die Hüllkurve
  kontinuierlich von ihrem aktuellen Pegel.
- Gleiche Tonhöhen teilen sich eine Stimme, werden aber je Quelle/Taste gezählt.
  Überlappende Note-Offs löschen keine andere gehaltene Quelle.
- Physische LEDs sind individuell; ein externes C5 beleuchtet beide passenden LEDs.
- Pickup verhindert Sprünge nach MIDI-Regleränderungen. Ein physisches Poti
  übernimmt erst nahe am Zielwert oder beim Überschreiten dieses Werts.
- Es gibt kein hartes Voice Stealing: Sind 16 verschiedene Ausklänge aktiv,
  wird ein weiterer neuer Ton verworfen. Der normale Tastenplan umfasst 15 Tonhöhen.

## Selbst bauen

Linux x86_64, Git, GNU Make, Python 3, curl, tar und ein Host-C++-Compiler:

```sh
bash scripts/install_toolchain.sh
python3 scripts/bootstrap.py
bash scripts/test.sh
python3 scripts/check_micropython.py
bash scripts/build.sh
```

Alle Abhängigkeiten sind in [dependencies.lock.json](dependencies.lock.json) auf
konkrete offizielle Commits festgelegt. Die ARM-GCC-Distribution ist auf
xPack 14.2.1-1.1 inklusive SHA-256 festgelegt. `build.sh` baut DIN, USB_INTERNAL
und USB_EXTERNAL und erzeugt `.bin`, `.elf`, `.map`, Prüfsummen und Manifest.
Einzelbuild nach dem Bibliotheksbuild:

```sh
export PATH="$PWD/.tools/xpack-arm-none-eabi-gcc-14.2.1-1.1/bin:$PATH"
make -C daisy MIDI_BACKEND=DIN
```

Der Build nutzt `desktop_devkit::Hardware`, keine Field-/Pod-/Patch-Pinbelegung.
Die Bibliothek erkennt Seed3 und dessen TAC5242-Codec zur Laufzeit. Ein
[GitHub-Actions-Workflow](.github/workflows/build.yml) baut und testet bei Push/PR;
er wurde in dieser Sitzung noch nicht auf GitHub ausgeführt.

Konfiguration: [config/protocol.json](config/protocol.json) ändern und
`python3 scripts/generate_protocol.py` ausführen. Daraus entstehen dieselben
Noten, CCs, Zeiten und MIDI-Kanäle für C++ und MicroPython.

## Übergabe / GitHub

Das Erstellen eines privaten Repositories `sscheidl/Daisy-on-Tulip` wurde am
16.10.2026 versucht und von GitHub mit **HTTP 403: Resource not accessible by
integration** abgelehnt. Daher wurde kein Remote-Repository und kein GitHub-
Release erstellt. Das lokale Repository besitzt den Alpha-Tag; Quellarchiv,
Git-Bundle und Firmware-Artefakte liegen zur Übernahme bereit.

Mit einer GitHub-Anmeldung, die neue private Repositories erstellen darf:

```sh
bash scripts/publish_github.sh
```

Das Skript erstellt ausschließlich ein neues privates Repository und einen
Prerelease mit Artefakten. Ein vorhandenes Repository wird nicht überschrieben.
Siehe [GitHub-Blocker](docs/GITHUB_HANDOFF.md) und [Release-Hinweise](docs/RELEASE_NOTES.md).

Architektur und Erweiterungspunkte: [ARCHITECTURE.md](docs/ARCHITECTURE.md).
Protokoll: [MIDI_PROTOCOL.md](docs/MIDI_PROTOCOL.md).
Lizenzen der eingebundenen Bibliotheken: [THIRD_PARTY_NOTICES.md](docs/THIRD_PARTY_NOTICES.md).
