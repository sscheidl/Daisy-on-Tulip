# Tulip-App über USB installieren

Keine WLAN-Einrichtung, kein Firmware-Flash und kein AMYboard erforderlich.
Benötigt wird eine vorhandene Tulip-Standardfirmware mit MicroPython, LVGL 9,
`UIScreen`, `UIButton`, `UISlider`, `UILabel` und MIDI-Callback-API. Der geprüfte
Quellstand steht in `dependencies.lock.json`; die genaue auf dem Gerät
installierte Firmware muss beim Hardwaretest notiert werden. Alte Builds mit
abweichenden APIs sind nicht automatisch kompatibel.

## Normaler Weg

1. Tulip einschalten und den **PWR/Charge/Program-USB-Port** mit einem Datenkabel
   an den Rechner anschließen. USB-KB ist der Host-Port und dient nicht zur
   Übertragung der App vom Rechner.
2. Installieren und kopieren:

   ```sh
   python3 -m pip install mpremote
   python3 scripts/install_tulip.py --port auto
   ```

   Bei mehreren Geräten statt `auto` etwa `/dev/ttyUSB0`, `/dev/ttyACM0` oder
   `COM4` angeben. Gegebenenfalls den CH340K-Treiber des Rechners installieren.
   Das Skript nutzt durchgehend **`resume`**, entsprechend der Tulip-Anleitung.
   Es führt keinen Soft-Reset, keine Neupartitionierung und kein Firmwareupgrade aus.

3. Es werden fünf Python-Dateien nach `/user/lib/daisy_toy_piano/` kopiert.
   `/user/lib` ist in Tulips Standard-Suchpfad. Vor einer Aktualisierung eine
   laufende Instanz sauber beenden; eigene Änderungen in diesem App-Verzeichnis
   vorher sichern. Andere Apps und `boot.py` werden nicht geändert.
4. Im Tulip-REPL, unabhängig vom aktuellen Arbeitsverzeichnis:

   ```python
   import tulip
   tulip.run('daisy_toy_piano')
   ```

5. Nach dem Kopieren kann der Rechner abgezogen werden. App-Dateien bleiben
   gespeichert und können bei jedem Neustart mit demselben Befehl gestartet
   werden. Autostart ist optional; vorhandene `boot.py` nicht ersetzen.

Warum `/user/lib`: `tulip.run()` wechselt bei einem lokalen gleichnamigen
App-Verzeichnis dessen Arbeitsverzeichnis. Ein importierbares Paket im
absoluten Bibliothekssuchpfad vermeidet Abhängigkeit vom aktuellen Verzeichnis
und entspricht dem Standard-`_boot.py`.

## Dateien manuell übertragen

Falls das Skript nicht verwendet werden soll:

```sh
mpremote connect auto resume fs mkdir :/user/lib/daisy_toy_piano
mpremote connect auto resume fs cp tulip/daisy_toy_piano/__init__.py :/user/lib/daisy_toy_piano/__init__.py
mpremote connect auto resume fs cp tulip/daisy_toy_piano/app.py :/user/lib/daisy_toy_piano/app.py
mpremote connect auto resume fs cp tulip/daisy_toy_piano/config.py :/user/lib/daisy_toy_piano/config.py
mpremote connect auto resume fs cp tulip/daisy_toy_piano/controller.py :/user/lib/daisy_toy_piano/controller.py
mpremote connect auto resume fs cp tulip/daisy_toy_piano/transport.py :/user/lib/daisy_toy_piano/transport.py
```

Bei bestehendem Verzeichnis den mkdir-Schritt weglassen. Das Paket enthält
**fünf** Python-Dateien; die erzeugte `config.py` gehört zwingend dazu.
Quelltext wird bevorzugt: ein `.mpy` aus einem fremden MicroPython-Build kann
inkompatibel sein. Die Alpha-Syntax wurde zusätzlich mit `mpy-cross` aus dem
zu Tulips Referenzstand gehörenden MicroPython-Commit geprüft.

## Bedienung / Beenden

Oben stehen MIDI-Status und zwei logarithmische Regler mit Millisekundenwerten.
Unten sind zwei Achterreihen großer Tasten. Grün zeigt eine von dieser App
gehaltene Taste an. Drücken sendet Note-On, Loslassen oder Wegziehen Note-Off.
Andere Finger erzeugen im nativen LVGL-Pointerpfad keine unabhängigen Akkorde.
Für Akkorde die Daisy-Taster zusätzlich verwenden.

Das native Power-Symbol oder Ctrl-Q beendet die App. Ctrl-Tab / Taskwechsel
löst alle gehaltenen virtuellen Tasten; die App bleibt im Hintergrund gestartet.
Beim Beenden werden Timer und eigener MIDI-Callback entfernt. Im selben
Tulip-Start sollte ein erneuter App-Start möglich sein. Nach einem Codeupdate
ist ein normaler Tulip-Neustart der einfachste Weg, alle importierten
Paketmodule frisch zu laden; kein Firmwareupdate nötig.

„Nicht verbunden“ bedeutet: keine passende bidirektionale Daisy-Antwort.
MIDI-Kanal 1, beide DIN-Richtungen, passende Backend-Firmware und Stromversorgung
prüfen. Eine reine OUT→IN-Verbindung reicht für die Session nicht aus.

## Nachweisgrenze

Dateisyntax, Controller und reale App-Event-Handler sind automatisiert geprüft;
Eventtests verwenden Testdoubles für LVGL/Tulip. Installation per USB, tatsächliches
Rendering, Touch-Latenz und Cleanup in einer laufenden Standardfirmware sind
noch am Gerät zu verifizieren. Es wird kein erfolgreicher Hardwarestart behauptet.
