# Testplan A–D

Alle Hardwarepunkte sind zunächst **OFFEN**. Ein Softwaretest ersetzt weder
Anschließen noch Hören oder Messen. Pro Durchlauf Datum, Geräte-/Platinenrevision,
Tulip-Firmwarestand, Daisy-Artefakt und SHA-256, Kabel/Adapter und Netzteile
notieren. Ergebnisse in `TEST_RESULTS.md` nachtragen; Vorlage:
`tests/hardware_checklist.csv`.

## Automatisiert in der Cloud

```sh
python3 scripts/bootstrap.py
bash scripts/test.sh
python3 scripts/check_micropython.py
bash scripts/build.sh
```

- C++-Hosttest mit AddressSanitizer und UndefinedBehaviorSanitizer:
  echte DaisySP-Oszillatoren, libDaisy-MIDI-Parser, Protokoll, doppelte C5,
  Referenzzähler, Velocity-0-Note-Off, Überlaufbegrenzung, Pickup in beide
  Richtungen, LEDs, Timeout über Zeitüberlauf, AD-Zeiten, glatter Retrigger,
  16 Stimmen, keine Übersteuerung, Warteschlangenreihenfolge/-überlauf.
- Python-Controller: alle 16 Noten, Session, Pending-CC-Zusammenfassung,
  Rückmeldung ohne Echo, Timeout/Reconnect, Lebenszyklus, Zeitüberlauf.
- Tatsächliche App-Callbacks mit Event-Testdoubles: PRESSED/RELEASED/PRESS_LOST,
  doppelte Press-/Click-Events, Slider und Timer-Cleanup auch nach Teilstart.
- MicroPython-Bytecodeübersetzung aller fünf App-Dateien aus Quellen.
- Crossbuild und Link von DIN, USB_INTERNAL und USB_EXTERNAL gegen die echten
  offiziellen Bibliotheken. Flash-/RAM-Auslastung und Prüfsummen speichern.

Diese Tests prüfen keine reale GPIO-/I2C-/Touch-/USB-/Audio-Hardware. Die
GitHub-Actions-Ausführung muss nach erfolgreicher Repository-Übernahme separat
beobachtet werden.

## Stufe A – Daisy eigenständig

Firmware DIN installieren, Tulip und MIDI-Kabel abziehen. Desktop separat an J7
versorgen. Beide Line-Outs oder Kopfhörer verwenden.

| ID | Aktion | Erwartung |
|---|---|---|
| A1 | Taster 1–16 einzeln anschlagen | Richtige Tonfolge laut Notenplan, jede zugehörige LED reagiert; kein Doppeltrigger bei langem Halten |
| A2 | Taster 8 und 9 separat und überlappend | Beide ergeben C5; Loslassen eines Tasters löscht den anderen nicht |
| A3 | Acht und dann möglichst 16 Taster gleichzeitig | Mehrstimmiger Klang; kein Absturz, keine harten Pegelsprünge |
| A4 | Poti 1 und 2 von Minimum bis Maximum | Attack etwa 1–1000 ms, Decay etwa 20–3000 ms; Änderungen gelten für neue Anschläge |
| A5 | Taste kurz/mehrere Sekunden halten und lösen | AD läuft einmal aus; LED bleibt nur während Halten; kein unendlicher Ton |
| A6 | Beide Stereoausgänge aufnehmen | L und R tragen identisches Signal; keine hörbaren Aussetzer; Kopfhörerregler prüfen |
| A7 | 30 Minuten Spielen/Regeln | Keine hängenden LEDs, kein Knacksen beim Retrigger, stabiler Pegel |

## Stufe B – Kommunikationsnachweis

Zunächst DIN verwenden, optional einen eigenständigen MIDI-Controller oder einen
Rechner nur zum Testen anschließen. Danach USB-Varianten getrennt prüfen.

| ID | Aktion | Erwartung |
|---|---|---|
| B1 | Kanal 1 Note-On 60/100, Note-Off 60/0 | C4 erklingt, LED1 an/aus; AD darf nach Note-Off ausklingen |
| B2 | Note-On mit Velocity 0; fremden Kanal 2 senden | Kein neuer Ton; fremder Kanal steuert Engine nicht |
| B3 | C5 zweimal Note-On, einmal Note-Off | Beide C5-LEDs bleiben bis zum zweiten Note-Off aktiv |
| B4 | CC20/21 = 0/127 | Endwerte der Hüllkurven; physische Potis bleiben bis Pickup wirkungslos |
| B5 | CC118=42 senden und Rückkanal mitschneiden | CC119=42, CC20 und CC21 kommen zurück |
| B6 | CC123 und CC120 nach externen Noten | Externe LEDs aus; physische Tasten bleiben aktiv; endliche Ausklänge erlaubt |
| B7 | USB_INTERNAL am Seed-Port; USB_EXTERNAL an J7 | Jeweils richtige Enumeration, IN/OUT und richtige Firmware; falsche Portvariante ergibt keine passende Session |
| B8 | MIDI-Last: 50 CC/s plus Noten, Audio aufnehmen | Kein hörbarer Aussetzer; bei USB zusätzlich Audio-DMA-Zeit prüfen |

