# -*- encoding: utf-8 -*-
"""
Views: from the URL to the rendered template
"""
from flask import Blueprint, render_template, url_for, redirect, request
from flask.ext.login import login_user, logout_user, login_required, current_user

import forms
import models
import login


login.login_manager.login_view = '.login_page'


bp = Blueprint(__name__, __name__)


@bp.route('/login', methods=['GET', 'POST'])
def login_page():
    form = forms.Login(request.form)
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        user = login.authentify(email, password)
        if user:
            login_user(user)
            return redirect(request.args.get('next') or url_for('.profil'))

        return render_template('login.html', form=form, message='Email ou mot de passe invalide')

    return render_template('login.html', form=form)


@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('.login_page'))


@bp.route('/register', methods=['GET', 'POST'])
def register():
    form = forms.Registration(request.form)
    if form.validate_on_submit():
        password = login.hash_password(form.password.data)
        user = models.User(form.email.data,
                password,
                form.name.data,
                form.sexe.data,
                form.ecole.data,
                form.portable.data)

        volontaire = models.Volontaire(user)
        models.db.session.add(volontaire)
        models.db.session.commit()

        user_for_login = login.User(user)
        login_user(user_for_login)

        # TODO: send email

        return redirect(url_for('.profil'))

    return render_template('register.html', form=form)


@bp.route('/profil', methods=['GET', 'POST'])
@login_required
def profil():
    # Du travail supplémentaire est requis au niveau des disponibilites pour
    # les faire marcher en many-to-many correctement (dommage)
    volontaire = current_user.user.role
    if request.method == 'POST':
        form = forms.Profil(request.form)
        if form.validate():
            # update user object
            volontaire.sweat = form.sweat.data

            map(models.db.session.delete, volontaire.disponibilites)
            dispos = []
            for i in form.disponibilites.data:
                dispo = models.Disponibilites(volontaire=volontaire, quand=i)
                models.db.session.add(dispo)
                dispos.append(dispo)
            volontaire.disponibilites = dispos

            models.db.session.commit()
    else:
        dispos_int = [d.quand for d in volontaire.disponibilites]
        form = forms.Profil(sweat=volontaire.sweat, disponibilites=dispos_int)

    return render_template('profil.html', form=form, user=current_user.user)
