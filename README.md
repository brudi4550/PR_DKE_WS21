# PR_DKE_WS21
Implementierung von Informationssystemen in einem Bahnunternehmen.<br>

Verantwortlicher Fahrplansystem: Alexander Wolf<br>
Verantwortlicher Flottensystem: Anil Yildiz<br>

Zum (erstmaligen) Starten des Systems:
```bash
git clone https://github.com/brudi4550/PR_DKE_WS21.git
cd PR_DKE_WS21
./install.sh
./run.sh
```
  
Bei weiteren Starts muss nur mehr run.sh ausgeführt werden.  
Falls sich Dependencies ändern, kann install.sh erneut ausgeführt werden.  

Bei keinen Parametern versucht run.sh alle Systeme zu starten.<br>
Es kann auch angegeben werden welche Systeme gestartet werden sollen.<br>
Reihenfolge der Parameter spielt keine Rolle.<br>
Parameter:<br>
fa (Fahrplansystem)<br>
fl (Flottensystem)<br>
st (Streckensystem)<br>
ti (Ticketsystem)<br>
q  (quiet - Keine Flask Informationen anzeigen)<br>

Also z.B. <br>
```bash
./run.sh fa q
```
oder<br>
```bash
./run.sh st ti fl
```

## Fahrplaninformationssystem
Das Fahrplaninfomrationssystem verwendet Daten aus dem Flottensystem und dem
Streckensystem und verarbeitet diese weiter. Ein Ticketsystem kann über die API
nach Durchführungen und den dazugehörigen Preisen suchen.

### Funktionalitäten
Einfache Benutzer (Mitarbeiter, Lokführer, Kontrolleur) hinzufügen und verwalten.  
Admins hinzufügen und verwalten.  
  
Benutzer zu Bordpersonalteams zuteilen.  
  
Eine Fahrt für eine Strecke aus dem Streckensystem anlegen.  
Einmalige Durchführung für diese Fahrt hinzufügen.  
Intervall-Durchführung für diese Fahrt hinzufügen.  
Stoßzeiten für Fahrten hinzufügen (Durchführungen in Stoßzeit werden höher bepreist).  
  
Routen für automatische Überprüfungen (über cron jobs) von:  
-Fahrplan (alte Durchführungen entfernen, neue Durchführungen nach angegebenem
Intervall hinzufügen)  
-Warnungen der Strecken-API (Bekannte Warnungen werden verglichen, bei neuen Warnungen
wird der Fahrplan auf betroffene Durchführungen überprüft. Betroffene Durchführungen 
werden entfernt)  
-Wartungen der Züge aus der Flotten-API (Gleiches Prinzip wie bei der Strecken-API)  
  
API zum Durchsuchen des Fahrplans. Preise wie auch Tickets sind nicht eingeschränkt
auf eine gesamte Strecke. Input sind Start- und Endpunkt als auch der späteste
Abfahrtszeitpunkt.  


### Sonstiges
Admin-Login für lokales Fahrplansystem:  
Mitarbeiter-ID: 1  
Passwort: 1234  
  
Bis Februar 2022 ist das Fahrplansystem auch auf diesem VPS deployed:  
52.29.120.183  

## Flottensystem
Das Flotteninformationssystem stellt dem Fahrplaninformationssystem und dem 
Ticketinformationssystem Daten zur Verfügung.

###Funktionalitäten
Das Hinzufügen eines Mitarbeiters, wobei ein Mitarbeiter ein Administrator,
Wartungspersonal oder Zugpersonal ist.

Erstellen/Bearbeiten/Löschen von Waggons.

Erstellen/Bearbeiten/Löschen von Zügen, wobei bei der Erstellung und Bearbeitung
darauf geachtet werden muss, dass die Spurweite der einzelnen Waggons einheitlich 
sind.

Erstellen/Bearbeiten/Löschen von Wartungen, wobei hier darauf geachtet werden muss,
dass die Mitarbeiter (die der Wartung zugeordnet werden) in dem angegebenen Zeitraum
keine andere Wartung durchführen. Zusätzlich muss darauf geachtet werden, dass für
den Zug in dem angegebenen Zeitraum bereits keine Wartung durchgeführt wird.

Übersicht über folgende Daten:
-Waggons
-Züge
-Wartungen
-Benutzer

Mitarbeiter mit nur lesenden Rechten (also alle Mitarbeiter, außer Administratoren) 
haben nur Zugriff auf die Übersichtsseiten, jedoch auch nicht auf alle (die Seite
"Benutzerübersicht" steht ebenfalls nur Administratoren zur Verfügung, der Grund dafür
wird im Code beschrieben)

API zum Bereitstellen von Zug- und Wartungsdaten. Weitere API's die implementiert wurden,
sind Waggons und Mitarbeiter (Einzelheiten werden im Code erklärt)

###Sonstiges
Admin-Login für lokales Flottensystem:<br>
Mitarbeiter-Email: anil@hotmail.com<br>
Passwort: test<br>
