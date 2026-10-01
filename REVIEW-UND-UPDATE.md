# Prüfung und Update: Claude Info Display

Stand: 1. Oktober 2026. Geprüft wurden die ESP32-C3/GC9A01-Firmware,
Weboberfläche, Claude-Code-Hooks und Skripte sowie die Python-MCP-Anbindung
und der App-Skill. Die bereinigte Firmwarequelle liegt im Repository unter `firmware`.
Die Python-Anbindung hat Version **0.2.2**, die neue Firmware
**1.8.3-gc9a01.4**.

## Was geändert wurde

| Befund | Änderung |
| --- | --- |
| Fehlende Nutzungswerte konnten als 0 % erscheinen. | Fehlende, ungültige und abgelaufene Fenster erscheinen als unbekannt: LCD `--`, Web `Unavailable`, JSON `null`. Ein gemessener Wert von 0 bleibt 0 %. |
| Der Grundzustand des Gesichts hing auch von Verbrauchsdaten ab. | App-Ereignisse und offene Sitzungen funktionieren unabhängig von verfügbaren Kontolimits. |
| Portugiesische und deutsche Texte waren gemischt. | LCD, Webübersicht, Gesichtsnamen, Hinweise, Kommandozeilentexte und 313 Druckerwarnungen sind auf Englisch. Der App-Skill und die Einrichtungshilfe bleiben für dich auf Deutsch. |
| Werkzeugaufrufe konnten ohne eindeutige Firmwarebestätigung als zugestellt gelten. | Erst HTTP-Erfolg mit Antwort `ok` bestätigt eine Ereignisübertragung. |
| Einige Claude-Code-Anfragen hatten nur zwei oder drei Sekunden Zeit. | Die Netzwerkzeit wurde auf zehn Sekunden vereinheitlicht; die Hook-Konfiguration lässt ausreichend Zeit. |
| Ein Flash-Fehler konnte als erfolgreicher Skriptablauf enden. | Der tatsächliche Fehlercode des Flashprogramms wird weitergegeben. |
| Die kleine Status-API baute JSON per Zeichenkettenformatierung. | JSON wird serialisiert; Modellnamen mit Anführungszeichen oder Backslashes bleiben gültig. |
| Touch-Spiele und Palette waren auf deinem Display unbedienbar. | Diese Teile werden beim GC9A01-Build ausgeschlossen. Die direkte Farbeinstellung bleibt verfügbar. |
| Alte Testmeldungen konnten den Verbindungstest scheinbar bestehen lassen. | Der Test verlangt einen neu hinzugekommenen Verlaufseintrag und versteht alte sowie neue Firmwaretexte. |
| Einrichtung und Protokoll hatten Randfälle. | Ungültige MCP-Anfrage-IDs werden abgewiesen; Einrichtung schützt vorhandene Konfigurationen vor zwischenzeitlichem Überschreiben. |

Das neue Gesamtpaket enthält eine einzige aktuelle Firmware für deinen
ESP32-C3 und einen Skill-ZIP. Alte Firmwaregenerationen, Nextion-Displaydateien,
portugiesische Dokumentationsduplikate, Build-Ausgaben und Python-Caches sind
im Download ausgelassen. Die portugiesische Druckerwarnungstabelle und ihr
Generator wurden durch eine englische, offline reproduzierbare Tabelle ersetzt.
Ungenutzte Zustandskopien und Variablen wurden entfernt.

Interne Ereignisnamen und Konfigurationsschlüssel bleiben kompatibel mit der
vorhandenen Anbindung. In der Webhistorie werden Ereignisse durch englische
Bezeichnungen dargestellt, beispielsweise `Waiting for you: Claude App`.

## Was geprüft wurde

- **20 Python-Tests bestanden:** Speicherung, Profiltrennung, Wiederholungen,
  veraltete Meldungen, Ausfälle, MCP, Konfiguration und OTA-Updateablauf.
- **Firmware erfolgreich mit allen Compilerwarnungen gebaut, ohne Warnungen:**
  1.355.593 Byte Flash, 51.528 Byte statischer RAM.
