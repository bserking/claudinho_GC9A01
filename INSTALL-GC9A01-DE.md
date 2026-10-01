# Claudinho auf ESP32-C3 Super Mini + GC9A01

Diese Variante ersetzt das ursprüngliche Nextion-Display durch ein rundes
GC9A01 mit 240 × 240 Pixeln. Der ESP32 rendert die Oberfläche selbst über SPI;
eine Nextion-`.tft`-Datei wird weder benötigt noch unterstützt.

## Verdrahtung

| GC9A01 | ESP32-C3 Super Mini | Funktion |
|---|---|---|
| VDD | 3.3V | Versorgung |
| GND | GND | Masse |
| SCL/SCK | GPIO 4 | SPI-Takt |
| SDA/MOSI | GPIO 5 | SPI-Daten |
| CS | GPIO 6 | Chip Select |
| DC | GPIO 7 | Data/Command |
| RST | GPIO 10 | Reset |

Wichtig: `VDD` kommt an **3,3 V**, nicht an 5 V. Ein MISO-Anschluss ist für
dieses Display nicht erforderlich. Die von dir beschriebene Verdrahtung
enthält keinen Touch-Controller.

## Was funktioniert

- animierte Claudinho-Gesichter und Reaktionen auf Claude-Code-Ereignisse;
- Anzeige der 5-Stunden- und 7-Tage-Nutzung;
- Werkzeug-Szenen (Code, Terminal, Lesen, Agenten);
- WLAN-Konfiguration, lokaler HTTP-Endpunkt und OTA-Firmwareupdates;
- optionales Bambu-Lab-Dashboard und Druckerwarnungen;
- Gesichtsfarbe per `claudinho.sh cor R G B salvar`.

Der BOOT-Taster ersetzt die einfachen Touch-Aktionen:

- im Gesicht: Verbrauchsanzeige öffnen;
- bei konfiguriertem Bambu-Drucker: weiter zum Druckerpanel;
- auf Daten-/Druckerseiten: zurück zum Gesicht;
- festen Druckeralarm bestätigen;
- ein angefordertes OTA-Update freigeben.

Nicht verfügbar sind die visuelle Farbpalette, Tic-Tac-Toe und Genius. Diese
Funktionen brauchen echte Touch-Koordinaten.

## Vorhandenes Display ohne neue Programme aktualisieren

Für ein bereits eingerichtetes Display genügt Python 3.10 oder neuer.
Es werden keine Zusatzpakete, Treiber oder Administratorrechte benötigt.
Der Rechner und das Display müssen sich im lokalen Netz erreichen können.

Öffne den Repository-Ordner `claudinho_GC9A01` im Explorer. Klicke in die Adresszeile,
tippe `powershell` ein und drücke Enter. In diesem Fenster eingeben:

```powershell
python ..\claude-app-integration\update_display.py --check
```

Das prüft die Verbindung, das richtige Displaymodell und die Firmwaredatei.
Für das eigentliche Update:

```powershell
python ..\claude-app-integration\update_display.py --apply
```

Halte das Display bereit. Sobald das Programm dazu auffordert und auf dem
LCD **Press BOOT** erscheint, drücke den BOOT-Taster am ESP32 kurz. Danach
überträgt das Programm die Datei, wartet auf den Neustart und prüft die
Version. Ein Erfolg wird erst nach bestätigter Version gemeldet. Die
Freigabe hat ungefähr eine Minute Zeit. Bei einem Fehler die Meldung lesen;
keine wiederholten Updates auf Verdacht starten.

Das Programm liest den bestehenden Geräteschlüssel lokal aus der
Claudinho-Konfiguration. Bei einem abweichenden Ablageort kann
`--device-config PFAD` angegeben werden. In einem neuen Paket liegen
den Repository-Ordner mit seinem Unterordner `claude-app-integration`; alle Dateien
zusammen entpacken.

## Neue Hardware über USB einrichten

Die geprüfte Komplett-Firmware liegt unter
`firmware/bin/claudinho-esp32c3-1.8.3-gc9a01.4-completo.bin`. Das vorhandene
Skript erkennt den ESP32-C3 und wählt diese Datei automatisch:

