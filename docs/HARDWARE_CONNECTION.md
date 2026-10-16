# Anschließen und Daisy flashen

Zielhardware: **Seed3 auf dem Desktop Development Kit**, 16 Taster, 16 LEDs,
8 Potis, DIN-MIDI. Keine Daisy-Field-/Pod-/Patch-Verdrahtung verwenden.
AMYboard bleibt für dieses Projekt unverbunden; Ton kommt ausschließlich von Daisy.

## Empfohlen: zwei MIDI-Leitungen

```text
Tulip MIDI OUT (TRS Type A) ── Adapter + DIN-Kabel ──> Desktop MIDI IN
Tulip MIDI IN  (TRS Type A) <── Adapter + DIN-Kabel ── Desktop MIDI OUT

5-V-Netzteil ──> externer Desktop-USB-C-Port J7
Eigenes Netzteil / Akku ──> Tulip PWR/Charge/Program
Daisy Line-Out L/R oder Daisy Kopfhörer ──> Abhöre
```

1. Ausgeschaltet verkabeln; MIDI IN/OUT nicht vertauschen. Type-A-Adapter
   verwenden, nicht Type B und kein analoges TRS-Audiokabel zum DIN-Port.
2. Daisy über den **externen Desktop-Port** regulär versorgen, damit auch
   Trägerplatinen-Analogschaltungen und Kopfhörerverstärker versorgt werden.
   Geeignetes 5-V-Netzteil gemäß tatsächlichem Kit verwenden. Keine höhere
   Spannung an USB einspeisen. Das Seed-VIN-Spannungsfenster gilt nicht für USB.
3. Tulip separat versorgen. DIN verbindet keine USB-5-V-Versorgungen.
4. Daisy-Ausgangspegel/Kopfhörerregler zunächst niedrig. Es ist kein
   Audiorouting von oder zu Tulip erforderlich.
5. DIN-Firmware installieren und danach Daisy zuerst allein mit allen Tastern
   und Poti 1/2 testen. Anschließend Tulip-App starten und Pong-Anzeige abwarten.

Im normalen Betrieb ist kein Rechner nötig. Ein USB-MIDI-Kabel zwischen den
Geräten bleibt bei diesem Aufbau unbenutzt. Tulips `midi_out()` sendet an TRS
**und** angeschlossene USB-MIDI-Geräte; doppelte Wege zum selben Daisy vermeiden.

## Flashen mit dem Daisy Web Programmer

1. Desktop weiter regulär versorgen. Seed3-Datenblatt bestätigt Rückspeiseschutz
   des internen Seed-USB-Eingangs bei gleichzeitigem VIN-Betrieb.
2. Den Rechner per Datenkabel mit dem **USB-C direkt auf dem Seed3** verbinden.
3. BOOT gedrückt halten, RESET kurz drücken, BOOT loslassen. Der STM32 muss als
   DFU-Gerät erscheinen. Ein Ladekabel ohne Datenleitungen funktioniert nicht.
