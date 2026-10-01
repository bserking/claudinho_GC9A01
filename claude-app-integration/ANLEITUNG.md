# Claude mit deinem Info-Display verbinden – Schritt für Schritt

Diese Anleitung ist für dich gedacht, wenn du Claude bereits benutzt, aber noch nie einen Skill hinzugefügt hast. Du musst dafür weder programmieren noch eine neue Anwendung installieren.

**Update zur automatischen Nutzung:** Wenn die Verbindung bereits funktioniert, beginne mit **AUTOMATIK.md** im selben Ordner. Dort stehen Skill-Austausch, persönliche Daueranweisung und ein Test ohne Display-Auftrag.

**Dein aktueller Stand:** Auf dem Rechner, auf dem wir die Anbindung eingerichtet haben, ist die Verbindung in Claude Desktop bereits eingetragen. Der Skill ist installiert. Eine normale Claude-Anfrage hat automatisch Arbeiten, Warten, erneutes Arbeiten und Fertig gemeldet. Auf diesem Rechner sind die folgenden Schritte eine Referenz; nach einem Server-Update genügt ein vollständiger Neustart der App.

**Auf diesem Rechner musst du keinen Einrichtungsbefehl mehr ausführen.** Für eine neue Einrichtung starte mit Schritt 1. Hinweise für weitere Rechner stehen am Ende.

## Was ist ein Skill?

Ein Skill ist eine gespeicherte Arbeitsanleitung für Claude. Du fügst sie einmal hinzu, statt denselben Ablauf bei jeder Aufgabe erneut erklären zu müssen.

Unser Skill heißt **info-display**. Er soll Claude bei jeder Nachricht selbstständig Beginn, Rückfragen und Abschluss melden lassen. Für die automatische Aktivierung in neuen Chats ist zusätzlich die Daueranweisung aus AUTOMATIK.md nötig.

Damit das Signal ankommt, gibt es zusätzlich eine **Verbindung**. In Claude wird sie möglicherweise „Connector“, „Tool“ oder „MCP-Server“ genannt. Du musst diese Begriffe nicht im Detail kennen:

| Teil | Aufgabe | Dein Stand |
| --- | --- | --- |
| Skill | Erklärt Claude, wann es eine Meldung senden soll | Bereits installiert; Einrichtung in Schritt 3 |
| Lokale Verbindung | Überträgt das Signal vom Rechner zum Display | Bereits eingerichtet; Prüfung in Schritt 4 |

Die Skill-ZIP ist ein fertiges Paket. Du musst den Inhalt nicht bearbeiten. Die ZIP lediglich an eine normale Chatnachricht anzuhängen, aktiviert den Skill noch nicht.

## Schritt 1: Display und App vorbereiten

1. Schließe das Display an die Stromversorgung an und warte, bis es gestartet ist.
2. Verbinde den Rechner mit dem Netz, in dem das Display erreichbar ist. Für den ersten Test eignet sich das bisher verwendete Heimnetz. Ein Firmen- oder Gastnetz kann die Verbindung zwischen Geräten blockieren.
3. Öffne die **Claude-Desktop-App unter Windows**. Verwende für diesen Test nicht Claude im Browser und nicht die Handy-App.
4. Melde dich mit dem Claude-Konto an, in dem du den Skill nutzen möchtest.

**Erwartetes Ergebnis:** Das Display ist eingeschaltet und die App zeigt deine normale Chatoberfläche. Das Display darf noch schlafen: Einschalten allein startet keine verfolgte Aufgabe.

## Schritt 2: Claude vollständig neu starten

Die neu eingetragene Verbindung muss von der App geladen werden.

1. Speichere gegebenenfalls noch nicht gesendeten Text. Lass laufende Aufgaben zuerst enden.
2. Suche im App-Menü nach **Beenden / Quit** und schließe Claude darüber.
3. Ist unten rechts bei der Windows-Uhr noch ein Claude-Symbol sichtbar, öffne gegebenenfalls den kleinen Pfeil, klicke das Symbol mit der rechten Maustaste an und wähle die angebotene Beenden-Funktion.
4. Öffne Claude erneut über das Windows-Startmenü.