```bash
export R="/pfad/zu/diesem/ordner"
export CLAUDINHO_DADOS="${HOME}/.claude/plugins/data/claudinho-claudinho"
bash "$R/scripts/porta.sh"
bash "$R/scripts/gravar.sh" COM6
```

`COM6` durch die gefundene Schnittstelle ersetzen. Der erste Flash löscht die
alte WLAN-Konfiguration. Danach die WLAN-Einrichtung wie im ursprünglichen
Claudinho-Setup ausführen. Das WLAN-Passwort nicht im Chat eingeben, sondern
vom vorhandenen `wifi.sh` verdeckt in einem separaten Terminal abfragen lassen.

Wenn `gravar.sh` `PRECISA_BOOT` meldet: BOOT gedrückt halten, USB kurz trennen
und wieder verbinden, BOOT loslassen, Port erneut ermitteln und noch einmal
flashen. Erfolg ist erst mit `Hash of data verified` bestätigt.

## Bedienung nach der Einrichtung

### Status-Webseite

Im gleichen WLAN lässt sich die integrierte Übersicht im Browser öffnen:

- `http://claudinho.local/`
- falls mDNS nicht funktioniert: die angezeigte IP verwenden, beispielsweise
  `http://<DISPLAY-IP>/`

Seit Version `1.8.3-gc9a01.3` zeigt die Webseite animierte Gesichtsvorschauen
beim aktuellen Zustand, in der Übersicht aller 16 Ausdrücke und in der
Ereignisliste. Augen, Münder, Tränen und Symbole entsprechen dem LCD;
die Animation läuft im Browser und ist nicht bildgenau mit dem LCD synchron.

Die Seite aktualisiert sich alle drei Sekunden. Sie zeigt den aktuellen
Gesichtsausdruck, die aktive Displayseite, WLAN-Signal, freien Speicher,
Laufzeit, Claude-Nutzung und die letzten 24 Befehle beziehungsweise
Gesichtswechsel. Die Historie liegt nur im RAM und beginnt nach einem Neustart
leer. Prompt-Inhalte und Zugangsdaten werden nicht gespeichert.

Die Rohdaten der Übersicht sind zusätzlich unter `/status.json` verfügbar.
Die Gerätekennung steht unter `/ident.json`.

### Kommandozeile

```bash
bash "$R/scripts/claudinho.sh" info
bash "$R/scripts/claudinho.sh" cara prompt feliz
bash "$R/scripts/claudinho.sh" consumo 20
bash "$R/scripts/claudinho.sh" cor 240 105 30 salvar
```

Für ein späteres OTA-Update:

```bash
bash "$R/scripts/claudinho.sh" atualizar
```

Wenn auf dem Display **Press BOOT** erscheint, den BOOT-Taster kurz drücken.
Den Befehl `claudinho.sh tela` nicht verwenden; das Skript erkennt den GC9A01
und erklärt, dass keine separate Bildschirmdatei nötig ist.

## Selbst kompilieren

Für Entwickler mit bereits vorhandener Build-Umgebung: benötigt werden
Arduino CLI, der ESP32-Core 3.x, ArduinoJson, Adafruit GC9A01A und Adafruit
GFX samt BusIO. Auf einem eingeschränkten Arbeitsrechner die fertige Firmware
verwenden; für das Update ist diese Build-Umgebung nicht erforderlich.

`firmware/compilar.sh` erstellt Firmware und Prüfsummen. Die Displaypins und die Umschaltung
zwischen GC9A01 und dem ursprünglichen Nextion-Backend stehen in
`firmware/claudinho/config.h`.

## Verifikationsstand

Die Firmware wurde mit ESP32-Arduino-Core 3.3.12, ArduinoJson 7.4.3,
Adafruit GC9A01A 1.1.1 und Adafruit GFX 1.12.6 erfolgreich für ESP32-C3
kompiliert. Version `1.8.3-gc9a01.4` belegt 1.355.593 Byte Flash (68 %) und
51.528 Byte statischen RAM (15 %). Der Build mit aktivierten Compilerwarnungen
lief ohne Warnungen durch. Die Web-Skripte und ihre Behandlung unbekannter
Verbrauchswerte wurden geprüft. Ein Build ersetzt keinen Hardwaretest nach
dem Einspielen; die frühere Version `1.8.3-gc9a01.3` wurde bereits auf deinem
Display benutzt.