- Embedded JavaScript syntaktisch geprüft; unbekannte Werte, echte 0 % und
  87 % überprüft. Die 16 Gesichtsbezeichnungen stimmen mit den Vorschauen überein.
- Shell-Syntax geprüft; ein simulierter Flash-Fehler und ein erfolgreicher
  Flash behalten ihren jeweiligen Rückgabecode.
- Englische Warnungstabelle reproduzierbar geprüft; alle **1.982
  Codezuordnungen** und Indizes erhalten.
- Der Python-Updater hat das vorhandene Display **lesend erreicht** und
  Firmwaredatei, Prüfsumme und Gerätetyp geprüft.

Die neue Firmware ist fertig gebaut. Das Einspielen und der anschließende
Hardwaretest benötigen noch die Freigabe mit BOOT am Display.

## Auf deinem Rechner anwenden

1. **Claude vollständig schließen und erneut öffnen.** Die Python-Dateien der
   bisherigen App-Verbindung wurden bereits aktualisiert. Die Arbeitsanweisungen
   des Skills sind gleich geblieben; für die neuen Serverfunktionen genügt der
   Neustart. Im neuen Skill-ZIP wurde die YAML-Beschreibung korrekt in
   Anführungszeichen gesetzt. Du kannst dieses ZIP bei Bedarf neu importieren.
2. Für die englische Anzeige die Firmware aktualisieren. Öffne den Ordner
   `claude-app-integration` im Explorer. Klicke auf die Adresszeile, tippe
   `powershell` und drücke Enter. Für eine Prüfung eingeben:

   ```powershell
   python update_display.py --check
   ```

   Für das Update eingeben:

   ```powershell
   python update_display.py --apply
   ```

3. **BOOT kurz drücken**, sobald das Programm dazu auffordert. Das Gerät kann
   vor dem Update noch `Aperte BOOT` anzeigen; nach dem Update heißt es
   `Press BOOT`. Die Übertragung startet erst nach der Freigabe. Das Programm
   meldet Erfolg erst, wenn das Display mit Version `.4` wieder antwortet.
4. Die Status-Webseite neu laden und den bekannten Checklisten-Test wiederholen.
   **Thinking → Waiting for you → Thinking → Done** ist der erwartete Ablauf.

Zum Aktualisieren genügen vorhandenes Python 3.10+ und das lokale Netzwerk.
Der Updater nutzt ausschließlich die Python-Standardbibliothek. Der
Geräteschlüssel wird aus der vorhandenen lokalen Konfiguration gelesen.
Ein Komplettimage ist für diesen Netzwerk-Updateweg nicht zulässig.

Die Repository-Struktur mit `firmware` und `claude-app-integration` beibehalten. Weitere Geräte- und
Verdrahtungsschritte stehen in `INSTALL-GC9A01-DE.md`.
Für die erstmalige Claude-App-Einrichtung gilt
`claude-app-integration/ANLEITUNG.md`.

Die übersetzten Claude-Code-Skripte und Hooks gehören zum neuen
Claudinho-Pluginpaket. Eine bereits installierte ältere Claude-Code-Pluginkopie
bekommt diese Dateien erst durch ihr Pluginupdate; ein Firmwareupdate allein
ersetzt keine Dateien auf dem Rechner.

## Grenzen der bestehenden Architektur

Die normale Claude-App meldet Zustände durch Werkzeugaufrufe des Modells.
Der erfolgreiche Chat-Test bestätigt diesen Ablauf; ein Skill ist keine
garantierte Hintergrundüberwachung. Beenden der App, Abbruch und ein
ausbleibender Werkzeugaufruf werden nicht unabhängig erkannt. App-Limits und
Tokenverbrauch sind weiterhin unbekannt.

Gesichter für Arbeit und Rückfragen sind zeitlich begrenzte Animationen von
ungefähr zwei Minuten. Das fertige Gesicht erscheint etwa fünf Sekunden.
Die Firmware besitzt eine gemeinsame Anzeige für App und Code; das zuletzt
eingehende Ereignis bestimmt die Reaktion. Gleichzeitige Sitzungen haben
noch keine Priorisierung ihrer Gesichter. Diese Funktionen sollten bei einer
späteren Erweiterung ausdrücklich umgesetzt werden.
