# Automatische Statusmeldungen einschalten

## Aktuelle Version 0.2.2

Der erste Aufruf sendet `prompt` (nachdenklich). Die Werkzeugantwort erinnert Claude
an die noch nötige Warte- oder Abschlussmeldung. Der Server prüft die Bestätigung des
Displays, bevor er eine Übertragung als erfolgreich meldet. Nach einem Server-Update
Claude vollständig neu starten. Ein erneuter Skill-Import ist nur bei Änderungen am
Skill nötig; die automatische Skill-Version bleibt beim Update auf 0.2.2 unverändert.

Ein eingeschalteter Skill ist nicht automatisch in jedem Chat vollständig geladen.
Claude wählt passende Skills dynamisch aus. Für den gewünschten Standardbetrieb
kombinieren wir deshalb den Skill mit einer persönlichen Daueranweisung.
Das ist eine Modellanweisung, keine garantierte Überwachung der App.
[Wie Skills geladen werden](https://support.claude.com/en/articles/12512176-what-are-skills)

## 1. Den vorhandenen Skill ersetzen

Öffne Einstellungen → Anpassen → Skills und suche `info-display`. Aktualisiere ihn
über die angebotene Bearbeitungs-/Uploadfunktion mit der neuen `info-display-skill.zip`.
Falls deine Version kein Ersetzen anbietet, entferne nur diesen selbst hochgeladenen
Skill und lade die neue ZIP erneut hoch. Aktiviere ihn danach. Nicht beide Versionen
nebeneinander aktiv lassen. In der Beschreibung steht jetzt „Melde automatisch bei
jeder Nutzernachricht …“.

## 2. Eine persönliche Daueranweisung hinzufügen

Öffne Einstellungen → Allgemein und suche **Anweisungen für Claude / Instructions
for Claude**. Ergänze den folgenden Absatz bei deinen vorhandenen Anweisungen;
überschreibe deine bisherigen Einstellungen nicht. Speichere die Änderung.
Bei älteren Oberflächen mit getrenntem Cowork können dafür zusätzlich dessen
Global Instructions unter Einstellungen → Cowork erforderlich sein.
[Persönliche Anweisungen](https://support.claude.com/en/articles/10185728-understanding-claude-s-personalization-features),
[Cowork-Anweisungen](https://support.claude.com/en/articles/13345190-get-started-with-claude-cowork)

### Diesen Absatz kopieren

Nutze bei jeder meiner Nachrichten automatisch den Skill info-display, sofern die Verbindung claude-info-display verfügbar ist. Melde den Beginn der Bearbeitung, notwendige Rückfragen und den Abschluss der aktuellen Anfrage selbstständig über die Statuswerkzeuge. Ich möchte dafür keinen gesonderten Auftrag geben und die Zustände nicht manuell setzen. Verwende nur neutrale Titel wie „Claude App“ oder „Cowork“ und keine Gesprächsinhalte. Beachte, wenn ich die Anzeige ausdrücklich ausschalte. Wenn die Verbindung fehlt oder ausfällt, bearbeite meine eigentliche Anfrage trotzdem weiter und behaupte keine erfolgreiche Übertragung.

Derselbe Text liegt zum einfachen Kopieren in `PERSOENLICHE-ANWEISUNG.txt`.
Diese Kontoeinstellung wurde hier nicht automatisch geändert.

## 3. Verbindung laden und Werkzeugfreigaben prüfen

Beende Claude vollständig und öffne es wieder: Die lokale Verbindung muss ihre
aktualisierte Anweisung laden. Ihre Konfiguration und ihr Name bleiben gleich.

Beginne einen neuen Chat. Falls vorhanden, wähle über + → Konnektoren → Werkzeugzugriff
**Immer verfügbar / Always available**. Laut Dokumentation gilt diese Auswahl nur
für den jeweiligen Chat; sie ist kein bestätigter globaler Schalter für alle neuen
Chats. Sie macht die Werkzeuge verfügbar, erzwingt aber weder Skill-Laden noch Aufrufe.
[Werkzeugzugriff](https://support.claude.com/en/articles/13730515-manage-claude-s-tool-access)

Falls Claude für jede Statusmeldung nach Erlaubnis fragt, prüfe bei genau diesen
Statuswerkzeugen, ob deine App **Immer erlauben / Always allow** anbietet. Das ist
etwas anderes als „Immer verfügbar“. Eine solche Freigabe wird hier nicht gesetzt;
es ist keine allgemeine Freigabe für andere Werkzeuge erforderlich. Firmenrichtlinien
können weiterhin Bestätigungen verlangen.
[Cowork-Berechtigungen](https://support.claude.com/en/articles/13345190-get-started-with-claude-cowork)

## 4. Automatik ohne manuelle Statusanweisung testen

Sende in einem neuen Chat nur:

> Erstelle eine Checkliste mit fünf Punkten. Frage mich zuerst, für welches Thema.

Erwähne diesmal weder den Skill noch das Display. Erwartet werden ein Startsignal
und danach „Wartet auf dich“. Antworte dann:

> Für einen Tagesausflug.

Erwartet werden erneute Bearbeitung und anschließend „Fertig“. Sende danach eine
weitere normale Nachricht, etwa „Ergänze einen Punkt zum Wetter“. Auch darauf müssen
die Zustände ohne Erinnerung wechseln. Wiederhole den Ablauf in einem zweiten neuen
Chat. Erst dann ist die Aktivierung auch über Chatgrenzen hinweg praktisch bestätigt.

Wenn der Ablauf nur nach Nennung von `info-display` funktioniert, ist die automatische
Aktivierung noch nicht erfolgreich. Prüfe Daueranweisung, aktive Skill-Version,
Verfügbarkeit der Werkzeuge und gegebenenfalls deren Berechtigungen. Einzelne
manuell erfolgreiche Signale sind kein Nachweis für autonomes Verhalten.

## Was diese Lösung nicht zuverlässig erfassen kann

- Das erste Denken vor dem ersten Werkzeugaufruf und lückenlose Aktivität beim Denken.
- Schließen der App, Absturz, Netzwerkverlust oder Betätigen des Stopp-Knopfs.
- Fortlaufende Sekunden-Updates: Es gibt keinen unabhängigen Hintergrund-Heartbeat.
- Gleichzeitige Chats als getrennte Gesichter: Die Firmware zeigt das letzte Ereignis.

Eine fertige Antwort wird kurz vor ihrem Textabschluss gemeldet; es gibt hier kein
technisches Ereignis nach dem tatsächlichen Ende der Ausgabe. Bei einer notwendigen
Rückfrage bleibt die Anzeige wartend. Aktive Meldungen werden nach Ablauf als unbekannt
behandelt, nicht automatisch als abgeschlossen.

Für deterministische Lebenszyklusmeldungen braucht es Hooks im ausführenden Produkt.
Die aktuelle Dokumentation unterscheidet Cowork/Claude Code mit Plugin-Hooks und
normalen Chat ohne diese Hooks. Ob die nötigen Hooks in deiner konkreten
Cowork-Version verfügbar sind, muss gesondert geprüft werden; sie sind nicht Teil
dieses Skill-Updates.
[Plugin-Funktionen je Oberfläche](https://support.claude.com/en/articles/13837440-use-plugins-in-claude)

## Prüfstand

Der Test in einem echten Claude-Chat wurde erfolgreich durchgeführt: Eine normale
Checklisten-Anfrage löste ohne Display-Auftrag `working` und `waiting_for_user` aus.
Nach der Antwort zum Thema folgten erneut `working` und `completed`; die letzte
Übertragung wurde bestätigt. Die Wiederholung in weiteren neuen Chats und Cowork
ist noch separat zu prüfen. Die automatisierten Tests können keine Entscheidung
des Claude-Modells vorhersagen.
