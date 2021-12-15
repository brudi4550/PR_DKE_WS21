# PR_DKE_WS21
Implementierung von Informationssystemen in einem Bahnunternehmen.

Verantwortlicher Fahrplansystem: Alexander Wolf<br>
Verantwortlicher Flottensystem: Anil Yildiz<br>
Verantwortlicher Streckensystem: Thomas Weißenbacher

Zum (erstmaligen) Starten des Systems:
1. Repository klonen
2. ./install.sh
3. ./run.sh

Bei weiteren Starts muss nur mehr run.sh ausgeführt werden.
Falls sich Dependencies ändern, kann install.sh erneut ausgeführt werden.

Bei keinen Argumenten versucht run.sh alle Systeme zu starten.
Es können auch die Systeme angegeben werden, die gestartet werden sollen.
Reihenfolge der Argumente spielt keine Rolle.
Argumente:
fa (Fahrplansystem)
fl (Flottensystem)
st (Streckensystem)
ti (Ticketsystem)
q  (quiet - Keine Flask error messages anzeigen)

Also z.B. 
./run.sh fa q
oder
./run.sh st ti fl 
