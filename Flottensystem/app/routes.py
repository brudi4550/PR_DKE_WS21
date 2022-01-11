from datetime import datetime
from flask import render_template, flash, redirect, url_for, request
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.urls import url_parse
from app import app, db
from app.forms import LoginForm, RegistrationForm, RegistrationFormZugpersonal, EmptyForm, EditProfileForm, \
    EditProfileFormZugpersonal, TriebwagenForm, PersonenwagenForm, EditTriebwagenForm, EditPersonenwagenForm, \
    ZugForm, EditZugForm, WartungForm, EditWartungForm
from app.models import Mitarbeiter, Wartungspersonal, Zugpersonal, Administrator, Wagen, Triebwagen, Personenwagen, \
    Zug, Wartung


@app.route('/')
@app.route('/Startseite')
def home():
    if current_user.is_authenticated:   # Falls der Benutzer schon angemeldet ist, wird dieser in die jeweilige Seite weitergeleitet
        if Administrator.query.filter_by(mitarbeiterNr=current_user.mitarbeiterNr).first() is not None:
            next_page = url_for('home_admin')
        else:
            next_page = url_for('home_personal')
        return redirect(next_page)
    return render_template('home.html', title='Startseite - Flotteninformationssystem')


@app.route('/Startseite/Admin')
@login_required
def home_admin():
    if Administrator.query.filter_by(mitarbeiterNr=current_user.mitarbeiterNr).first() is None: # Hier wird kontrolliert, ob der angemeldete Benutzer kein Administrator ist. Ist dies der Fall, wird dieser in die Personalseite weitergeleitet (wo man auch keine Administratorrechte hat)
        flash('Sie müssen als Administrator angemeldet sein, um in die Administrator-Startseite zu gelangen!')  # Anschließend wird diese Meldung mitgegeben, um den Benutzer darüber zu informieren, warum dieser nicht auf diese Webseite zugreifen kann
        return redirect(url_for('home_personal'))
    return render_template('home_administrator.html', title='Startseite - Flotteninformationssystem')


@app.route('/Startseite/Personal')
@login_required
def home_personal():
    if Administrator.query.filter_by(mitarbeiterNr=current_user.mitarbeiterNr).first() is not None: # Falls es sich beim angemeldet User um einen Administrator handelt, wird dieser in die Administrator-Startseite weitergeleitet
        flash('Sie sind als Administrator angemeldet!')
        return redirect(url_for('home_admin'))
    return render_template('home_personal.html', title='Startseite - Flotteninformationssystem')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:   # Ist der Nutzer schon angemeldet, dann hat dieser keinen Zugriff auf die Login-Webseite und wird entsprechend weitergeleitet
        if Administrator.query.filter(mitarbeiterNr=current_user.mitarbeiterNr).first() is not None:
            return redirect(url_for('home_admin'))
        else:
            return redirect(url_for('home_personal'))
    form = LoginForm()
    if form.validate_on_submit():   # Drückt man beim Login auf den Submit-Button, dann ist diese Bedingung True
        user = Mitarbeiter.query.filter_by(email=form.email.data).first()   # Es wird über die gesamte Mitarbeitertabelle hinweg die eingegebene Email Adresse gesucht
        if user is None or not user.check_password(form.passwort.data): # Falls kein User unter der angegebenen Email Adresse gefunden wurde oder das Passwort vom User falsch eingegeben wurde, dann wird die folgende Fehlermeldung ausgegeben und der Benutzer muss sich nochmal anmelden
            flash('Email bzw. Passwort ungültig!')
            return redirect(url_for('login'))
        login_user(user, remember=form.angemeldet_bleiben.data) # Das Login wird durchgeführt und es wird sich auch gemerkt, ob die Checkbox "angemeldet_bleiben" angekreuzt worden ist
        next_page = request.args.get('next')    # Wurde ein Benutzer von einer anderen Seite in das Login weitergeleitet, so wird diese vorherige Seite (auf die man zugreifen wollte) in next_page gespeichert
        if not next_page or url_parse(next_page).netloc != '':
            if Administrator.query.filter_by(mitarbeiterNr=user.mitarbeiterNr).first() is not None:
                next_page = url_for('home_admin')
            else:
                next_page = url_for('home_personal')
        return redirect(next_page)
    return render_template('login.html', title='Anmelden', form=form)

    
@app.route('/logout')
def logout():
    logout_user()   # Hier wird der User ausgeloggt und in die Startseite weitergeleitet
    return redirect(url_for('home'))


@app.route('/register')
@login_required
def register():
    if Administrator.query.filter_by(mitarbeiterNr=current_user.mitarbeiterNr).first() is None: # Hier wird überprüft, ob ein Administrator auf diese Webseite zugreift. ist dies nicht der Fall, wird der User in die Personal-Startseite weitergeleitet
        flash('Sie müssen als Administrator angemeldet sein, um einen neuen Benutzer erstellen zu können!')
        return redirect(url_for('home_personal'))
    return render_template('register.html', title='Benutzer erstellen')


