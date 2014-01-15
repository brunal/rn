# -*- encoding: utf-8 -*-
"""
Basic views: profile, register, login and logout from the URL to the rendered template
"""
from flask import Blueprint, render_template, url_for, redirect, request, flash
from flask.ext.login import login_user, logout_user, login_required, current_user

import forms
import models
import login


login.login_manager.login_view = 'views.basic.login_page'


bp = Blueprint(__name__, __name__, url_prefix='/')


@bp.route('')
def index():
    return render_template('index.html')


@bp.route('login', methods=['GET', 'POST'])
def login_page():
    form = forms.Login(request.form)
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        user = login.authentify(email, password)
        if user:
            login_user(user)
            return redirect(request.args.get('next') or url_for('.index'))

        flash('Email ou mot de passe invalide')
        return render_template('login.html', form=form)

    return render_template('login.html', form=form)


@bp.route('logout')
def logout():
    logout_user()
    return redirect(url_for('.login_page'))


@bp.route('profil', methods=['GET', 'POST'])
@login_required
def profil():
    if login.get_current_user_role() is not models.Volontaire:
        # on affiche juste les informations
        return render_template('profil.html', user=current_user.user)

    # Du travail supplémentaire est requis au niveau des disponibilites pour
    # les faire marcher en many-to-many correctement (dommage)
    volontaire = current_user.user.role
    if request.method == 'POST':
        form = forms.Profil(request.form)
        if form.validate():
            # update user object
            volontaire.sweat = form.sweat.data
            volontaire.user.sexe = form.sexe.data

            map(models.db.session.delete, volontaire.disponibilites)
            dispos = []
            for i in form.disponibilites.data:
                dispo = models.Disponibilites(volontaire=volontaire, quand=i)
                models.db.session.add(dispo)
                dispos.append(dispo)
            volontaire.disponibilites = dispos

            models.db.session.commit()

            flash(u'Infos bien mises à jour !')
    else:
        dispos_int = [d.quand for d in volontaire.disponibilites]
        form = forms.Profil(sweat=volontaire.sweat, disponibilites=dispos_int)

    return render_template('profil.html',
                           form=form,
                           user=current_user.user)