4. In einem unterstützten Browser [flash.daisy.audio](https://flash.daisy.audio/)
   öffnen, das DFU-Gerät verbinden und die passende `.bin` auswählen.
5. Für den empfohlenen Aufbau `daisy_toy_piano_DIN.bin` laden. Danach RESET.
   **BOOT_NONE**, interne Flashadresse `0x08000000`; kein QSPI-/SRAM-Bootloader-
   Image. Ein vorhandener Daisy-Bootloader im internen Flash wird durch diese
   Instrumenten-Firmware ersetzt. Für diesen Prototyp ist er nicht erforderlich.
6. Rechnerkabel entfernen. Die Versorgung an Desktop J7 bleibt bestehen.

Alternativ mit installiertem `dfu-util` und aktiviertem DFU-Modus:

```sh
dfu-util -a 0 -s 0x08000000:leave -D artifacts/daisy_toy_piano_DIN.bin -d ,0483:df11
```

Wiederherstellung: erneut ROM-DFU über BOOT/RESET und den internen Seed-Port.
Ein fehlendes MIDI-Gerät im normalen Betriebsmodus bedeutet nicht, dass ROM-DFU
nicht mehr möglich ist.

## USB-MIDI über den internen Seed3-Port

Diese Variante ist quellseitig kompatibel, aber noch nicht physisch getestet:

```text
Eigenes 5-V-Netzteil ──> externer Desktop-USB-C J7 (Trägerplatine + Seed-VIN)
Tulip USB-KB / Host ── normales USB-Datenkabel ──> interner Seed3-USB-C
```

Firmware: **`daisy_toy_piano_USB_INTERNAL.bin`**.

Der interne Seed3-USB-Eingang ist laut Seed3-Datenblatt rückspeisegeschützt
und gleichzeitig mit VIN verwendbar. Normales Host-VBUS bleibt angeschlossen,
damit PA9-VBUS-Erkennung funktioniert. Kein pauschaler VBUS-Blocker nötig;
dieser könnte die Enumeration gerade verhindern. An tatsächlicher Seed3-
Revision und gewählten Netzteilen prüfen, dass die Datenblattbedingungen gelten.

Vom Stecker des Tulip USB-KB abhängiges Datenkabel/Hostadapter verwenden.
USB-KB ist bereits Host; keinen zweiten aktiven USB-Host anschließen.
Desktop-MIDI-Kabel während dieses Tests entfernen, um parallele Wege zu vermeiden.

## USB-MIDI über den externen Desktop-Port J7

Firmware: **`daisy_toy_piano_USB_EXTERNAL.bin`**.

J7 ist mit D29/D30 = PB14/PB15 verbunden und verwendet einen anderen USB-
Controller als der Seed-Anschluss. INTERNAL-Firmware enumeriert hier nicht.
J7 ist zugleich die 5-V-Versorgung der Desktop-Platine. Ein einfacher Anschluss
an Tulip würde somit das Kit aus dem Tulip-Host speisen. Strombudget, Einschalt-
spitzen und Audioqualität sind nicht nachgewiesen.

Für diesen Test eine einzige ausreichend leistungsfähige, spezifikationskonforme
Hostversorgung nutzen, gegebenenfalls einen passenden aktiven Hub mit Schutz
gegen Rückspeisung zum Upstream. Dessen Tulip-Kompatibilität ist separat zu
prüfen. Keinen zweiten 5-V-Ausgang über Y-Kabel mit J7 verbinden, keine
selbstgebauten Speiseweichen und keine ungemessene Hostversorgung als Standard
empfehlen. Die einfache, getrennt gespeiste DIN-Lösung bleibt der erste Aufbau.

## Revisions- und Messprotokoll

Der Hersteller verlinkt einen Rev3-Schaltplan und eine Rev4-BOM. Vor Ort die
wirkliche Platinenrevision notieren. Die Studie belegt die Signalführung des
verlinkten Schaltplans, nicht jede gefertigte Revision.

Zu erfassen: Serien-/Revisionsstand, Firmwarestände, Netzteilspannung und
Nennstrom, Stromaufnahme beim Start und bei 16 Stimmen/LEDs, Host-Port-Zustand
bei einseitig ausgeschalteten Geräten, stabile Enumeration, Audio-Brumm-/
Aussetzerverhalten. Keine Messung wurde in Codex Cloud durchgeführt.

Quellen: [Desktop Produktseite](https://docs.daisy.audio/product/Seed3-Desktop-Dev-Kit/),
[Desktop-Schaltplan](https://daisy.nyc3.cdn.digitaloceanspaces.com/products/seed-3-desktop/ES-Seed3-DevKit-Desktop-Rev3.pdf),
[Seed3-Datenblatt](https://daisy.nyc3.cdn.digitaloceanspaces.com/products/seed3/Daisy_Seed3_datasheet.pdf),
[Tulip Getting Started](https://github.com/shorepine/tulipcc/blob/17d1ef1d14aa0a51520fced04c87c1328f79bbd0/docs/getting_started.md).