@app.route('/registerUser/<name>', methods=['GET', 'POST'])
@login_required
def registerUser(name):
    if Administrator.query.filter_by(mitarbeiterNr=current_user.mitarbeiterNr).first() is None: # Hier wird überprüft, ob ein Administrator auf diese Webseite zugreift. ist dies nicht der Fall, wird der User in die Personal-Startseite weitergeleitet
        flash('Sie müssen als Administrator angemeldet sein, um einen neuen Benutzer erstellen zu können!')
        return redirect(url_for('home_personal'))
    if name == 'Zugpersonal':   # Es wird überprüft, ob im übergebenen Parameter 'name' 'Zugpersonal' eingetragen ist. Ist dies der Fall wird ein Formular für das Zugpersonal verwendet der eine kleine Abweichung im Unterschied zu den anderen Mitarbeitern enthält
        form = RegistrationFormZugpersonal()
        ''' Als nächstes werden die Zugnummern dynamisch dem SelectField "zugNr" übergeben. Auch der User sieht bei der Beschriftung die Zugnummer
            (rechter Ausruck von (z.nr, z.nr)). Hier wird dem User bewusst nicht der Name des Zuges (also (z.nr, z.name)) angezeigt, da Zugnamen 
            redundant sein können und der User somit nicht wissen kann, welches Feld im SelectField nun das gewünschte ist. Als Beispiel kann man
            den Zugnamen Railjet nehmen: Es gibt Railjet Züge mit unterschiedlichen Zugnummern (z.B.: RJX 368, RJX 660, usw.). Jedoch haben all
            diese Zugnummern den gleichen Zugnamen, nämlich "Railjet". Würde man somit dem User beim SelectField den Zugnamen anzeigen (also indem 
            man in der nachfolgenden Zeile (z.nr, z.name) eingibt), dann würde nur "Railjet" stehen und der User wüsste dadurch nicht, welches sein 
            gewünschter Zug ist. '''
        form.zugNr.choices = [(z.nr, z.nr) for z in Zug.query.all()]
    else:   # Ist im Parameter 'name' nicht 'Zugpersonal' eingetragen, so wird das andere Formular für die Registrierung eines Users verwendet
    	form = RegistrationForm()
    if form.validate_on_submit():
        if name == 'Administrator':
            user = Administrator(mitarbeiterNr=form.mitarbeiterNr.data, svnr=form.svnr.data, vorname=form.vorname.data, nachname=form.nachname.data, email=form.email.data)
        elif name == 'Wartungspersonal':
            user = Wartungspersonal(mitarbeiterNr=form.mitarbeiterNr.data, svnr=form.svnr.data, vorname=form.vorname.data, nachname=form.nachname.data, email=form.email.data)
        elif name == 'Zugpersonal':
            user = Zugpersonal(mitarbeiterNr=form.mitarbeiterNr.data, svnr=form.svnr.data, vorname=form.vorname.data, nachname=form.nachname.data, email=form.email.data, berufsbezeichnung=form.berufsbezeichnung.data, zugNr=form.zugNr.data)
        user.set_password(form.passwort.data)
        db.session.add(user)
        db.session.commit() # Hier werden die Daten persistiert
        flash('Benutzer wurde erfolgreich erstellt!')
        return redirect(url_for('register'))
    return render_template('register_user.html', title=name + ' erstellen', form=form, typ=name)


@app.route('/User_bearbeiten')
@login_required
def updateUser():
    if Administrator.query.filter_by(mitarbeiterNr=current_user.mitarbeiterNr).first() is None: # Auch hier werden User, die nicht Administrator sind, in die Personal-Startseite weitergeleitet
        flash('Sie müssen als Administrator angemeldet sein, um einen Benutzer bearbeiten zu können!')
        return redirect(url_for('home_personal'))
    wartungspersonal = Wartungspersonal.query.all()
    zugpersonal = Zugpersonal.query.all()
    form = EmptyForm()
    return render_template('user.html', wartungspersonal=wartungspersonal, zugpersonal=zugpersonal, form=form)  # Wartungs- und Zugpersonal werden auch übergeben, um diese nachfolgend auf der Webseite darzustellen
    
    
@app.route('/User_bearbeiten/<mitarbeiterNr>', methods=['GET', 'POST'])
@login_required
def editUser(mitarbeiterNr):
    if Administrator.query.filter_by(mitarbeiterNr=current_user.mitarbeiterNr).first() is None: # Auch hier werden User, die nicht Administrator sind, in die Personal-Startseite weitergeleitet
        flash('Sie müssen als Administrator angemeldet sein, um einen Benutzer bearbeiten zu können!')
        return redirect(url_for('home_personal'))
    user = Mitarbeiter.query.filter_by(mitarbeiterNr=mitarbeiterNr).first()
    if user is None:    # Wird unter der übergebenen Mitarbeiternummer kein User gefunden, so wird der Benutzer darüber informiert
        flash('Es wurde kein Mitarbeiter unter der Mitarbeiternummer {} gefunden!'.format(mitarbeiterNr))
        return redirect(url_for('updateUser'))
    elif type(user) == Administrator and user.mitarbeiterNr != current_user.mitarbeiterNr:  # Hier wird verhindert, dass die Daten eines anderen Administrators geändert werden
        flash('Sie dürfen die Daten eines anderen Administrators nicht bearbeiten!')
        return redirect(url_for('updateUser'))
    elif type(user) == Zugpersonal:
        typ = 'Zugpersonal'
        form = EditProfileFormZugpersonal(user.mitarbeiterNr, user.svnr, user.email)
        form.zugNr.choices = [(z.nr, z.nr) for z in Zug.query.all()]
    else:
        typ = 'Wartungspersonal'
        form = EditProfileForm(user.mitarbeiterNr, user.svnr, user.email)
    if form.validate_on_submit():
        user.mitarbeiterNr = form.mitarbeiterNr.data
        user.svnr = form.svnr.data
        user.vorname = form.vorname.data
        user.nachname = form.nachname.data
        user.email = form.email.data
        if typ == 'Zugpersonal':
            user.berufsbezeichnung = form.berufsbezeichnung.data
            user.zugNr = form.zugNr.data
        db.session.commit()
        flash('Änderungen wurden erfolgreich durchgeführt!')
        return redirect(url_for('updateUser'))
    elif request.method == 'GET':   # Ist die Abfragemethode 'GET', dann wird das Formular mit den Daten des jeweiligen Mitarbeiters angezeigt
        form.mitarbeiterNr.data = user.mitarbeiterNr
        form.svnr.data = user.svnr
        form.vorname.data = user.vorname
        form.nachname.data = user.nachname
        form.email.data = user.email
        if typ == 'Zugpersonal':
            form.berufsbezeichnung.data = user.berufsbezeichnung
            form.zugNr.data = user.zugNr
    return render_template('edit_user.html', title='User bearbeiten', form=form, typ=typ)