USB-Tests benötigen den Stromplan aus `HARDWARE_CONNECTION.md`. Replug bei
laufendem Tulip-USB-Tx ist ausdrücklich ein Risikotest; ein Hänger ist ein
Fehlschlag, kein „bestanden mit Einschränkung“.

## Stufe C – native Tulip-App

App mit `mpremote resume` kopieren, ohne Standardfirmware zu ersetzen. Vollständiges
bidirektionales DIN-MIDI anschließen.

| ID | Aktion | Erwartung |
|---|---|---|
| C1 | `tulip.run('daisy_toy_piano')` | 1024×600-Layout, 16 lesbare Tasten, zwei Slider, kein WLAN nötig |
| C2 | Jede Taste drücken, halten, lösen | Ein Note-On/Off-Paar, sichtbare Hervorhebung |
| C3 | Finger von Taste ziehen, sehr kurze Taps | Kein Hängen; Drag-off endet per PRESS_LOST; schnelle Taps hörbar |
| C4 | Slider rasch und langsam bewegen | Werte in ms; höchstens 25 CC/s je Slider; letzter Wert wird übertragen |
| C5 | Ctrl-Tab / native Task-Umschaltung beim Halten | Note-Offs und CC123; im Hintergrund keine neuen Anschläge |
| C6 | Ctrl-Q / Power-Symbol, dann erneut starten | Keine alten Tasten; kein verbliebener Timer/MIDI-Callback; kein Absturz |
| C7 | Zwei und drei Finger auf getrennte Tasten | Aktuelle native Implementierung bietet keine unabhängigen Multi-Touch-Noten; Einschränkung bestätigen und Fingerwechsel beobachten |
| C8 | Ohne Daisy starten, nur ein MIDI-Kabel anschließen | Klare Offline-Meldung; keine fälschliche Verbindungszusage; virtuelle Tasten gesperrt |

## Stufe D – Integration

| ID | Aktion | Erwartung |
|---|---|---|
| D1 | Daisy und Touch abwechselnd/gemeinsam spielen | Richtige Töne, keine verlorenen Hardwaretasten |
| D2 | Hardware-C5 halten, Touch-C5 spielen und lösen, Reihenfolge umkehren | Keine fremde Quelle wird durch Note-Off gelöscht |
| D3 | Touch-Attack ändern, physisches Poti fern vom neuen Wert bewegen, dann darüber hinweg | Kein Parametersprung bis Pickup; danach aktuelle Werte im GUI |
| D4 | Physische Potis schnell bewegen, anschließend GUI-Slider | Rückmeldung stabil, kein Echo/Flood; sinnvoller neuer Anschlag |
| D5 | Beide MIDI-Kabel bzw. USB während Halten abziehen | Offline nach etwa 1,6 s; externe LEDs bereinigt; Audio spätestens nach AD aus; Hardware bleibt spielbar |
| D6 | Jede MIDI-Richtung einzeln unterbrechen | Kein dauerhaft festgehaltener Remote-Zustand; Status geht nach Timeout offline |
| D7 | Wiederverbinden, 20-mal wiederholen | Automatische Session-Rückkehr; keine alten Noten/Slider-Kommandos; neue Anschläge möglich |
| D8 | 60 Minuten kombinierte Bedienung, 16-Stimmen-Audio mitschneiden | Stabile Ausgabe ohne Dropouts; Debugzähler bei normaler Bedienung unauffällig |
| D9 | USB-Strom-/Ausschaltzustände messen | Keine Rückspeisung entgegen Datenblatt/Hub-Spezifikation, keine Unterspannung; konkrete Messwerte protokollieren |

Abnahme: A, B, C und D jeweils separat bewerten. DIN darf als erster
Hardwareprototyp abgenommen werden, während USB-Hotplug weiterhin offen/fehlgeschlagen
bleibt. Nicht unterstütztes Mehrfingertouch bleibt als Produktgrenze sichtbar.
