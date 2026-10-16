# MIDI-Protokoll v0.1

MIDI 1.0, Kanal **1** (Status-Low-Nibble `0`), ein logischer MIDI-Port.
DIN/TRS: 31.250 Baud, 8N1. USB: klassisches USB-MIDI-1.0-Event-Paket.
Die Anwendung arbeitet transportunabhängig mit MIDI-Nachrichten.

| Richtung | Nachricht / Bytes (hex) | Bedeutung |
|---|---|---|
| Tulip → Daisy | `90 nn vv`, `vv > 0` | Anschlag, `nn` = MIDI-Note 0–127 |
| Tulip → Daisy | `80 nn 00` oder `90 nn 00` | Einen Haltezähler dieser Note lösen |
| Beide | `B0 14 vv` | CC20, Attack |
| Beide | `B0 15 vv` | CC21, Decay |
| Tulip → Daisy | `B0 76 2A` | CC118 = 42, Ping und Parameter-Snapshot anfordern |
| Daisy → Tulip | `B0 77 2A` | CC119 = 42, Pong / Session-Lebenszeichen |
| Tulip → Daisy | `B0 7B 00` | CC123, alle MIDI-Haltezähler löschen |
| MIDI → Daisy | `B0 78 00` | CC120 ebenfalls als MIDI-Quellen-Panik behandelt |

libDaisy liefert CC120/123 als **ChannelMode**-Events. Das Routing behandelt
`AllSoundOff` / `AllNotesOff` entsprechend; dies wird mit dem echten Parser
automatisiert geprüft. In dieser AD-Testfirmware laufen bereits angeschlagene
endliche Ausklänge auch nach Panik aus. Physische Haltezustände bleiben bestehen.

## Parameter und Auflösung

`value` ist ein Integer 0–127:

```text
Attack_ms = 1  * (1000 / 1)  ^ (value / 127)
Decay_ms  = 20 * (3000 / 20) ^ (value / 127)
```

Tulip zeigt gerundete Millisekunden, Daisy rechnet mit Float-Millisekunden.
Beide physische Potis werden ebenfalls auf 7 Bit quantisiert. Die Kennlinie
bietet im kurzen Bereich mehr Feinauflösung. Für spätere präzisere Anforderungen
sollte das Protokoll auf 14 Bit erweitert werden.

## Zuständigkeit, Pickup und Rückmeldung

Daisy hält den maßgeblichen aktuellen Parameterwert. Beim Start kommen die
Werte von Poti 1/2. Ein empfangener CC setzt den Wert und aktiviert Pickup am
entsprechenden physischen Poti. Es übernimmt erst bei höchstens zwei CC-Schritten
Abstand oder wenn seine Bewegung den Zielwert überschreitet. Zwei Schritte
Hysterese unterdrücken Rauschen; Endwerte bleiben erreichbar.

Physische Änderungen werden als CC zurückgesendet. Ein Tulip-Ping fordert
zusätzlich den vollständigen AD-Stand an: Pong, CC20, CC21. Jeweils höchstens ein
Daisy-Tx-Paket alle 5 ms; neuere Werte ersetzen alte Pending-Werte.

Tulip sendet maximal eine Nachricht je Parameter pro 40 ms, also maximal
50 Slider-Nachrichten/s für beide zusammen. Die GUI aktualisiert empfangene
Werte **ohne** sie zurückzusenden. Während des Ziehens oder solange ein lokaler
Wert noch ungesendet ist, überschreibt eingehende Rückmeldung den Slider nicht.
Nach dem Beenden einer Bewegung gewinnt der aktuelle Daisy-Stand. Es gibt
kein MIDI-Thru und keine Echo-Schleife.

## Session / Status / Ausfall

Tulip sendet alle 500 ms Ping. Erst nach Pong ist die Anzeige „verbunden“ und
die virtuelle Klaviatur freigegeben. Das belegt eine antwortende Anwendung auf
dem gewählten MIDI-Kanal, **keine USB-Enumeration** und keine kryptografisch
eindeutige Geräteidentität. Eine andere Anwendung mit demselben Ping/Pong-Paar
könnte ebenfalls antworten.

Nach 1600 ms ohne Pong räumt Tulip aktive Tasten auf, löscht nicht gesendete
Reglerwerte und sperrt die Klaviatur. Pings laufen weiter. Daisy löscht nach
1600 ms ohne gültige Note-/Parameter-/Ping-Nachricht alle MIDI-Haltezähler,
aber keine physisch gedrückte Taste. Die Audio-Hüllkurven laufen einmalig aus;
maximal 4000 ms bei den konfigurierten Höchstwerten.

Auch bei DIN gibt es keine elektrische Kabelstatusanzeige: „verbunden“ wird
ausschließlich durch den Rückkanal ermittelt. Für die App sind deshalb **beide
MIDI-Kabel** erforderlich. Ein generisches MIDI-Keyboard ohne Heartbeat kann
Noten spielen; Halte-LEDs werden aber nach 1600 ms ohne Nachrichten bereinigt.
Der Klang ist davon unabhängig ein One-Shot. MIDI Active Sensing wird nicht
als Sessionersatz ausgewertet.

Bei Reconnect: frische Pong-/Parameter-Antwort abwarten, keine alten virtuellen
Noten wiederherstellen, kein alter Slider-Sollwert ungefragt an Daisy senden.
Eine noch aufliegende Touch-Taste muss neu gedrückt werden. Beim Taskwechsel/
Beenden werden einzelne Note-Offs plus CC123 gesendet. Der Hintergrundtimer
hält die Session während eines normalen Taskwechsels am Leben.

Wenn nur eine Richtung ausfällt, sorgt der Timeout auf der jeweils anderen
Seite für Aufräumen bzw. die noch funktionierende Richtung für Note-Offs.
Beim nativen Tulip-USB-Blockaderisiko kann dieser GUI-Timer selbst ausbleiben;
der Daisy-Timeout und die endlichen AD-Ausklänge begrenzen trotzdem Daisy-
Zustände. Ein eingefrorenes Tulip-GUI lässt sich dadurch nicht reparieren.

## Doppelte Noten und Polyphonie

Notenplan: `60 62 64 65 67 69 71 72 | 72 74 76 77 79 81 83 84`.
Physische Tasten besitzen einzelne Zustände, MIDI besitzt je Note einen Zähler
von 0 bis maximal 255. Jeder Note-Off löst genau einen MIDI-Anschlag. GUI-
Tasten-IDs 7 und 8 senden beide Note 72, bleiben intern jedoch getrennt.
Bei externem C5 leuchten beide passenden LEDs. Bei ausschließlich physischen
Anschlägen leuchtet die jeweilige tatsächlich gehaltene Taste.

Überlappende gleiche Tonhöhen teilen sich einen Oszillator und retriggern die
Hüllkurve kontinuierlich; dies ist keine unabhängige Schichtung gleicher
Tonhöhen. Velocity wird in v0.1 nur zur Erkennung von Note-On/Off benutzt,
nicht als Anschlagdynamik. Andere Kanäle, Sustain, Pitchbend, Program Change,
Clock und SysEx steuern diese Engine nicht.

## Konfiguration ändern

`config/protocol.json` editieren, dann `python3 scripts/generate_protocol.py`.
Die CCs 118/119 nicht mit anderen Synthparametern belegen. Kanal und alle
generierten Dateien auf beiden Geräten zusammen aktualisieren. Es gibt in
v0.1 keine automatische Protokollversionsaushandlung.