@app.route('/User_löschen/<mitarbeiterNr>', methods=['POST'])
@login_required
def deleteUser(mitarbeiterNr):
    if Administrator.query.filter_by(mitarbeiterNr=current_user.mitarbeiterNr).first() is None:
        flash('Sie müssen als Administrator angemeldet sein, um einen Benutzer löschen zu können!')
        return redirect(url_for('home_personal'))

    mitarbeiter = Mitarbeiter.query.filter_by(mitarbeiterNr=mitarbeiterNr).first()
    if mitarbeiter is None: # Wird der Mitarbeiter nicht gefunden, so kann dieser auch nicht gelöscht werden. Diese Meldung wird dem User übergeben.
        flash('Löschen eines nicht vorhandenen Mitarbeiters nicht möglich')
        return redirect(url_for('updateUser'))

    # Da man Administratoren auch nicht zu viele Rechte geben will (da dies dann das Potential zu einem Machtmissbrauch hat), dürfen Administratoren
    # keine anderen Administratoren löschen, sich selbst jedoch schon. In der folgenden Überprüfung wird verhindert, dass ein Administrator einen
    # anderen Administrators löscht.
    elif type(mitarbeiter) == Administrator and mitarbeiter.mitarbeiterNr != current_user.mitarbeiterNr:
        flash('Löschen eines anderen Administrators ist nicht erlaubt!')
        return redirect(url_for('updateUser'))

    form=EmptyForm()

    if form.validate_on_submit():
        db.session.delete(mitarbeiter)
        ''' Es wird in der nachfolgenden if-Abfrage überprüft, ob es sich beim gelöschten Mitarbeiter um einen Wartungspersonalmitarbeiter
            handelt. Ist dies der Fall, dann werden alle Wartungen von diesem Wartungspersonalmitarbeiter überprüft (falls welche vorhanden sind) '''
        if type(mitarbeiter) == Wartungspersonal:
            wartungen = mitarbeiter.wartungen.all()
            if wartungen is not None:
                ''' In diesen Wartungen von dem gelöschten Wartungspersonalmitarbeiter wird überprüft, ob noch Mitarbeiter vorhanden sind. Falls 
                    nicht, dann wird die Wartung ebenfalls gelöscht, da einer Wartung Wartungspersonalmitarbeiter zugeteilt sein müssen. Dies 
                    musste so realisiert werden, da durch das setzen eines Cascade-Constraints (cascade="all, delete") in der  Klasse "Wartungspersonal" 
                    in "models.py" bewirken würde, dass das Löschen eines Wartungspersonalmitarbeiters alle Wartungen löscht, in der dieser zugeteilt
                    war, auch wenn in den Wartungen noch weitere Wartungspersonalmitarbeiter zugeteilt worden wären. Also wird durch diese Abfrage 
                    sichergestellt, dass eine Wartung erst dann gelöscht wird, wenn diesem keine Wartungspersonalmitarbeiter zugeteilt sind '''
                for wartung in wartungen:
                    if wartung.zugeordnetes_wartungspersonal() is None:
                        db.session.delete(wartung)

        db.session.commit()
        ''' Es wird hier überprüft, ob der Administrator einen anderen User als sich selbst gelöscht hat '''
        if Administrator.query.filter_by(mitarbeiterNr=current_user.mitarbeiterNr).first() is not None:
            flash('Löschen des Mitarbeiters {} {} mit der Mitarbeiternummer {} wurde erfolgreich durchgeführt'.format(mitarbeiter.vorname, mitarbeiter.nachname, mitarbeiterNr))
            return redirect(url_for('updateUser'))
        # Kann der Administrator sich selbst in der vorherigen Abfrage nicht finden, dann heißt es, dass dieser sich selbst gelöscht hat.
        else:
            flash('Sie haben Ihr Profil erfolgreich gelöscht!')
            return redirect(url_for('login'))
    else:
        return redirect(url_for('updateUser'))


