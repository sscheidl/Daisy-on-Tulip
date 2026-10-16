# Technische Machbarkeitsstudie

Stand 16.10.2026, Quellprüfung vor der Implementierung. Grundlage sind die
Commits in `dependencies.lock.json`; die konkreten Geräte standen nicht zur
Verfügung. „Quellseitig kompatibel“ bedeutet ausdrücklich keinen bestandenen
Enumeration-, Strom-, Latenz- oder Audiotest auf Hardware.

## Entscheidung

Für v0.1 wird **bidirektionales TRS-Type-A/DIN-MIDI** empfohlen. Dafür sind alle
Schnittstellen bereits vorhanden, keine Modifikation oder neue Firmware auf
Tulip nötig, und die Stromversorgung bleibt einfach getrennt. USB-MIDI erhält
zwei eigenständig kompilierte Backends zum gezielten Testen. Ein späterer Wechsel
verändert weder GUI noch Synthese-Engine.

| Variante | Realisierbarkeit / Kabel | Rückkanal | Latenz / Zuverlässigkeit | Aufwand / spätere GUI |
|---|---|---|---|---|
| USB-MIDI | Tulip USB-KB ist Host; Seed3 ist MIDI-Device. Datenkabel mit passender Host-Steckerausführung, am Seed oder Desktop-Port unterschiedliche Firmware nötig. Strombudget prüfen. | Ein Kabel, Bulk IN + OUT | Full Speed, typischer USB-Frame 1 ms; End-to-End-Latenz ungemessen. Tulip kann beim Senden unbegrenzt warten; Replug offen. | Geringer App-Aufwand, höheres Hotplug-/Stromrisiko. Gute Bandbreite für viele Regler, ein USB-MIDI-Gerät im untersuchten Treiber. |
| TRS/DIN-MIDI | Zwei Type-A-TRS/DIN-Adapter und zwei DIN-Kabel. Desktop-MIDI ist schon korrekt in der Hardware-Abstraktion konfiguriert. | Zwei getrennte Leitungen | 31.250 Baud, 10 Bit/Byte, 0,96 ms je 3-Byte-Nachricht. Kein USB-Enumeration-/VBUS-Problem. Tatsächliche Touch-/Audio-Latenz ungemessen. | Kleinster Aufwand, sehr gut für Noten und einige Dutzend Parameter. Größere Dumps benötigen Drosselung/ggf. NRPN oder SysEx. |
| TTL-UART direkt | Technisch 3,3-V-UART möglich, aber keine vorgesehenen TTL-Buchsen zwischen den Geräten. Daisy D13/D14 sind bereits an MIDI-Schaltungen gebunden. Zusätzliche Verdrahtung und Pin-/Pegelprüfung nötig. | RX, TX und gemeinsame Masse | Frei wählbare Baudrate; störanfälliger als optogekoppeltes MIDI, keine galvanische Trennung. | Ohne Hardwareeingriff kein Vorteil. Für diesen vorhandenen Aufbau verworfen; MIDI über vorhandene UART-Schaltungen ist bereits DIN/TRS. |

## USB-MIDI: konkrete Kompatibilitätskette

