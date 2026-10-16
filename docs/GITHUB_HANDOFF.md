# GitHub-Blocker und Übergabe

Am 16.10.2026 war die GitHub-CLI als **sscheidl** authentifiziert. Der konkrete
Versuch `POST /user/repos` mit `name=Daisy-on-Tulip` und `private=true` lieferte:

```text
HTTP 403
Resource not accessible by integration
https://docs.github.com/rest/repos/repos#create-a-repository-for-the-authenticated-user
```

Die verfügbare Integration darf somit kein neues Repository für diesen Account
erstellen. Es wurde kein anderes Repository als Ausweichziel verwendet, kein
bestehendes `Daisy-Seed` geändert und kein öffentlicher Ersatz angelegt. Es
gibt keinen GitHub-Release und keine bestätigte GitHub-Actions-Ausführung.

## Vorbereitet

- Eigenständiges lokales Git-Repository, Branch `main`, Tag `v0.1.0-alpha`.
- Vollständige Quellstruktur, Dokumentation, Tests und Build-/Installationsskripte.
- Drei `.bin`-/`.elf`-/`.map`-Sätze, Prüfsummen, Manifest und lokale Testlogs.
- `dist/Daisy-on-Tulip-v0.1.0-alpha.zip`: Quellstand plus fertige Artefakte.
- `dist/daisy_toy_piano.zip`: installierbare Python-Quelldateien.
- `dist/Daisy-on-Tulip-v0.1.0-alpha.bundle`: Git-Historie und Tag für Übernahme.

Builddateien sind bewusst nicht im Quell-Git getrackt; sie befinden sich im
Komplettpaket und werden im vorbereiteten GitHub-Prerelease als Assets hochgeladen.

## Übernahme auf eigenem Rechner

Komplett-ZIP entpacken und entweder ein neues lokales Git-Repository initialisieren
oder die vorbereitete Historie aus dem Bundle verwenden:

```sh
git clone Daisy-on-Tulip-v0.1.0-alpha.bundle Daisy-on-Tulip-git
```

Die `artifacts/` aus dem Komplettpaket in diesen Checkout kopieren, wenn nicht
erneut gebaut werden soll. `dist/` muss nicht übernommen werden; die Pakete
werden vom Skript neu erzeugt.

Mit einer GitHub-Anmeldung, die neue private Repositories erstellen darf:

```sh
cd Daisy-on-Tulip-git
git remote remove origin
bash scripts/publish_github.sh
```

`git clone <bundle>` setzt `origin` auf die Bundle-Datei; dieses lokale origin
deshalb vorher entfernen. Bei einem frisch mit `git init` erstellten Checkout
ohne origin ist der Schritt nicht nötig. Das Skript erstellt
`<angemeldeter Account>/Daisy-on-Tulip` privat, pusht `main` und den vorbereiteten
Tag und erstellt `v0.1.0-alpha` als Prerelease mit Firmware- und App-Assets.
Wenn der Name schon existiert oder origin gesetzt ist, bricht es ab. Es versucht
keine Umstrukturierung vorhandener Projekte.

Nach Push die Actions-Ausführung prüfen und deren Ergebnis gesondert in
`TEST_RESULTS.md` dokumentieren. Ein lokaler Crossbuild ist kein Nachweis einer
erfolgreichen GitHub-Runner-Ausführung.