@app.route('/Profil', methods=['GET', 'POST'])
@login_required
def profile():  # Bei der Änderung eines Profils wird zwischen einem Administrator und den anderen Personalarten unterschieden. Ein Administrator kann die eigenen Daten verändern, während normales Personal nur Leserechte hat
    user = Mitarbeiter.query.filter_by(mitarbeiterNr=current_user.mitarbeiterNr).first()
    if type(user) == Administrator:
        typ = 'Administrator'
        form = EditProfileForm(user.mitarbeiterNr, user.svnr, user.email)
        form2 = EmptyForm()
    elif type(user) == Wartungspersonal:
        typ = 'Wartungspersonal'
    else:
        typ = 'Zugpersonal'
        
    if type(user) == Administrator and form.validate_on_submit():
        user.mitarbeiterNr = form.mitarbeiterNr.data
        user.svnr = form.svnr.data
        user.vorname = form.vorname.data
        user.nachname = form.nachname.data
        user.email = form.email.data
        db.session.commit()
        flash('Änderungen wurden erfolgreich durchgeführt!')
        return redirect(url_for('home_admin'))
        
    if type(user) == Administrator and request.method == 'GET':
        form.mitarbeiterNr.data = user.mitarbeiterNr
        form.svnr.data = user.svnr
        form.vorname.data = user.vorname
        form.nachname.data = user.nachname
        form.email.data = user.email
        
    if type(user) == Administrator:
        return render_template('profile.html', form=form, form2=form2, typ=typ)
    else:
        return render_template('profile.html', typ=typ)


@app.route('/Wagen_erstellen')
@login_required
def waggon():
    if Administrator.query.filter_by(mitarbeiterNr=current_user.mitarbeiterNr).first() is None:
        flash('Sie müssen als Administrator angemeldet sein, um einen neuen Waggon erstellen zu können!')
        return redirect(url_for('home_personal'))
    return render_template('wagen.html', title='Wagen erstellen')


@app.route('/Wagen_erstellen/<typ>', methods=['GET', 'POST'])
@login_required
def createWaggon(typ):
    if Administrator.query.filter_by(mitarbeiterNr=current_user.mitarbeiterNr).first() is None:
        flash('Sie müssen als Administrator angemeldet sein, um einen neuen Waggon erstellen zu können!')
        return redirect(url_for('home_personal'))
    if typ == 'Triebwagen': # Für die unterschiedlichen Typen des Waggons werden unterschiedliche Formulare verwendet
        form = TriebwagenForm()
    else:
        form = PersonenwagenForm()
    if form.validate_on_submit():
        if typ == 'Triebwagen':
            wagen = Triebwagen(nr=form.nr.data, spurweite=form.spurweite.data, maxZugkraft=form.maxZugkraft.data)
        elif typ == 'Personenwagen':
            wagen = Personenwagen(nr=form.nr.data, spurweite=form.spurweite.data, sitzanzahl=form.sitzanzahl.data, maximalgewicht=form.maximalgewicht.data)
        db.session.add(wagen)
        db.session.commit()
        flash(typ + ' wurde erfolgreich erstellt!')
        return redirect(url_for('waggon'))
    return render_template('create_waggon.html', title=typ + ' erstellen', form=form, typ=typ)

@app.route('/Wagen_bearbeiten')
@login_required
def updateWaggon():
    if Administrator.query.filter_by(mitarbeiterNr=current_user.mitarbeiterNr).first() is None:
        flash('Sie müssen als Administrator angemeldet sein, um einen Waggon bearbeiten zu können!')
        return redirect(url_for('home_personal'))
    triebwagen = Triebwagen.query.all()
    personenwagen = Personenwagen.query.all()
    form = EmptyForm()
    return render_template('edit_wagen_overview.html', title='Wagen bearbeiten', triebwagen=triebwagen, personenwagen=personenwagen, form=form)

@app.route('/Wagen_bearbeiten/<nr>', methods=['GET', 'POST'])
@login_required
def editWaggon(nr):
    if Administrator.query.filter_by(mitarbeiterNr=current_user.mitarbeiterNr).first() is None: # Auch hier werden User, die nicht Administrator sind, in die Personal-Startseite weitergeleitet
        flash('Sie müssen als Administrator angemeldet sein, um einen bestehenden Waggon bearbeiten zu können!')
        return redirect(url_for('home_personal'))

    wagen = Wagen.query.filter_by(nr=nr).first()
    if wagen is None:    # Wird unter der übergebenen Wagennummer kein Waggon gefunden, so wird der Benutzer darüber informiert
        flash('Es wurde kein Waggon unter der Wagennummer {} gefunden!'.format(nr))
        return redirect(url_for('updateWaggon'))
    elif type(wagen) == Triebwagen:
        typ = 'Triebwagen'
        form = EditTriebwagenForm(wagen.nr)
    else:
        typ = 'Personenwagen'
        form = EditPersonenwagenForm(wagen.nr)

    if form.validate_on_submit():
        wagen.nr = form.nr.data
        wagen.spurweite = form.spurweite.data
        if type(wagen) == Triebwagen:
            wagen.maxZugkraft = form.maxZugkraft.data
        else:
            wagen.sitzanzahl = form.sitzanzahl.data
            wagen.maximalgewicht = form.maximalgewicht.data
        db.session.commit()
        flash('Änderungen wurden erfolgreich durchgeführt!')
        return redirect(url_for('updateWaggon'))

    elif request.method == 'GET':   # Ist die Abfragemethode 'GET', dann wird das Formular mit den Daten des jeweiligen Waggons angezeigt
        form.nr.data = wagen.nr
        form.spurweite.data = wagen.spurweite
        if type(wagen) == Triebwagen:
            form.maxZugkraft.data = wagen.maxZugkraft
        else:
            form.sitzanzahl.data = wagen.sitzanzahl
            form.maximalgewicht.data = wagen.maximalgewicht

    return render_template('edit_wagen.html', title='Wagen bearbeiten', form=form, typ=typ)

