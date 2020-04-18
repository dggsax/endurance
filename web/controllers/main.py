from flask import Blueprint, flash, render_template, url_for, redirect
from web.controllers.forms import *

main = Blueprint('main', __name__)

@main.route('/', methods=['GET'])
def default_view():
    return render_template('home.html')

@main.route('/profile', methods=['GET'])
def profile_view():
    return render_template('profile.html')

@main.route('/sign-up', methods=['GET', 'POST'])
def sign_up_view():
    form = MemberForm()

    if form.validate_on_submit():
        print(form.first_name)

    print(form.first_name.__dict__)
    print(form.initials.__dict__)

    return render_template('signup.html', form=form)