Das Kreuz oben rechts kann je nach Einstellung nur das Fenster schließen. Entscheidend ist, dass die App wirklich neu startet. Ein Neustart gehört zur Einrichtung lokaler Verbindungen. [Offizielle Anleitung zu lokalen Verbindungen](https://modelcontextprotocol.io/docs/develop/connect-local-servers)

## Schritt 3: Den Skill hinzufügen

### Die richtige Datei auswählen

Du brauchst **info-display-skill.zip**. Speichere sie über den Link in unserem Chat oder wähle sie direkt aus dem vorhandenen Integrationsordner aus.

Auf dem bereits eingerichteten Rechner liegt die Datei hier:

```text
C:\Projekte\claudinho_GC9A01\claude-app-integration\info-display-skill.zip
```

So findest du den Ordner: Drücke **Windows-Taste + E**, klicke oben in die Adressleiste des Explorers, füge diesen Ordnerpfad ein und drücke Enter:

```text
C:\Projekte\claudinho_GC9A01\claude-app-integration
```

**Die Skill-ZIP nicht entpacken.** Die Datei `claude-info-display-clean.zip` ist dagegen das Gesamtpaket für weitere Rechner. Sie gehört nicht in den Skill-Upload.

### In Claude hochladen

Die englischen Menünamen entsprechen der aktuellen Claude-Hilfe. In deiner App können sie übersetzt sein; die deutschen Begriffe dienen der Orientierung.

1. Öffne die **Einstellungen** der Claude-App.
2. Wähle links unter **Anpassen** den Punkt **Skills**. In anderssprachigen Versionen heißt der Bereich **Customize → Skills**.
3. Öffne die Funktion zum Hinzufügen eines Skills. Je nach Version heißt sie **+** beziehungsweise **Skill erstellen**.
4. Wähle **Skill hochladen** (Upload a skill).
5. Wähle im Dateifenster **info-display-skill.zip** und bestätige.
6. Prüfe im Uploadfenster, dass unter **Vorschau** der Name **info-display** steht. Klicke auf **Hochladen** und warte auf den Sicherheitscheck und den Eintrag in der Skill-Liste.
7. Schalte ihn ein, falls er noch deaktiviert ist.

Falls Skills nicht verfügbar sind, prüfe bei einem persönlichen Konto unter **Settings → Capabilities**, ob **Code execution and file creation** eingeschaltet ist. Bei einem verwalteten Konto können Organisationsfreigaben nötig sein. Das ist eine Claude-Einstellung, keine Python-Installation auf deinem Rechner. [Offizielle Anleitung: Skills hinzufügen und aktivieren](https://support.claude.com/en/articles/12512180-use-skills-in-claude)

Der Skill heißt **info-display**; die bereits eingerichtete Verbindung heißt weiterhin **claude-info-display**. Diese unterschiedlichen Namen sind richtig.

**Erwartetes Ergebnis:** Der Skill ist sichtbar und aktiviert. Du lädst ihn nicht vor jeder Nachricht erneut hoch.

## Schritt 4: Die Verbindung zum Display prüfen

1. Starte in der Claude-Desktop-App einen **neuen Chat**.
2. Öffne beim Eingabefeld das Menü für zusätzliche Funktionen, häufig über **+**.
3. Suche nach **Connectors / Verbindungen** beziehungsweise der Verwaltung verbundener Werkzeuge.
4. Prüfe, ob **claude-info-display** vorhanden ist. Falls eine Auswahl für diesen Chat angeboten wird, aktiviere sie.

Die lokale Verbindung ist über die Connector-/Werkzeugverwaltung zugänglich. Ihre genaue Anordnung kann je nach App-Version abweichen. [Lokale Verbindungen in Claude Desktop](https://modelcontextprotocol.io/docs/develop/connect-local-servers)

Kopiere zur Prüfung diese Nachricht in den neuen Claude-Chat:

> Prüfe bitte, ob dir die Werkzeuge start_status, report_status und list_status der Verbindung claude-info-display zur Verfügung stehen. Rufe anschließend list_status auf. Starte dabei noch keine neue Display-Aufgabe.

Diese Namen sind die Funktionen unserer Verbindung. Im Alltag bedient Claude sie für dich:

| Werkzeug | Bedeutung |
| --- | --- |
| `start_status` | Eine Aufgabe anmelden |
| `report_status` | Einen neuen Zustand melden |
| `list_status` | Gespeicherte Zustände abfragen |

**Erwartetes Ergebnis:** Claude ruft `list_status` tatsächlich auf und bekommt ein Ergebnis. Eine leere Liste ist beim ersten Mal richtig. Eine reine Textantwort „Ja, ich kann das“ bestätigt die Verbindung noch nicht; achte auf den Werkzeugaufruf und sein Ergebnis.

Meldet Claude fehlende Werkzeuge, gehe zur Fehlerhilfe weiter unten. Ein erneuter Skill-Upload repariert eine fehlende Verbindung nicht.

## Schritt 5: Der erste sichtbare Test

Bleibe zunächst im normalen Desktop-Chat. Kopiere diese Nachricht vollständig hinein:

> Ich nutze den normalen Chat in der Claude-Desktop-App. Verwende den Skill info-display und verfolge die folgende Aufgabe auf meinem Display: Erstelle eine kurze Checkliste mit fünf Punkten. Frage mich zuerst, für welches Thema die Checkliste sein soll, und warte auf meine Antwort. Melde dem Display, wenn du auf mich wartest und wenn die Checkliste fertig ist.

**Jetzt sollte Folgendes passieren:** Claude meldet die Aufgabe an und fragt nach dem Thema. Das Display reagiert auf den Start und zeigt anschließend das wartende Gesicht.

Fragt Claude nach einer Erlaubnis für unsere Statuswerkzeuge, kannst du den jeweiligen Aufruf für diesen Test erlauben. Er speichert den Status lokal und sendet ein Signal an dein Display. Dafür brauchst du keine pauschale Freigabe für andere Werkzeuge.

Antworte auf die Frage nach dem Thema zum Beispiel:

> Für das Packen meines Rucksacks für einen Tagesausflug.

**Danach:** Claude erstellt die Checkliste und meldet den Abschluss. Das Display sollte kurz das Fertig-Gesicht zeigen.

Gib einer Meldung einige Sekunden Zeit. Im Gerätetest dauerten Antworten teilweise vier bis fünf Sekunden. Der Abschluss kann länger brauchen, weil zusätzlich die Aufgabe aus dem Sitzungszähler entfernt wird.

**Der Test ist bestanden, wenn** die Werkzeugaufrufe erfolgreich sind und dein Display sowohl auf das Warten als auch auf den Abschluss reagiert. Eine bloß behauptete Übertragung genügt nicht.

Das Fertig-Gesicht ist nur ungefähr fünf Sekunden sichtbar. Falls du es verpasst hast, prüfe den Geräteverlauf auf deiner vorhandenen Display-Webseite. Die Meldungen heißen dort **Claude App**. Die Webseite muss für die Übertragung nicht geöffnet sein.

## Schritt 6: Automatische Nutzung einschalten

Befolge **AUTOMATIK.md** im selben Ordner. Nach Skill-Update, persönlicher
Daueranweisung und Prüfung der Werkzeugverfügbarkeit sollen normale Anfragen genügen.
Du musst weder den Skill erwähnen noch „arbeitend“ oder „fertig“ selbst setzen.
Prüfe das in einem neuen Chat ohne Display-Anweisung und danach in einem zweiten Chat.

Für eine reine Statusabfrage kannst du weiterhin schreiben:

> Frage mit dem Skill info-display den zuletzt gemeldeten Status dieser Aufgabe ab.

Die Automatik bleibt eine Anweisung an Claude. Sie garantiert keine lückenlose
App-Überwachung. Bei Stopp, Absturz oder Schließen kann die Abschlussmeldung fehlen;
„veraltet“ bedeutet dann nicht „fertig“. Die Gesichter sind außerdem zeitlich begrenzt.

## Schritt 7: Cowork ausprobieren

Teste Cowork erst, wenn der normale Desktop-Chat funktioniert.

1. Öffne eine neue Cowork-Aufgabe in der Desktop-App.
2. Prüfe wie in Schritt 4, ob die drei Statuswerkzeuge verfügbar sind.
3. Falls ja, wiederhole Schritt 5. Ersetze den ersten Satz durch: „Ich nutze Cowork in der Claude-Desktop-App.“
4. Im Geräteverlauf sollten die Meldungen diesmal **Cowork** heißen.

Fehlen die Werkzeuge dort, ist die lokale Verbindung in diesem Modus noch nicht nutzbar. Das kann insbesondere bei entfernt ausgeführten Aufgaben der Fall sein. Der Skill allein macht den lokalen Rechner nicht aus der Cloud erreichbar. Die konkrete Cowork-Kompatibilität ist noch nicht durch einen echten App-Test bestätigt.

## Wenn etwas nicht funktioniert

| Was du siehst | Dein nächster Schritt |
| --- | --- |
| Kein Bereich „Skills“ | Prüfe die Fähigkeiten/Freigaben aus Schritt 3. Bei abweichender Oberfläche notiere die sichtbaren Menünamen. |
| Meldung zum reservierten Wort „claude“ im Skill-Namen | Entferne die bisher ausgewählte ZIP über das X. Wähle die korrigierte `info-display-skill.zip`; die Vorschau muss `info-display` zeigen. |
| Der ZIP-Upload wird abgelehnt | Verwende `info-display-skill.zip`, nicht die entpackte Datei und nicht das portable Gesamtpaket. |
| Skill vorhanden, aber Werkzeuge fehlen | Claude vollständig beenden, neu öffnen und einen neuen Chat starten. Verbindung wie in Schritt 4 prüfen. |
| Die Verbindung wird als fehlerhaft angezeigt | Liegt der Integrationsordner noch am ursprünglichen Ort? Verschieben oder Löschen unterbricht den Start. |
| Claude schreibt über den Status, aber nichts passiert | Verwende den Test aus Schritt 5 und prüfe das Ergebnis des tatsächlichen Werkzeugaufrufs. |
| „Lokal gespeichert; Display nicht erreichbar …“ | Stromversorgung und Netzwerk prüfen. Ist auch die vorhandene Display-Webseite nicht erreichbar, zuerst die Netzwerkverbindung klären. |
| „Fertig“ war nicht zu sehen | Das Gesicht erscheint kurz. Geräteverlauf prüfen oder den Test wiederholen. |
| Ein anderes Gesicht überschreibt die Meldung | Auch Claude Code kann senden. Für den Test dort vorübergehend keine neuen Aufgaben starten. |
| Keine App-Token oder Abolimits | Diese erste Version meldet Arbeitszustände. App-Verbrauch und Abolimits sind noch nicht angebunden; vorhandene Verbrauchswerte können weiterhin von Claude Code stammen. |

Für Hilfe notiere den **Schritt**, den verwendeten Modus (**Chat oder Cowork**) und die **Fehlermeldung**. Den Display-Schlüssel oder andere Zugangsdaten brauchst du nicht mitzuschicken.

## Nur bei Bedarf: Verbindung unabhängig von Claude prüfen

Dieser Test liest den Gerätestatus, ohne eine Aufgabe anzumelden.

1. Öffne über das Windows-Startmenü **PowerShell** ganz normal, nicht „als Administrator“.
2. Kopiere diese Zeile hinein und drücke Enter. Sie wechselt in unseren Integrationsordner:

```powershell
Set-Location -LiteralPath 'C:\Projekte\claudinho_GC9A01\claude-app-integration'
```

3. Kopiere danach diese Zeile hinein und drücke erneut Enter:

```powershell
python server.py --check-device
```

**Bei Erfolg erscheint:** `Display erreichbar; Authentifizierung erfolgreich.`

Wird Python nicht gefunden oder öffnet sich der Microsoft Store, schließe ihn. Installiere nichts nur für den Test; dann muss der vorhandene Python-Pfad geprüft werden. Anschließend kannst du PowerShell schließen.

## Nur für einen weiteren Rechner

Auch wenn der Skill dort schon in deinem Claude-Konto sichtbar ist, braucht ein weiterer Rechner seine eigene lokale Verbindung.

Voraussetzungen: vorhandene Claude-Desktop-App, vorhandenes Python ab Version 3.10, erlaubte lokale MCP-Konfiguration und eine erreichbare Display-IP. Die Display-Konfiguration mit Geräteschlüssel muss ebenfalls auf diesem Rechner vorhanden sein. Sie ist absichtlich nicht im Downloadpaket enthalten. Falls sie noch fehlt, muss zuerst diese Verbindung eingerichtet werden; das folgende Skript überträgt den Schlüssel nicht automatisch.

1. Speichere **claude-info-display-clean.zip** auf dem weiteren Rechner.
2. Entpacke dieses Gesamtpaket im Explorer über **Alle extrahieren** in einen dauerhaften Ordner mit Schreibzugriff.
3. Öffne den enthaltenen Ordner `claude-app-integration`. Dort müssen `setup.py` und `server.py` liegen.
4. Kopiere den Ordnerpfad aus der Explorer-Adressleiste.
5. Öffne PowerShell und gib `Set-Location -LiteralPath 'DEIN ORDNERPFAD'` ein. Ersetze `DEIN ORDNERPFAD` durch den kopierten Pfad; behalte die einfachen Anführungszeichen bei.
6. Führe anschließend diese Zeile aus:

```powershell
python setup.py --apply
```

Das ergänzt die Verbindung und sichert eine bestehende Claude-Konfiguration. Es installiert keine Python-Pakete. Bei einer Fehlermeldung diese zuerst prüfen lassen.

7. Prüfe mit `python server.py --check-device`, ob die Verbindung funktioniert.
8. Fahre mit Schritt 2 dieser Anleitung fort. Ist der Skill im gewählten Konto schon aktiv, überspringe den erneuten Upload.

**Auf dem bereits eingerichteten Rechner ist dieser Abschnitt nicht erforderlich.** Verschiebe den vorhandenen Integrationsordner dort bitte nicht, solange Claude ihn verwendet.

## Bereits geprüft und noch offen

- Die lokale Verbindung ist in die bestehende Claude-Konfiguration eingetragen; andere Einstellungen wurden beibehalten.
- Zwölf automatisierte Funktionstests haben bestanden.
- Arbeiten, Warten und Fertig wurden im echten Geräteverlauf bestätigt. Die Testsitzung wurde entfernt.
- Die Automatik ohne ausdrücklichen Display-Auftrag wurde in einem Claude-Chat bestätigt. Weitere neue Chats und Cowork müssen separat geprüft werden; siehe AUTOMATIK.md.

Technische Details zu Datenformat, Speicherung, Firmware-Ereignissen, weiteren Tests und Rückbau stehen in **TECHNIK.md** im selben Ordner. Für die normale Nutzung genügt diese Anleitung.