@app.route('/Wagen_löschen/<nr>', methods=['POST'])
@login_required
def deleteWaggon(nr):
    if Administrator.query.filter_by(mitarbeiterNr=current_user.mitarbeiterNr).first() is None:
        flash('Sie müssen als Administrator angemeldet sein, um einen Waggon löschen zu können!')
        return redirect(url_for('home_personal'))

    form = EmptyForm()
    if form.validate_on_submit():
        wagen = Wagen.query.filter_by(nr=nr).first()
        if wagen is None: # Wird kein Wagggon gefunden, so kann dieser auch nicht gelöscht werden. Diese Meldung wird dem User übergeben
            flash('Löschen eines nicht vorhandenen Waggons nicht möglich!')
            return redirect(url_for('updateWaggon'))

        db.session.delete(wagen)
        ''' Folgende Vorgehensweise wird durchgeführt: Es wird überprüft, ob dem jeweiligen Zug noch ein Personenwagen zugeordnet
            ist. Ist dies nicht der Fall, dann wird der gesamte Zug gelöscht (da ein Zug einen Personenwagen haben muss). Dieser 
            "Umweg" musste hier so realisiert werden, da durch das setzen eines Cascade-Constraints (cascade="all, delete") in der 
            Klasse "Personenwagen" in "models.py" bewirken würde, dass das Löschen eines Personenwagens den Zug löscht, auch wenn
            der Zug noch aus weiteren Personenwaggons bestehen würde. Also wird hier sichergestellt, dass der Zug nur dann gelöscht
            wird, wenn der letzte Personenwagen von diesem entfernt wird. '''
        if type(wagen) == Personenwagen:
            zug = Zug.query.filter_by(nr=wagen.zugNr).first()
            if zug is not None and zug.personenwagen.first() is None:
                db.session.delete(zug)
        db.session.commit()
        flash('Löschen des Waggons mit der Wagennummer {} wurde erfolgreich durchgeführt!'.format(nr))
        return redirect(url_for('updateWaggon'))
    else:
        return redirect(url_for('updateWaggon'))


@app.route('/Zug_erstellen', methods=['GET', 'POST'])
@login_required
def createTrain():
    if Administrator.query.filter_by(mitarbeiterNr=current_user.mitarbeiterNr).first() is None:
        flash('Sie müssen als Administrator angemeldet sein, um einen Zug erstellen zu können!')
        return redirect(url_for('home_personal'))

    triebwagen = Triebwagen.query.all()
    personenwagen = Personenwagen.query.all()
    form = ZugForm()
    form.triebwagen_nr.choices = [(t.nr, str(t.nr) + " (Spurweite: " + str(t.spurweite) + " mm)") for t in triebwagen]

    if form.validate_on_submit():
        ''' Für die Erläuterung der Vorgehensweise in dieser View Function, siehe nachfolgende View Function "addMaintenance",  
            da dessen Vorgehensweise ähnlich mit der von dieser View Function ist. '''
        personenwagenListe = request.form.getlist('personenwagenCheckbox')
        if personenwagenListe == []:
            flash('Fehler: Zu einem Zug muss mindestens ein Personenwagen zugeordnet werden!')
            return redirect(url_for('createTrain'))

        waggons = []
        for liste in personenwagenListe:
            wagen = Personenwagen.query.filter_by(nr=liste).first()
            ''' In folgender Abfrage wird überprüft, ob ein ausgewählter Personenwagen schon einem Zug zugeordnet ist.
                Ist dies der Fall wird der User durch "flash" darüber informiert und muss die Auswahl anpassen. '''
            if wagen.zug is not None:
                flash('Fehler: Der Personenwagen mit der Wagennummer {} ist bereits einem Zug zugeordnet!'.format(wagen.nr))
                return redirect(url_for('createTrain'))
            ''' Die ausgewählten Personenwaggons werden zur der Liste "waggons" hinzugefügt, welches dann der Variable 
                "personenwagen" von der Klasse Zug (also dem jeweiligen Zug) zugeteilt wird. '''
            waggons.append(wagen)

        '''Als nächstes wird die Spurweite des augewählten Triebwagen in die Variable "spurweite" eingespeichert '''
        spurweite = Triebwagen.query.filter_by(nr=form.triebwagen_nr.data).first().spurweite
        ''' Die Variable "spurweite" wird nun mit allen anderen Spurweiten verglichen (also mit den Spurweiten der
            ausgewählten Personenwaggons bzw. mit dem ausgewählten Personenwagen, da man auch nur ein Personenwagen
            auswählen kann). Hat ein Wagen nicht dieselbe Spurweite wie in der Variable "spurweite", dann wird der 
            User durch "flash" darüber informiert, wodurch dieser dann die Auswahl anpassen kann. '''
        for w in waggons:
            if spurweite != w.spurweite:
                flash('Die Spurweiten der ausgewählten Waggons stimmen nicht überein! Bitte wählen Sie Waggons mit einer einheitlichen Spurweite aus.')
                return redirect(url_for('createTrain'))

        zug = Zug(nr=form.nr.data, name=form.name.data, triebwagen_nr=form.triebwagen_nr.data, personenwagen=waggons)
        db.session.add(zug)
        db.session.commit()
        flash('Zug wurde erfolgreich erstellt!')
        return redirect(url_for('createTrain'))

    return render_template('create_zug.html', title='Zug erstellen', triebwagen=triebwagen, personenwagen=personenwagen, form=form)

