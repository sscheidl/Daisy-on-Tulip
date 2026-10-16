# Eingebundene Software

Eigener Projektcode: MIT, siehe `LICENSE`. Die folgenden Bibliotheken bleiben
unter ihren jeweiligen Lizenzen. Exakte Versionen stehen in
`dependencies.lock.json`; die Bibliotheken werden vom Bootstrap-Skript aus
den offiziellen Repositories geladen und nicht verändert.

| Bestandteil | Verwendung / Lizenzhinweis |
|---|---|
| Electro-Smith libDaisy | Desktop-Hardware, Codec, ADC, LEDs, MIDI, USB; [MIT-Lizenz](licenses/libDaisy.txt) |
| Electro-Smith DaisySP | Sinusoszillator; [MIT-Lizenz](licenses/DaisySP.txt) |
| ARM CMSIS / CMSIS-DSP | STM32-/Cortex-M-Basis; [Apache 2.0](licenses/CMSIS.txt), [CMSIS-DSP](licenses/CMSIS-DSP.txt) |
| ST STM32H7 HAL / CMSIS Device | Treiber und MCU-Definitionen; [HAL](licenses/STM32H7xx_HAL.md), [CMSIS Device](licenses/STM32H7xx_CMSIS.md) |
| ST USB Device Middleware | USB-Device/MIDI-Transport; [Lizenz](licenses/STM32_USB_Device.md) |

Weitere Treiber-/Middleware-Dateien im libDaisy-Baum besitzen eigene
Copyright-/Lizenzhinweise, insbesondere USB-Host und FatFs. Die vollständigen
Quellen mit diesen Hinweisen sind über den gepinnten offiziellen libDaisy-
Commit verfügbar. Auf dem hier ausgewählten Firmwarepfad werden keine
Samples oder fremde Musikdaten eingebunden.

`DaisySP-LGPL` wird als offizielles Git-Submodul möglicherweise mit ausgecheckt,
ist aber nicht aktiviert, kompiliert oder in die Firmware gelinkt
(`USE_DAISYSP_LGPL` ist nicht gesetzt).

Tulip CC, MicroPython, LVGL und die Tulip-Widgets laufen in der vorhandenen
Tulip-Firmware. Diese Firmware wird nicht als Projektartefakt verteilt oder
ersetzt. Die App verwendet ihre APIs und enthält keine kopierten Tulip-
Widgetimplementierungen. Tulip/MicroPython dienen zusätzlich als gepinnte
Referenz bzw. Syntaxprüfwerkzeug.

ARM-GCC wird separat aus dem xPack-Projekt bezogen und nicht im Komplettpaket
verteilt. Prüfsumme und Downloadadresse stehen im Installationsskript.
