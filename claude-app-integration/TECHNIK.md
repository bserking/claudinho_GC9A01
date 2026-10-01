# Technische Referenz: Claude-App und Claudinho

Für die erste Einrichtung bitte ANLEITUNG.md verwenden. Dieser Anhang beschreibt Datenformat, Geräteanbindung und Prüfungen.

## Vorhandene Display-Konfiguration

Der Server liest den bestehenden Display-Schlüssel ausschließlich lokal aus
`~/.claude/plugins/data/claudinho-claudinho/claudinho.env`, alternativ
`~/.claudinho/claudinho.env`. Ein anderer Pfad kann mit `--device-config` gesetzt werden.
Die Werte werden nicht in den Skill, die MCP-Antworten oder das ZIP kopiert.
Python verbindet sich direkt mit der vorhandenen lokalen Display-IP; Rechner und
Display müssen sich erreichen können. Es werden keine neuen Firewallregeln angelegt.

Der Transport verwendet wie die bestehende Firmware HTTP im lokalen Netz und den
Geräteschlüssel im Authorization-Header. Er ist nicht TLS-verschlüsselt und ist nur
für das vertraute lokale Netz gedacht; keine Portfreigabe ins Internet einrichten.
Das Gerät benötigte im Live-Test teilweise vier bis fünf Sekunden pro Anfrage.
Der Adapter wartet deshalb bis zu zehn Sekunden je Anfrage und lässt zwischen
aufeinanderfolgenden Verbindungen mindestens eine Sekunde Abstand. Die zweiteilige
Abschlussmeldung kann entsprechend länger dauern.

## Meldungen

| Zustand | Bestehendes Firmware-Ereignis |
| --- | --- |
| Aufgabe gestartet / Arbeit beginnt | `prompt` (nachdenklich) |
| Arbeit läuft | `prompt` |
| Rückfrage / Freigabe | `atencao` |
| Abgeschlossen | Sitzung über `fim` entfernen, danach `parou` ohne Sitzungsregistrierung |
| Fehler | `erro` |
| Abgebrochen | `fim` |

Im Geräteverlauf steht `Claude App` beziehungsweise `Cowork`. Auf das Gerät gelangen
nur Ereignistyp, Oberflächenname und eine kurze abgeleitete Sitzungskennung, keine
Aufgabentitel oder Nachrichten. Bestehende Claude-Code-Hooks können weiter senden.
Die aktuelle Firmware zeigt jeweils die zuletzt eingehende Reaktion; sie besitzt noch
keine Priorisierung zwischen App und Code und maximal acht registrierte Sitzungen.

Die Gesichter sind zeitlich begrenzte Ereignisanimationen (Arbeiten/Warten derzeit
etwa zwei Minuten, Fertig etwa fünf Sekunden). Diese Erweiterung macht daraus noch
keine durchgängige App-Zustandsüberwachung. Die vorhandene Firmware lässt unbestätigte
Sitzungen nach 30 Minuten auslaufen; die lokale Übersicht markiert aktive Meldungen
standardmäßig schon nach 15 Minuten als unbekannt. Es gibt keinen Hintergrund-Heartbeat.

## Statusdaten und Display-Anschluss

Die maßgeblichen Daten liegen in `data/status.sqlite3`. `--profile` ist ein lokal
gewähltes Zuordnungslabel, keine automatisch erkannte oder verifizierte Accountidentität.
Für getrennte Profile eigene Servereinträge mit unterschiedlichen `--profile`-Werten
verwenden. Diese Labels ersetzen keine Zugangskontrolle zwischen Windows-Benutzern.

Aktuellen Stand als JSON lesen:

```powershell
python server.py --profile claude-app --snapshot
python server.py --profile claude-app --snapshot --output display-status.json
```

Der Export enthält `schema_version`, `generated_at` und `sessions`. Jede Sitzung hat
`session_id`, `profile`, `surface`, `state`, `reported_state`, `updated_at`, `stale_after`,
`stale`, `revision` und `source: skill_reported`. Zeitwerte sind Unix-Sekunden.
Ein gespeicherter JSON-Export aktualisiert sich nicht selbst; regelmäßig neu erzeugen
oder die angegebenen Ablaufzeiten beim Anzeigen auswerten.

Tokenverbrauch und Abolimits sind `null` / `unavailable`. Es wird absichtlich kein
`/estado` mit erfundenen Werten gesendet. Die auf dem ESP32 bereits vorhandenen
Verbrauchswerte stammen weiterhin aus Claude Code und sind keine App-Einzelmessung.
Die lokale Datenbank bleibt bis zur manuellen Löschung erhalten.

Der Adapter verlangt für `/evento` neben einem erfolgreichen HTTP-Status die
Firmware-Antwort `ok`. `display_delivery.state` in der Werkzeugantwort zeigt `sent`, `already_sent`, `failed`,
`skipped` oder `disabled`. Bei fehlgeschlagener Zustellung bleibt der Status gespeichert.
Ein identischer Werkzeugaufruf darf einmal wiederholt werden; es gibt keine automatische
Offline-Warteschlange. Die Firmware hat keine Ereignis-Deduplizierung: Bei einem Timeout
nach Annahme kann ein erneuter Versuch dieselbe Animation nochmals auslösen.

## Prüfung

```powershell
python -m unittest discover -v
python server.py --check-device
python check_live.py
```

`--check-device` liest nur. `check_live.py` sendet kurz Arbeiten/Warten/Fertig, prüft den
Geräteverlauf und entfernt die Testsitzung. Der vollständige Test aus einem echten
Claude-Chat erfolgt nach Neustart und Skill-Import mit dem Beispiel oben.

Die zwanzig automatisierten Tests prüfen unter anderem Kontoprofiltrennung, Wiederholungen,
veraltete Meldungen, Netzwerkausfälle, Protokollkommunikation, Datenerhalt nach Neustart
und das Beibehalten vorhandener Claude-Einstellungen. Hinzu kommen die Ablehnung
ungültiger MCP-Anfrage-IDs und die Prüfung der Firmware-Bestätigung. Einrichtungstests
arbeiten mit einer isolierten Kopie, damit sie vorhandene Vorlagen und ZIPs nicht
überschreiben. Acht Tests prüfen zusätzlich den Python-OTA-Helfer: Prüfsumme,
Gerätetyp, BOOT-Freigabe, einmalige Übertragung und bestätigte Zielversion.
Skill-Struktur und ZIP-Inhalt wurden zusätzlich geprüft.

## Rückbau

Nur den Eintrag `claude-info-display` aus `mcpServers` entfernen und Claude neu starten.
Den Skill in Claude deaktivieren/löschen. Den Integrationsordner erst entfernen, wenn
der Server nicht mehr läuft. Eine alte Gesamtkonfiguration nur dann zurückspielen,
wenn dadurch keine späteren Änderungen verloren gehen.

## Quellen und Kompatibilität

- [Lokale MCP-Verbindungen in Claude Desktop](https://modelcontextprotocol.io/docs/develop/connect-local-servers)
- [MCP-Lifecycle, implementierte Version 2025-06-18](https://modelcontextprotocol.io/specification/2025-06-18/basic/lifecycle)
- [MCP-Werkzeuge](https://modelcontextprotocol.io/specification/2025-06-18/server/tools)
- [Claude-Skills](https://support.claude.com/en/articles/12512198-how-to-create-custom-skills)

Die Geräteanbindung wurde anhand der angepassten Firmware aus dem Chat
„GC9A01-Display für ESP32-C3 anpassen“ erstellt (`webEvento`, `trataEvento`).
