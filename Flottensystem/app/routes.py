from datetime import datetime
from flask import render_template, flash, redirect, url_for, request
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.urls import url_parse
from app import app, db
from app.forms import LoginForm, RegistrationForm, RegistrationFormZugpersonal, EmptyForm, EditProfileForm, EditProfileFormZugpersonal
from app.models import Mitarbeiter, Wartungspersonal, Zugpersonal, Administrator


@app.route('/')
@app.route('/Startseite')
def home():
    if current_user.is_authenticated:
        if Administrator.query.filter_by(mitarbeiterNr=current_user.mitarbeiterNr).first() is not None:
            next_page = url_for('home_admin')
        else:
            next_page = url_for('home_personal')
        return redirect(next_page)
    return render_template('home.html', title='Startseite - Flotteninformationssystem')


@app.route('/Startseite/Admin')
@login_required
def home_admin():
    if Administrator.query.filter_by(mitarbeiterNr=current_user.mitarbeiterNr).first() is None:
        flash('Sie müssen als Administrator angemeldet sein, um in die Administrator-Startseite zu gelangen!')
        return redirect(url_for('home_personal'))
    return render_template('home_administrator.html', title='Startseite - Flotteninformationssystem')


@app.route('/Startseite/Personal')
@login_required
def home_personal():
    if Administrator.query.filter_by(mitarbeiterNr=current_user.mitarbeiterNr).first() is not None:
        flash('Sie sind als Administrator angemeldet!')
        return redirect(url_for('home_admin'))
    return render_template('home_personal.html', title='Startseite - Flotteninformationssystem')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        if Administrator.query.filter(mitarbeiterNr=current_user.mitarbeiterNr).first() is not None:
            return redirect(url_for('home_admin'))
        else:
            return redirect(url_for('home_personal'))
    form = LoginForm()
    if form.validate_on_submit():
        user = Mitarbeiter.query.filter_by(email=form.email.data).first()
        if user is None or not user.check_password(form.passwort.data):
            flash('Email bzw. Passwort ungültig!')
            return redirect(url_for('login'))
        login_user(user, remember=form.angemeldet_bleiben.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            if Administrator.query.filter_by(mitarbeiterNr=user.mitarbeiterNr).first() is not None:
                next_page = url_for('home_admin')
            else:
                next_page = url_for('home_personal')
        return redirect(next_page)
    return render_template('login.html', title='Anmelden', form=form)

    
@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route('/register')
@login_required
def register():
    if Administrator.query.filter_by(mitarbeiterNr=current_user.mitarbeiterNr).first() is None:
        flash('Sie müssen als Administrator angemeldet sein, um einen neuen Benutzer erstellen zu können!')
        return redirect(url_for('home_personal'))
    return render_template('register.html', title='Benutzer erstellen')


@app.route('/registerUser/<name>', methods=['GET', 'POST'])
@login_required
def registerUser(name):
    if Administrator.query.filter_by(mitarbeiterNr=current_user.mitarbeiterNr).first() is None:
        flash('Sie müssen als Administrator angemeldet sein, um einen neuen Benutzer erstellen zu können!')
        return redirect(url_for('home_personal'))
    if name == 'Zugpersonal':
        form = RegistrationFormZugpersonal()
    else:
    	form = RegistrationForm()
    if form.validate_on_submit():
        if name == 'Administrator':
            user = Administrator(mitarbeiterNr=form.mitarbeiterNr.data, svnr=form.svnr.data, vorname=form.vorname.data, nachname=form.nachname.data, email=form.email.data)
        elif name == 'Wartungspersonal':
            user = Wartungspersonal(mitarbeiterNr=form.mitarbeiterNr.data, svnr=form.svnr.data, vorname=form.vorname.data, nachname=form.nachname.data, email=form.email.data)
        if name == 'Zugpersonal':
            user = Zugpersonal(mitarbeiterNr=form.mitarbeiterNr.data, svnr=form.svnr.data, vorname=form.vorname.data, nachname=form.nachname.data, email=form.email.data, berufsbezeichnung=form.berufsbezeichnung.data)
        user.set_password(form.passwort.data)
        db.session.add(user)
        db.session.commit()
        flash('Benutzer wurde erfolgreich erstellt!')
        return redirect(url_for('register'))
    return render_template('register_user.html', title=name + ' erstellen', form=form, typ=name)


@app.route('/User_bearbeiten')
@login_required
def updateUser():
    if Administrator.query.filter_by(mitarbeiterNr=current_user.mitarbeiterNr).first() is None:
        flash('Sie müssen als Administrator angemeldet sein, um einen Benutzer bearbeiten zu können!')
        return redirect(url_for('home_personal'))
    wartungspersonal = Wartungspersonal.query.all()
    zugpersonal = Zugpersonal.query.all()
    form = EmptyForm()
    return render_template('user.html', wartungspersonal=wartungspersonal, zugpersonal=zugpersonal, form=form)
    
    
@app.route('/User_bearbeiten/<mitarbeiterNr>', methods=['GET', 'POST'])
@login_required
def editUser(mitarbeiterNr):
    if Administrator.query.filter_by(mitarbeiterNr=current_user.mitarbeiterNr).first() is None:
        flash('Sie müssen als Administrator angemeldet sein, um einen Benutzer bearbeiten zu können!')
        return redirect(url_for('home_personal'))
    user = Mitarbeiter.query.filter_by(mitarbeiterNr=mitarbeiterNr).first()
    if user is None:
        flash('Es wurde kein Mitarbeiter unter der Mitarbeiternummer {} gefunden!'.format(mitarbeiterNr))
        return redirect(url_for('updateUser'))
    elif type(user) == Administrator and user.mitarbeiterNr != current_user.mitarbeiterNr:
        flash('Sie dürfen die Daten eines anderen Administrators nicht bearbeiten!')
        return redirect(url_for('updateUser'))
    elif type(user) == Zugpersonal:
        typ = 'Zugpersonal'
        form = EditProfileFormZugpersonal(user.mitarbeiterNr, user.svnr, user.email)
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
        db.session.commit()
        flash('Änderungen wurden erfolgreich durchgeführt!')
        return redirect(url_for('updateUser'))
    elif request.method == 'GET':
        form.mitarbeiterNr.data = user.mitarbeiterNr
        form.svnr.data = user.svnr
        form.vorname.data = user.vorname
        form.nachname.data = user.nachname
        form.email.data = user.email
        if typ == 'Zugpersonal':
            form.berufsbezeichnung.data = user.berufsbezeichnung
    return render_template('edit_user.html', form=form, typ=typ)

@app.route('/User_löschen/<mitarbeiterNr>', methods=['POST'])
@login_required
def deleteUser(mitarbeiterNr):
    if Administrator.query.filter_by(mitarbeiterNr=current_user.mitarbeiterNr).first() is None:
        flash('Sie müssen als Administrator angemeldet sein, um einen Benutzer löschen zu können!')
        return redirect(url_for('home_personal'))
    form=EmptyForm()
    if form.validate_on_submit():
        mitarbeiter = Mitarbeiter.query.filter_by(mitarbeiterNr=mitarbeiterNr).first()
        if mitarbeiter is None:
            flash('Löschen eines nicht vorhandenen Mitarbeiters nicht möglich')
            return redirect(url_for('updateUser'))
        db.session.delete(mitarbeiter)
        db.session.commit()
        if Administrator.query.filter_by(mitarbeiterNr=current_user.mitarbeiterNr).first() is not None: # Es wird hier kontrolliert ob der Administrator sich selbst gelöscht hat
            flash('Löschen des Mitarbeiters {} {} mit der Mitarbeiternummer {} wurde erfolgreich durchgeführt'.format(mitarbeiter.vorname, mitarbeiter.nachname, mitarbeiterNr))
            return redirect(url_for('updateUser'))
        else:
            flash('Sie haben Ihr Profil erfolgreich gelöscht!')
            return redirect(url_for('login'))
    else:
        return redirect(url_for('updateUser'))


@app.route('/Profil', methods=['GET', 'POST'])
@login_required
def profile():
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
