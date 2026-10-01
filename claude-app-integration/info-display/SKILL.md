---
name: info-display
description: "Melde automatisch bei jeder Nutzernachricht in Claude Chat oder Cowork den Arbeitsstatus an das verbundene Info-Display: Beginn, Rückfrage und Abschluss. Kein gesonderter Display-Auftrag nötig."
---

# Info-Display: automatische Meldungen

Der Nutzer möchte Statusmeldungen als Standard für seine eigenen Unterhaltungen.
Wenn dieser Skill geladen und die lokale Verbindung verfügbar ist, führe die
folgenden Schritte selbstständig aus. Verlange keinen zusätzlichen Display-Auftrag
und bitte den Nutzer nicht, Zustände manuell zu setzen. Ein ausdrücklicher Wunsch,
die Anzeige auszusetzen, hat Vorrang. Berechtigungen des Hosts bleiben maßgeblich.

## Bei jeder neuen Nutzernachricht

1. Verwende die verbundenen Werkzeuge `start_status`, `report_status`, `list_status`.
   Falls nötig, suche diese Werkzeuge über die Werkzeugauswahl des Hosts.
   Sind sie nicht verfügbar, bearbeite die eigentliche Anfrage weiter. Melde eine
   fehlende Verbindung einmal knapp, nicht bei jeder weiteren Nachricht.
2. Ohne eine diesem Chat sicher zugeordnete `session_id`: Rufe `start_status` auf.
   Nutze eine neue eindeutige `request_id` und den neutralen Titel „Claude App“
   beziehungsweise „Cowork“. `surface` ist `claude_chat` oder `claude_cowork`.
   Verwende bei unklarer Oberfläche `claude_chat` als Anzeige-Standard; stelle
   deshalb keine Rückfrage. Das Feld ist ein Label, keine gemessene App-Identität.
   Bewahre `session_id` und `revision` im Gesprächskontext auf. `start_status`
   setzt bereits `working`; ein sofortiger doppelter Aufruf ist unnötig.
3. Bei bekannter Sitzungs-ID: Melde vor der inhaltlichen Bearbeitung `working`
   über `report_status`, auch wenn die vorige Nachricht schon abgeschlossen war.
   Nutze dieselbe Sitzung weiter. Nach Kontextverlust keine fremde Sitzung anhand
   eines ähnlichen Titels übernehmen; im Zweifel neu registrieren.
4. Unmittelbar vor einer notwendigen Rückfrage oder einer selbst eingeleiteten
   Freigabeanfrage: Melde `waiting_for_user`. Nach der Antwort gilt wieder Schritt 3.
5. Vor deiner abschließenden Antwort: Melde `completed`, wenn die Bearbeitung der
   aktuellen Anfrage abgeschlossen ist. Das bedeutet „für diese Anfrage fertig“,
   nicht, dass ein übergeordnetes Projekt abgeschlossen oder die App geschlossen ist.
   Endet die Antwort mit einer notwendigen Rückfrage, bleibt `waiting_for_user`.
   Zwischenberichte sind kein Abschluss. Setze eine wartende Meldung nicht sofort
   durch `completed` zurück.
6. Melde `error` nur bei einem tatsächlich nicht fortsetzbaren Fehler der Aufgabe.
   Melde `cancelled` nur bei einem beobachteten Abbruchauftrag. Ein technischer
   Stopp-Knopf oder das Schließen der App ist möglicherweise nicht beobachtbar.

Nutze neue `event_id`-Werte je Meldung und die zuletzt bestätigte `revision` als
`expected_revision`. Bei Transportproblemen höchstens einmal mit identischen
Argumenten wiederholen. Bei Revisionskonflikt zuerst `list_status` für die bekannte
Sitzung lesen und prüfen, ob die beabsichtigte Meldung noch aktuell ist.

Melde bei längerer Arbeit auch an sinnvollen Zwischenständen `working`. Starte
keine künstliche Schleife oder Hintergrundaufgabe nur für Statusmeldungen. Es gibt
keinen unabhängigen Heartbeat; während langen Denkens kann kein Werkzeugaufruf
stattfinden. Zeitlich begrenzte Gesichter sind kein dauerhafter Aktivitätsnachweis.

## Übertragung und Datenschutz

Prüfe `display_delivery.state`: Nur `sent` oder `already_sent` bestätigen die
Übertragung. `failed` bedeutet lediglich lokal gespeichert; bei `skipped` oder
`disabled` wurde nicht neu übertragen. Behaupte dann keine erfolgreiche Zustellung.
Ein ausgefallenes Display darf die eigentliche Aufgabe nicht verhindern.
Erfolgreiche Meldungen brauchen keinen zusätzlichen Erklärungstext im Chat;
Werkzeugaufrufe können in der Oberfläche trotzdem sichtbar bleiben.

Sende neutrale Titel und leere oder rein technische Kurzmeldungen. Keine Prompts,
Dateinamen, Dokumentinhalte oder Zugangsdaten übertragen. Bearbeite nur die Sitzung
dieses Chats; überwache keine anderen Chats durch Polling. Wenn der Nutzer die
Automatik deaktiviert, melde für die bekannte aktive Sitzung einmal `cancelled`,
sofern die Verbindung verfügbar ist, und sende danach nichts bis zur Reaktivierung.

## Statusabfrage und Grenzen

Bei einer expliziten Statusabfrage `list_status` verwenden. Unterscheide aktuelle
Meldungen von `stale`/`unknown`. Die Meldungen sind Selbstauskünfte, keine Messung
der App. Tokenverbrauch und Abolimits sind nicht verfügbar: keine Werte schätzen;
`null` bedeutet unbekannt, nicht null Verbrauch.

Ein Skill erzwingt seine eigene Aktivierung nicht. Eine dauerhafte persönliche
Anweisung muss den Host auffordern, ihn bei jeder Nachricht zu verwenden; auch das
ist keine garantierte Ereignisschnittstelle. Führe keine Ersatzskripte in einer
Cloud-Sandbox aus: deren Dateien sind nicht die lokalen Dateien des Rechners.
