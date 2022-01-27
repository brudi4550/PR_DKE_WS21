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
./run.sh fa q<br>
oder<br>
./run.sh st ti fl <br>

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
<br>
Admin-Login für lokales Flottensystem:<br>
Mitarbeiter-Email: anil@hotmail.com<br>
Passwort: test<br>
