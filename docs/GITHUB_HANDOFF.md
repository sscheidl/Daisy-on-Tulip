# GitHub und Übergabe

Repository: [sscheidl/Daisy-on-Tulip](https://github.com/sscheidl/Daisy-on-Tulip),
**privat**. Der Zugriff mit Pull-/Push-Rechten ist nach Freigabe bestätigt.
Die ursprünglichen Versuche zur Repository-Erstellung lieferten HTTP 403
„Resource not accessible by integration“. Das anschließend angelegte Repository
wurde eingebunden; sein Initialisierungscommit bleibt in der Historie erhalten.
Andere Repositories, insbesondere `Daisy-Seed`, wurden nicht verändert.

## GitHub verwenden

```sh
git clone https://github.com/sscheidl/Daisy-on-Tulip.git
cd Daisy-on-Tulip
```

Der [Alpha-Prerelease](https://github.com/sscheidl/Daisy-on-Tulip/releases/tag/v0.1.0-alpha)
enthält Firmware- und App-Dateien. Zugriff auf Repository und Assets erfordert
eine passende GitHub-Anmeldung. Der erste Actions-Lauf ist bestanden; Details
und Hardwaretestgrenzen stehen in `TEST_RESULTS.md`.

## Enthaltene Übergabe

- Eigenständiges Git-Repository, Branch `main`, Alpha-Tag `v0.1.0-alpha`.
- Quellcode, Dokumentation, Tests und Build-/Installationsskripte.
- Drei `.bin`-/`.elf`-/`.map`-Sätze, Prüfsummen, Manifest und lokale Testlogs.
- `dist/Daisy-on-Tulip-v0.1.0-alpha.zip`: Quellstand plus fertige Artefakte.
- `dist/daisy_toy_piano.zip`: installierbare Python-Quelldateien.
- `dist/Daisy-on-Tulip-v0.1.0-alpha.bundle`: vollständige Git-Historie und Tag.

Die geprüften Alpha-Builddateien und Testlogs sind unter
`release-assets/v0.1.0-alpha/` im privaten Repository abgelegt. Sie liegen
zusätzlich im Komplettpaket und als Prerelease-Assets vor. Mit `scripts/build.sh` lassen sie
sich aus den gepinnten Quellen erneut erzeugen. Das Manifest prüft den
Zusammenhang von Firmware-/App-Quellen und Artefakten vor dem Verpacken.

## Offline übernehmen

```sh
git clone Daisy-on-Tulip-v0.1.0-alpha.bundle Daisy-on-Tulip-git
cd Daisy-on-Tulip-git
git remote set-url origin https://github.com/sscheidl/Daisy-on-Tulip.git
```

Die `artifacts/` aus dem Komplettpaket übernehmen, falls nicht neu gebaut werden
soll. `python3 scripts/package.py` erzeugt die Übergabepakete erneut.

`scripts/publish_github.sh` ist der ursprüngliche Erstanlage-Helfer für ein
**noch nicht existierendes** Repository in einem entsprechend berechtigten
Account. Im nun bestehenden Repository wird er nicht erneut benötigt. Normale
Änderungen werden über Git gepusht; veröffentlichte Tags/Assets nicht überschreiben.
