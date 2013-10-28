"""
Views: from the URL to the rendered template
"""
from flask import Blueprint, render_template, url_for, redirect, request
from flask.ext.login import login_user, logout_user, login_required, current_user

import forms
import models
import login


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
            return redirect(url_for('.profil'))

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


@bp.route('/profil')
@login_required
def profil():
    return render_template('profil.html', user=current_user.user)