@app.route('/Zug_bearbeiten')
@login_required
def updateTrain():
    if Administrator.query.filter_by(mitarbeiterNr=current_user.mitarbeiterNr).first() is None:
        flash('Sie müssen als Administrator angemeldet sein, um einen Zug bearbeiten zu können!')
        return redirect(url_for('home_personal'))
    zug = Zug.query.all()
    form = EmptyForm()
    return render_template('edit_zug_overview.html', title='Zug bearbeiten', zug=zug, form=form)

''' In dieser View Function werden nur Abweichungen von der View Function "createTrain" erklärt. Für weitere
    Erklärung, siehe View Function "createTrain". '''
@app.route('/Zug_bearbeiten/<nr>', methods=['GET', 'POST'])
@login_required
def editTrain(nr):
    if Administrator.query.filter_by(mitarbeiterNr=current_user.mitarbeiterNr).first() is None:
        flash('Sie müssen als Administrator angemeldet sein, um einen bestehenden Waggon bearbeiten zu können!')
        return redirect(url_for('home_personal'))

    zug = Zug.query.filter_by(nr=nr).first()
    if zug is None:
        flash('Es wurde kein Zug unter der Zugnummer {} gefunden!'.format(nr))
        return redirect(url_for('updateTrain'))

    personenwagen = Personenwagen.query.all()
    form = EditZugForm(zug.nr, zug.triebwagen_nr)
    form.triebwagen_nr.choices = [(t.nr, str(t.nr) + " (Spurweite: " + str(t.spurweite) + " mm)") for t in Triebwagen.query.all()]

    if form.validate_on_submit():
        personenwagenListe = request.form.getlist('personenwagenCheckbox')
        if personenwagenListe == []:
            flash('Fehler: Zu einem Zug muss mindestens ein Personenwagen zugeordnet werden!')
            return redirect(url_for('editTrain', nr=nr))

        waggons = []
        for liste in personenwagenListe:
            wagen = Personenwagen.query.filter_by(nr=liste).first()
            ''' Hier wird durch "wagen.zugNr != zug.nr" noch zusätzlich überprüft, ob der ausgewählte Personenwagen einem 
                einem anderen Zug als dem momentan zu bearbeitenden Zug zugeordnet ist. Würde dieser Ausdruck fehlen, dann 
                wäre der Schleifenausdruck auch dann True, wenn der Personenwagen dem zu bearbeitenden Zug zugeteilt wäre. '''
            if wagen.zug is not None and wagen.zugNr != zug.nr:
                flash('Fehler: Der Personenwagen mit der Wagennummer {} ist bereits einem Zug zugeordnet!'.format(wagen.nr))
                return redirect(url_for('editTrain', nr=nr))
            waggons.append(wagen)

        spurweite = Triebwagen.query.filter_by(nr=form.triebwagen_nr.data).first().spurweite
        for w in waggons:
            if spurweite != w.spurweite:
                flash('Die Spurweiten der ausgewählten Waggons stimmen nicht überein! Bitte wählen Sie Waggons mit einer einheitlichen Spurweite aus.')
                return redirect(url_for('editTrain', nr=nr))

        ''' Hier ist es wichtig, die nachfolgende Zuweisung der Zugnummer nach der ersten for-Schleife zu setzen, denn sonst wäre
            die if-Bedingung in der for-Schleife immer True. '''
        zug.nr = form.nr.data
        zug.name = form.name.data
        zug.triebwagen_nr = form.triebwagen_nr.data
        zug.personenwagen = waggons
        db.session.commit()
        flash('Änderungen wurden erfolgreich durchgeführt!')
        return redirect(url_for('updateTrain'))

    elif request.method == 'GET':
        form.nr.data = zug.nr
        form.name.data = zug.name
        form.triebwagen_nr.data = zug.triebwagen_nr

    return render_template('edit_zug.html', title='Zug bearbeiten', zug=zug, personenwagen=personenwagen, form=form)

@app.route('/Zug_löschen/<nr>', methods=['POST'])
@login_required
def deleteTrain(nr):
    if Administrator.query.filter_by(mitarbeiterNr=current_user.mitarbeiterNr).first() is None:
        flash('Sie müssen als Administrator angemeldet sein, um einen Zug löschen zu können!')
        return redirect(url_for('home_personal'))
    form = EmptyForm()

    if form.validate_on_submit():
        zug = Zug.query.filter_by(nr=nr).first()
        if zug is None: # Wird kein Zug gefunden, so kann dieser auch nicht gelöscht werden. Diese Meldung wird dem User übergeben
            flash('Löschen eines nicht vorhandenen Zuges nicht möglich')
            return redirect(url_for('updateTrain'))
        db.session.delete(zug)
        db.session.commit()
        flash('Löschen des Zuges mit der Zugnummer {} wurde erfolgreich durchgeführt'.format(nr))
        return redirect(url_for('updateTrain'))
    else:
        return redirect(url_for('updateTrain'))


