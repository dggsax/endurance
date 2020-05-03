from flask import Blueprint, flash, render_template, url_for, redirect, request
from flask_login import login_required, login_user, current_user, logout_user

from web.utils import admin_required
from web.controllers.forms import *
from web.models import Member, Major, Minor
from web.dropbox import dropbox_setup_member, cancel_request
from web.mail import send_email, send_registration_confirmation, resend_magic_link
from web import csrf, db, login_manager, app

import time

main = Blueprint("main", __name__)


@main.route("/", methods=["GET"])
def index():
    return render_template("home.html")


@main.route("/profile", methods=["GET", "POST"])
@login_required
def profile_view():

    form = MemberForm(obj=current_user)
    form.affiliation.data = current_user.affiliation.value

    form.email.description = "We do not allow you to change your email once you've created your account. If you really wish to change the email, please email endurance-help@mit.edu"

    try:
        if form.validate_on_submit():

            filtered = {
                k: v
                for k, v in form.data.items()
                if v != ""
                and str(v) != "None"
                and k != "submit"
                and k != "csrf_token"
                and k != "affiliation"
                and current_user.__dict__[k] != v
            }

            filtered = {}
            invalid_items = ["submit", "csrf_token", "affiliation"]
            for k, v in form.data.items():
                if k in invalid_items:
                    continue

                # existing value
                e_v = current_user.__dict__[k]

                if type(e_v) is bool:
                    if bool(v) != e_v: filtered[k] = v
                elif type(e_v) is int:
                    if int(v) != e_v: filtered[k] = v
                elif type(e_v) is str:
                    if v != e_v: filtered[k] = v
                else:
                    # If we are here, then we're working with the arrays of majors/minors
                    # which we currently are not allowing users to change
                    continue
                
            for key, value in filtered.items():
                setattr(current_user, key, value)

            db.session.commit()

            flash(
                message='User "{}" successfully updated'.format(current_user.full_name()),
                category='info',
            )

    except Exception as e:
        raise e

    return render_template("profile.html", form=form)


@main.route("/to-the-class-of-2020", methods=["GET"])
def letter_2020():
    return render_template("2020.html")


@main.route("/to-the-class-of-1970", methods=["GET"])
def letter_1970():
    return render_template("1970.html")


@main.route("/to-everyone-else", methods=["GET"])
def everyone_else():
    return render_template("everyone_else.html")


@main.route("/admin", methods=["GET", "POST"])
@login_required
@admin_required()
def admin():
    test_email_form = SendTestEmailForm()

    if test_email_form.validate_on_submit():
        print("Sending email now!")
        recipient = test_email_form.email.data
        print(recipient)
        send_email(
            recipient=recipient,
            subject="[ENDURANCE] TEST EMAIL",
            template="mail/test_email",
        )

    return render_template("admin.html", test_email_form=test_email_form)


@main.route("/login", methods=["GET", "POST"])
def login():

    if current_user.is_authenticated:
        flash(message=f"Hi {current_user.first_name}, you are already signed in, so we sent you to the profile page.", category="info")
        return redirect("/profile")

    email = request.args.get("email")
    token = request.args.get("token")

    # check if email and token provided in request
    if email and token:
        member = Member.query.filter_by(email=email).first()

        if member is None:
            flash(
                message=f'No member with email "{email}". Make sure you are using the correct magic link that was emailed to you, or that `email=` in the URL shows the email you used to sign up to submit content.',
                category="error",
            )
            flash(
                message=f"If you lost your magic link or are having issues, with you can request a new link be sent to you.",
                category="info",
            )
        elif member.verify_magic_link_token(token):
            print("Verified")
            login_user(member, remember=True)

            next = request.args.get("next")

            # is_safe_url should check if the url is safe for redirects.
            # See http://flask.pocoo.org/snippets/62/ for an example.
            # if not is_safe_url(next):
            #     return flask.abort(400)

            return redirect(next or url_for("main.profile_view"))
        else:
            flash(
                message='Unable to log in with link. If you think is a mistake, please select "Request new magic link" and one will be emailed to you',
                category="error",
            )
    else:
        flash(message="If you are trying to log in, make sure you're clicking the magic link that was generated for you and emailed to you.")
    # set up magic link sending form
    form = ResendMagicLink()

    if form.validate_on_submit():
        recipient_member = Member.query.filter(func.lower(Member.email) == func.lower(form.email.data)).first()

        # this will generate a new magic token for the member, create the link, send an email to them, and then flash a message to the interface
        resend_magic_link(recipient_member)

    return render_template("login.html", form=form)


@main.route("/resend-confirmation")
@login_required
def resend_confirmation():
    try:
        send_registration_confirmation(member=current_user)
        return current_user.magic_link()
        # return str(request.host)
    except:
        return "Not sent"


@main.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Logged out!")
    return redirect(url_for("main.index"))


@main.route("/sign-up", methods=["GET", "POST"])
def sign_up_view():
    if current_user.is_authenticated:
        flash(message=f"Hi {current_user.first_name}, you are already signed in, so we sent you to the profile page. If you are trying to sign up on behalf of someone else, please log out.", category="info")
        return redirect("/profile")

    form = MemberForm()

    csrf.protect()

    if form.validate_on_submit():
        email = form.data["email"]

        existing_member = Member.query.filter_by(email=email).first()

        if existing_member is not None:
            form.email.errors.append(
                f"A contributor with email {email} is already registered in our system. If you believe this to be an error, please let us know."
            )
        else:
            try:
                member_data = form.data
                member_data["affiliation"] = AffiliationEnum(member_data["affiliation"])

                del member_data["csrf_token"]
                del member_data["major"]
                del member_data["minor"]

                member = Member(**member_data)

                # process major(s)
                for major in form.data["major"]:
                    major_object = Major.query.filter_by(name=major).first()
                    member.major.append(major_object)

                # process minor(s)
                for minor in form.data["minor"]:
                    minor_object = Minor.query.filter_by(name=minor).first()
                    member.minor.append(minor_object)

                dropbox_setup_member(member)

                db.session.add(member)
                db.session.commit()

                member.generate_magic_link_token()

                send_registration_confirmation(member=member)

                login_user(member)

                return redirect(url_for("main.profile_view"))
            except Exception as e:
                app.logger.error(type(e), str(e))

                # TODO make this more robust...
                # Cancel the created FIle Request with Dropbox and commit the changes
                # to the database session
                cancel_request(member, commit=False)
                app.logger.debug(f"Dropbox requests created for {member.email} deleted")
                app.logger.debug(
                    f"User {member.email} deleted due to errors with creation"
                )

    return render_template("signup.html", form=form)