1. [Tulip API](https://github.com/shorepine/tulipcc/blob/17d1ef1d14aa0a51520fced04c87c1328f79bbd0/docs/tulip_api.md)
   beschreibt USB-KB als Host, TRS und USB für MIDI I/O sowie parallelen Versand
   an beide Ausgänge. Tulip ist an diesem Anschluss kein USB-MIDI-Device.
2. [Tulip usb_host.c](https://github.com/shorepine/tulipcc/blob/17d1ef1d14aa0a51520fced04c87c1328f79bbd0/tulip/esp32s3/usb_host.c)
   `check_interface_desc_MIDI()` akzeptiert Class `0x01`, Subclass `0x03`, Protocol
   `0x00`. `prepare_endpoint_midi()` erwartet Bulk-Endpunkte und richtet IN/OUT
   ein. Keine Einschränkung auf einen bestimmten Daisy-Hersteller/Produktnamen.
3. [libDaisy usbd_cdc.c](https://github.com/electro-smith/libDaisy/blob/f715e4875b2d28445d0c11a0a17f064a248f69d0/Middlewares/Patched/ST/STM32_USB_Device_Library/Class/CDC/Src/usbd_cdc.c)
   enthält trotz CDC-Dateiname die MIDI-Konfiguration `USBD_MIDI_CfgDesc`:
   MIDIStreaming `01/03/00`, zwei Bulk-Endpunkte mit 64 Byte MaxPacketSize,
   USB-MIDI-1.0-Jacks. Diese Deskriptoren erfüllen Tulips Klassentest.
4. [MidiUsbTransport](https://github.com/electro-smith/libDaisy/blob/f715e4875b2d28445d0c11a0a17f064a248f69d0/src/hid/usb_midi.cpp)
   setzt `usbd_mode = USBD_MODE_MIDI`, verpackt 3-Byte-Nachrichten in 4-Byte-
   USB-MIDI-Events und wandelt empfangene Events wieder zurück. Tulip macht
   denselben Pakettyp. `MidiUsbHandler` parst darüber Standard-MIDI-Nachrichten.
5. Seed3 nutzt weiterhin STM32H750 und USB-Device-Unterstützung der Bibliothek.
   Die Audio-Codec-Erkennung (`DAISY_SEED_3`, PH6) ist in
   [daisy_seed.cpp](https://github.com/electro-smith/libDaisy/blob/f715e4875b2d28445d0c11a0a17f064a248f69d0/src/daisy_seed.cpp)
   enthalten. Der Build muss deshalb eine aktuelle, Seed3-fähige libDaisy verwenden.

**Portauswahl ist zwingend:**

| Physischer Anschluss | STM32-Leitungen / libDaisy | Firmware |
|---|---|---|
| USB-C direkt auf Seed3 | PA11/PA12, OTG_FS, `FS_INTERNAL` | `USB_INTERNAL`, `MidiUsbTransport::Config::INTERNAL` |
| Externer Desktop-USB-C J7 | D29/D30 = PB14/PB15, OTG_HS mit internem Full-Speed-PHY, `FS_EXTERNAL` | `USB_EXTERNAL`, `...::EXTERNAL` |

Der Host-Modus `HOST` in libDaisy ist für diese Verbindung falsch: Tulip ist
bereits Host. Der Desktop-Anschluss ist kein passiver Verlängerungsanschluss
des Seed3-Ports. libDaisy initialisiert bei INTERNAL VBUS-Sensing auf PA9;
bei EXTERNAL ist VBUS-Sensing deaktiviert. Ein pauschales Datenkabel ohne VBUS
ist daher gerade am internen Anschluss keine verlässlich funktionierende Lösung.

Die Portzuordnung wurde gegen `src/hid/usb.cpp`, `src/usbd/usbd_conf.c`, das
Seed3-Datenblatt (Pins 36/37) und den Desktop-Schaltplan (J7 → USB_OTG_HS_N/P)
geprüft. Das generische
[USB_MIDI-Beispiel](https://github.com/daisyaudio/DaisyExamples/blob/259ed82c7d4c0d7699f695945e6e111b7dc7cb27/seed/USB_MIDI/USB_MIDI.cpp)
allein ist kein Nachweis für den externen Desktop-Port.

## Audio und USB gleichzeitig

Audio läuft als DMA-/SAI-Callback mit 48 Samples/Block bei 48 kHz. Dort werden
keine MIDI-Transfers, Potis, LEDs, Speicherallokationen oder GUI-Funktionen
aufgerufen. MIDI, Bedienelemente und LED-I2C laufen im Vordergrund; Anschläge
gehen über eine atomare SPSC-Warteschlange zur Audioseite. USB-Tx auf Daisy hat
`tx_retry_count = 0`; Rückmeldungen sind zusammengefasst und zeitlich begrenzt.
Die Firmware stuft USB-Interrupts von libDaisys Defaultpriorität 0 auf 1 zurück,
sodass die Audio-DMA-Interrupts mit Priorität 0 Vorrang haben.
Damit ist gleichzeitiger Betrieb auf Quell-/Build-Ebene vorgesehen. Interrupt-
Latenz, USB-Last, Codec-Ausgabe und Aussetzer müssen am Gerät gemessen werden.

## Verbindungsabbruch / Wiederverbindung

Tulips `USB_HOST_CLIENT_EVENT_DEV_GONE` setzt `midi_claimed`, `midi_ready`,
`midi_has_in` und `midi_has_out` zurück. Neue Geräte werden erneut geöffnet;
Puffer werden wiederverwendet. Das ist implementierte Wiederanlauf-Logik,
aber noch kein Dauertest mit Daisy.

Ein konkretes Risiko: `midi_out_transfer()` ruft
`usb_host_transfer_submit(MIDIOut)` auf und wartet anschließend mit
`ulTaskNotifyTake(pdTRUE, portMAX_DELAY)` **vor** der Prüfung eines Submit-Fehlers.
Bei Fehler oder ausbleibendem Abschluss kann der MicroPython-Aufruf blockieren.
Die App kann einen bereits blockierten nativen Aufruf nicht durch ihren eigenen
Timer beenden. Deshalb gehört USB-Hotplug noch nicht zum zugesicherten Verhalten;
DIN ist der v0.1-Standard. Es wird keine Tulip-Firmwareänderung verlangt.

Daisy löscht MIDI-Haltezustände nach 1600 ms ohne gültige Session-Nachricht;
Tulip erkennt fehlende Daisy-Antworten ebenfalls nach 1600 ms. Das benötigt keine
USB-Verbindungs-API. Nach Wiederverbindung wird der Daisy-Parameterstand gelesen,
keine alte Taste neu angeschlagen. Klang ist durch AD ohnehin auf höchstens
Attack + Decay begrenzt. Details im [Protokoll](MIDI_PROTOCOL.md).

## Stromversorgung

Der [Desktop-Schaltplan, Rev3](https://daisy.nyc3.cdn.digitaloceanspaces.com/products/seed-3-desktop/ES-Seed3-DevKit-Desktop-Rev3.pdf)
zeigt J7-VBUS als `+5V_USB`, danach einen Boost für Trägerplatine, analoge
Schaltungen und `DSY_VIN`. Ein Rechner-/Host-Anschluss kann dadurch mehr als nur
den Seed versorgen müssen. Tulips erlaubte Hostlast ist hier nicht belastbar
nachgewiesen. Ein direkter Betrieb des kompletten Kits aus Tulips USB-KB wird
deshalb nicht als stromseitig freigegeben dargestellt.

Das [Seed3-Datenblatt, S. 10–11](https://daisy.nyc3.cdn.digitaloceanspaces.com/products/seed3/Daisy_Seed3_datasheet.pdf)
beschreibt den internen USB-Eingang ausdrücklich als rückspeisegeschützt und
parallel zu VIN verwendbar. Damit ist ein sinnvoller USB-Testaufbau: Desktop J7
aus eigenem 5-V-Netzteil, Tulip Host → interner Seed3-USB-C mit normalem Datenkabel,
Firmware USB_INTERNAL. VBUS-Sensing bleibt erhalten. Diese Aussage gilt für
**Seed3**; tatsächliche Platinenrevision und Netzteile vor Ort abgleichen.

Der empfohlene DIN-Aufbau braucht keinerlei USB-Verbindung zwischen den Geräten.
Beide separat regulär versorgen. Keine Y-Kabel, keine zusammengeführten 5-V-
Ausgänge, keine improvisierte VIN-Einspeisung. Ein USB-Test am externen J7 benötigt
eine einzige ausreichend dimensionierte Hostversorgung, gegebenenfalls einen
geeigneten rückspeisegeschützten aktiven Hub. Siehe [Anschlussplan](HARDWARE_CONNECTION.md).

## Native Tulip-GUI und Touch

Geprüft wurden `tulip/shared/py/ui.py`, `juno6.py`, `drums.py`, `voices.py` und
[`tulip/fs/tulip/ex/buttons.py`](https://github.com/shorepine/tulipcc/blob/17d1ef1d14aa0a51520fced04c87c1328f79bbd0/tulip/fs/tulip/ex/buttons.py).
`UIScreen` verwaltet Taskwechsel, Darstellung und Beenden. `UIButton`,
`UISlider` und `UILabel` sind vorhandene native LVGL-Wrapper. LVGL 9 wird verwendet;
Montserrat 24 ist in der Tulip-Konfiguration aktiviert.

`UIButton(callback=...)` bindet ausschließlich `lv.EVENT.CLICKED`.
Das reicht nicht für eine Instrumententaste. Die App verwendet deshalb den
Wrapper für Darstellung und das darunterliegende `.button` für `PRESSED`,
`RELEASED`, `PRESS_LOST`. Wiederholungs-/Click-Events erzeugen keine zusätzlichen
Noten. Die Buttons haben kein PRESS_LOCK; Wegziehen beendet die Note.

**Mehrfingertouch:** Der GT911-Treiber liest bis zu drei Punkte und
`tulip.touch()` gibt drei Koordinatenpaare aus. Die tatsächliche native
LVGL-Eingabefunktion `lvgl_input_read_cb()` in
[`display.c`](https://github.com/shorepine/tulipcc/blob/17d1ef1d14aa0a51520fced04c87c1328f79bbd0/tulip/shared/display.c)
übergibt jedoch ausschließlich `last_touch_x[0]`, `last_touch_y[0]` als einen
Pointer. Weitere Finger sind damit keine unabhängigen LVGL-Tastendrücke.
Außerdem bleiben Rohkoordinaten nach vollständigem Loslassen teilweise stehen;
blindes Polling von `tulip.touch()` wäre kein zuverlässiger Ersatz.

v0.1 bleibt bei nativen Widgets und einem Finger. Mehrfinger-Akkorde und
gleichzeitiges Touch-Spiel plus Slider mit einem zweiten Finger sind nicht
zugesichert. Hardware-Taster können parallel zum Touch verwendet werden.
Ein zukünftiger Multitouch-Pfad bräuchte stabile Kontakt-/Release-Zustände und
eigene Hit-Tests oder zusätzliche native Eingabegeräte; er ist bewusst kein
Teil dieses einfachen Prototyps.

## Offene Nachweise

- Konkrete Firmwareversion und Platinenrevision beider vorhandenen Geräte.
- USB-Enumeration an beiden korrekt konfigurierten Ports und bidirektionale Daten.
- USB-Stromaufnahme / Anlaufspitzen / tatsächliches Rückspeiseverhalten.
- Reconnect bei laufendem USB-Tx, mindestens 20 Steckzyklen.
- Touch-Latenz, schneller Tap, Drag-off, Taskwechsel und langes Halten.
- Reale Taster-/LED-Reihenfolge, Potirichtung, Audio auf Line-Out und Kopfhörer.

Die Architektur eignet sich als Ausgangspunkt für mehr Syntheseparameter und
Module. MIDI 1.0 mit 7-Bit-CC reicht für diesen AD-Prototyp; feinere Regler,
umfangreiche Zustandsabbilder und Presets werden spätere Protokollerweiterungen
benötigen. Die Quellprüfung rechtfertigt keinen Anspruch auf bereits bewiesene
Hardwarefunktion.
