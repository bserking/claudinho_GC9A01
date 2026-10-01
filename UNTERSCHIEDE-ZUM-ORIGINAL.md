# Unterschiede zum Original: Claudinho GC9A01

Vergleichsbasis: argeuthiesen/claudinho, Commit `35d192d92202ed9b2441489c246140f9f19d8acc` (Firmware 1.8.3). Der Originalstand wurde vor dem Upload von GitHub abgerufen.
Ziel: https://github.com/bserking/claudinho_GC9A01

| Bereich | Original | Dieser Fork |
| --- | --- | --- |
| Display | Nextion NX3224F024, serielle Anbindung | Rundes GC9A01, 240 × 240, SPI; ESP32-C3 Super Mini |
| Bedienung | Touch-Oberfläche | BOOT-Taste für Navigation und Updatefreigabe; Touch-Spiele und Palette beim GC9A01-Build ausgeschlossen |
| Firmware | 1.8.3; C3- und S3-Images | 1.8.3-gc9a01.4; C3-Komplettimage und OTA-Image mit SHA-256-Prüfsummen |
| Anzeige | Nextion-Ausgabe | Direkte Grafik mit Gesichtern, Arbeitsszenen und Vorschauen |
| Sprache | Portugiesische Bestandteile | LCD, Webübersicht, Skriptausgaben und 313 Druckerwarnungen auf Englisch; Einrichtungshilfe auf Deutsch |
| Zeitzone | Originalkonfiguration | Deutschland einschließlich Sommerzeit |
| Claude Code | Hooks und Statusline | Bestehende Anbindung weitergeführt; Netzwerkzeit und Hook-Zeitlimits angepasst |
| Claude App / Cowork | Keine mitgelieferte Python-MCP-Anbindung | Python-MCP-Server, Skill, Einrichtung, lokale Statusverwaltung und Verbindungstest ergänzt |
| Verbrauch | Originalanzeige | Fehlende oder abgelaufene Werte als unbekannt statt 0 %; App-Arbeitszustand unabhängig von Verbrauch |
| Übertragung | Bisherige Rückmeldungen | Explizite Gerätebestätigung, korrekt weitergereichte Flash-Fehler und gültige JSON-Ausgabe |
| Updates | Bestehende Flash-/OTA-Wege | Python-OTA-Updater mit Prüfung von Image, Prüfsumme, Gerätetyp, BOOT-Freigabe und Zielversion |
| Warnungstabelle | Portugiesische HMS-Tabelle | Englische Tabelle und offline reproduzierbarer Generator |
| Paketumfang | Nextion-Projektdateien, mehrere Images und Originalhandbücher | Auf GC9A01 zugeschnittene Dokumentation und Images; Nextion-Dateien und alte Handbücher entfernt |
| Lizenz | MIT, Argeu Thiesen | MIT-Lizenz und ursprüngliche Urheberangabe erhalten; Original im README verlinkt |

## Prüfung dieses Uploadstands

- Alle 20 Python-Tests bestanden.
- Beide Firmware-Prüfsummen geprüft.
- OTA-Standardpfad an die Repository-Struktur angepasst und geprüft.
- Lokale Sitzungsdatenbank, Gerätekonfiguration, Rechnerpfade, Python-Caches und Build-Artefakte vom Upload ausgeschlossen. Rechnerpfade in der Anleitung durch Beispielpfade ersetzt.
- Der frühere Build- und Reviewbericht steht in `REVIEW-UND-UPDATE.md`. Die Firmware wurde für diesen Upload nicht erneut kompiliert oder auf dem Gerät installiert.

## Grenzen

Die Claude-App meldet Zustände durch Modell-Werkzeugaufrufe; sie bietet damit keine unabhängige Hintergrundüberwachung. App-Kontolimits und Tokenverbrauch bleiben unbekannt. Gleichzeitige Sitzungen haben keine priorisierte Gesichtsanzeige. Der Nextion-Backendcode ist noch vorhanden, die zugehörigen Displaydateien und fertigen Images werden in diesem Fork jedoch nicht mitgeliefert.