@app.route('/Wartung_hinzufügen', methods=['GET', 'POST'])
@login_required
def addMaintenance():
    if Administrator.query.filter_by(mitarbeiterNr=current_user.mitarbeiterNr).first() is None:
        flash('Sie müssen als Administrator angemeldet sein, um eine Wartung hinzufügen zu können!')
        return redirect(url_for('home_personal'))

    wartungspersonal = Wartungspersonal.query.all()
    zug = Zug.query.all()
    form = WartungForm()
    #form.mitarbeiterNr.choices = [(w, w.vorname) for w in wartungspersonal]
    form.zugNr.choices = [(z.nr, z.nr) for z in zug]

    if form.validate_on_submit():
        ''' Folgende Vorgehensweise wurde hier angewendet: Da es keine Implementierung von Checkboxen in wtforms gefunden wurde hat man einen etwas
            "unsauberen" Weg benutzt. In der Variable "wartungspersonal", sind alle Mitarbeiter der Klasse Wartungspersonal eingespeichert. Diese
            werden an das HTML-Dokument "create_wartung.html" übergeben, welches diese Mitarbeiter in Checkboxen (<input type="checkbox"...) ausgibt.
            Die Werte der Checkboxen werden an die nachfolgende Variable "wartungspersonalListe" übergeben. Würde in diesem Ausdruck nur "get" stehen 
            statt "getlist", so wird dann nur die erste angekreuzte Checkbox in die Variable eingefügt. Durch "getlist" wird also sichergestellt, dass 
            eine Liste der angekreuzten Werte zurückkommt. Die Werte von diesen Checkboxen beinhalten die Mitarbeiternummer des jeweiligen Mitarbeiters.
            Nachfolgend werden diese Mitarbeiter durch die for-Schleife in die Assoziationstablle eingefügt (indem auf die Methode "wartungspersonal_hinzufügen"
            zugegriffen wird) bzw. werden diese Mitarbeiter der Variable "wartungspersonal" von der Klasse "Wartung" (welche durch ein backref Argument in der 
            Klasse Wartungspersonal definiert wurde) zugeteilt. Durch diese Vorgehensweise sind jedoch auch die Nachteile erstichtlich: Die Vorteile von wtforms
            entfallen, also muss separat ein Error ausgegeben werden, welches in der nachfolgenden Abfrage gemacht wird. Dort wird kontrolliert, ob die übergebene
            Liste Leer ist, also keine einzige Checkbox angekreuzt wurde. Dies wird dann dem User mitgeteilt. Ein weiterer Nachteil ist, dass diese Checkboxansicht
            zu unübersichtlich sein kann. Hat man bspw. viele (z.B. 100) Wartungspersonalmitarbeiter, dann wäre die Checkboxliste sehr lang, was zur 
            Unübersichtlichkeit führen würde'''
        wartungspersonalListe = request.form.getlist('WartungspersonalCheckbox')
        if wartungspersonalListe == []:
            flash('Fehler: Zu einer Wartung muss mindestens ein Wartungspersonal eingeteilt werden!')
            return redirect(url_for('addMaintenance'))
        wartung = Wartung(wartungsNr=form.wartungsNr.data, von=form.von.data, bis=form.bis.data, zugNr=form.zugNr.data)
        db.session.add(wartung)


        for liste in wartungspersonalListe:
            wartung.wartungspersonal_hinzufuegen(Wartungspersonal.query.filter_by(mitarbeiterNr=liste).first())

        db.session.commit()
        flash('Die Wartung mit der Wartungsnummer {} wurde erfolgreich erstellt!'.format(wartung.wartungsNr))
        return redirect(url_for('home_admin'))
    return render_template('create_wartung.html', title='Wartung hinzufügen', wartungspersonal=wartungspersonal, zug=zug, form=form)

@app.route('/Wartung_bearbeiten')
@login_required
def updateMaintenance():
    if Administrator.query.filter_by(mitarbeiterNr=current_user.mitarbeiterNr).first() is None:
        flash('Sie müssen als Administrator angemeldet sein, um eine Wartung bearbeiten zu können!')
        return redirect(url_for('home_personal'))
    wartung = Wartung.query.all()
    form = EmptyForm()
    return render_template('edit_wartung_overview.html', title='Wartung bearbeiten', wartung=wartung, form=form)


''' In dieser View Function werden nur Änderungen dokumentiert. Für weitere Dokumentation des Codes in dieser View
    Function, siehe "addMaintenance()". '''
