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
    """profil view

    Common variables are set once for all. Some fields can be disabled
    depending on the user state. See `forms.Profil`.
    """
    user = current_user.user
    volontaire = user.volontaire

    def update_profile_form(form):
        """Remove fields and update others"""
        if not volontaire:
            del form.disponibilites
        form.sweat.choices = [(s, s) for s in user.available_sweats()]

    if request.method == 'POST':
        form = forms.Profil(request.form)
        update_profile_form(form)
        if form.validate():
            # check for sweat shirt
            # setting the choices should prevent this from failing
            if not user.try_get_sweat(form.sweat.data):
                flash(u'Cette taille n\'est plus disponible')

            # if volontaire then other fields must be updated
            if volontaire:
                volontaire.user.sexe = form.sexe.data

                # careful with many-to-many disponibiles relationship
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
        data = {}
        # prepare data bount to fields
        if user.sweat is not None:
            data['sweat'] = user.sweat
        if volontaire:
            data['disponibilites'] = [d.quand for d in volontaire.disponibilites]

        form = forms.Profil(**data)
        update_profile_form(form)

    return render_template('profil.html',
                           form=form,
                           user=user)