@app.route('/Wartung_bearbeiten/<wartungsNr>', methods=['GET', 'POST'])
@login_required
def editMaintenance(wartungsNr):
    if Administrator.query.filter_by(mitarbeiterNr=current_user.mitarbeiterNr).first() is None:
        flash('Sie müssen als Administrator angemeldet sein, um eine bestehenden Wartung bearbeiten zu können!')
        return redirect(url_for('home_personal'))
    wartung = Wartung.query.filter_by(wartungsNr=wartungsNr).first()
    if wartung is None:
        flash('Es wurde keine Wartung unter der Wartungsnummer {} gefunden!'.format(wartungsNr))
        return redirect(url_for('updateMaintenance'))

    wartungspersonal = Wartungspersonal.query.all()
    form = EditWartungForm(wartung.wartungsNr)
    form.zugNr.choices = [(z.nr, z.nr) for z in Zug.query.all()]

    if form.validate_on_submit():
        wartungspersonalListe = request.form.getlist('WartungspersonalCheckbox')
        if wartungspersonalListe == []:
            flash('Fehler: Zu einer Wartung muss mindestens ein Wartungspersonal eingeteilt werden!')
            return redirect(url_for('editMaintenance', wartungsNr=wartungsNr))
        wartung.wartungsNr = form.wartungsNr.data
        wartung.von = form.von.data
        wartung.bis = form.bis.data
        ''' Als nächstes wird von der zu ändernden Wartung auf die ursprünglich zugeteilten Wartungspersonalmitarbeiter (durch
            Aufruf der Methode "zugeordnetes_wartungspersonal") zugegriffen. Diese Wartungspersonalmitarbeiter werden in der 
            Variable "personal" eingespeichert. '''
        personal = wartung.zugeordnetes_wartungspersonal().all()

        ''' Folgende Vorgehensweise wird in der nachfolgenden Schleife durchgeführt: Da die Variable "personal" eine Liste der
            Wartungspersonalmitarbeiter ist, wird durch den Ausdruck "for p in personal" über die Liste iteriert, um somit auf
            die einzelnen Mitarbeiter zuzugreifen. Zu aller erst wird eine Variable "cnt" definiert. Danach wird über die aktualisierte
            Liste der Wartungspersonalmitarbeiter iteriert (die aktualisierte Liste der Wartungspersonalmitarbeiter ist in der 
            Variable "wartungspersonalListe" eingespeichert. Hierbei kann es sein dass neue Mitarbeiter hinzugefügt worden sind
            oder auch Mitarbeiter, die der Wartung zugeteilt waren, entfernt worden sind). In dieser (inneren) Schleife wird überprüft,
            ob der Mitarbeiter der ursprünglichen Liste der Wartungspersonalmitarbeiter ("personal") in der aktualisierten Liste 
            ("wartungspersonalListe") vorhanden ist. Ist dies der Fall, dann wird die Variable "cnt" erhöht. Ist man nun fertig mit
            der inneren Schleife, so wird die "cnt" Variable überprüft. Ist diese größer als 0 (es wäre auch richtig, wenn man
            überprüfen würde, ob die "cnt" Variable genau den Wert 1 hat, da ein Mitarbeiter nur einmal in der Liste vorhanden sein
            kann und "cnt" somit höchstens den Wert 1 haben kann), so wird durch continue auf die nächste Schleifeniteration gesprungen
            und der Code darunter ignoriert. Hat jedoch "cnt" den Wert 0 (und es wurde auch somit der Wartungspersonalmitarbeiter von 
            der ursprünglichen Liste nicht in der aktualisierten Liste gefunden), dann wird dieser Mitarbeiter von der Assoziationstabelle 
            durch die Methode "wartungspersonal_entfernen" entfernt. Zusammengefasst dienen diese beiden Schleifen also zum entfernen
            von Wartungspersonalmitarbeitern aus der jeweiligen Wartung, die im nachhinein beim Bearbeiten der Wartung durch die 
            Checkbox wieder entfernt wurden (also das Hackerl entfernt wurde)'''
        for p in personal:
            cnt = 0
            for liste in wartungspersonalListe:
                if p.mitarbeiterNr == liste:
                    cnt += 1
            if cnt > 0:
                continue
            wartung.wartungspersonal_entfernen(p)

        ''' In der folgenden Schleife werden die Wartungspersonalmitarbeiter (von der aktualisierten Liste "wartungspersonalListe")
            in die Assoziationstabelle anhand der Methode "wartungspersonal_hinzufuegen" eingefügt. Diese Methode stellt sicher, dass
            Mitarbeiter, dies sich schon in der Assoziationstabelle befinden, nicht noch einmal eingefügt werden. '''
        for liste in wartungspersonalListe:
            wartung.wartungspersonal_hinzufuegen(Wartungspersonal.query.filter_by(mitarbeiterNr=liste).first())

        wartung.zugNr = form.zugNr.data
        db.session.commit()
        flash('Änderungen wurden erfolgreich durchgeführt!')
        return redirect(url_for('updateMaintenance'))

    elif request.method == 'GET':
        form.wartungsNr.data = wartung.wartungsNr
        form.von.data = wartung.von
        form.bis.data = wartung.bis
        form.zugNr.data = wartung.zugNr

    return render_template('edit_wartung.html', title='Wartung bearbeiten', wartung=wartung, wartungspersonal=wartungspersonal, form=form)

@app.route('/Wartung_löschen/<wartungsNr>', methods=['POST'])
@login_required
def deleteMaintenance(wartungsNr):
    if Administrator.query.filter_by(mitarbeiterNr=current_user.mitarbeiterNr).first() is None:
        flash('Sie müssen als Administrator angemeldet sein, um eine Wartung löschen zu können!')
        return redirect(url_for('home_personal'))
    form = EmptyForm()
    if form.validate_on_submit():
        wartung = Wartung.query.filter_by(wartungsNr=wartungsNr).first()
        if wartung is None: # Wird keine Wartung gefunden, so kann diese auch nicht gelöscht werden. Diese Meldung wird dem User übergeben
            flash('Löschen einer nicht vorhandenen Wartung nicht möglich')
            return redirect(url_for('updateMaintenance'))
        db.session.delete(wartung)
        db.session.commit()
        flash('Löschen der Wartung mit der Wartungsnummer {} wurde erfolgreich durchgeführt'.format(wartungsNr))
        return redirect(url_for('updateMaintenance'))
    else:
        return redirect(url_for('updateMaintenance'))


@app.route('/Zugübersicht')
@login_required
def trainOverview():
    zug = Zug.query.order_by('name').all()
    return render_template('zug_overview.html', title='Zugübersicht', zug=zug)

@app.route('/Waggonübersicht')
@login_required
def waggonOverview():
    triebwagen = Triebwagen.query.all()
    personenwagen = Personenwagen.query.all()
    return render_template('wagen_overview.html', title='Waggonübersicht', triebwagen=triebwagen, personenwagen=personenwagen)

@app.route('/Wartungsübersicht')
@login_required
def wartungOverview():
    wartung = Wartung.query.all()
    return render_template('wartung_overview.html', title='Wartungsübersicht', wartung=wartung)