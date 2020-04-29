from flask import Blueprint, flash, render_template, url_for, redirect, request
from flask_login import login_required, login_user, current_user, logout_user
from web.controllers.forms import *
from web.models import Member, Major, Minor
from web.dropbox import dropbox_setup_member, cancel_request
from web.mail import send_email, send_registration_confirmation
from web import csrf, db, login_manager, q, app

import time

main = Blueprint("main", __name__)


@main.route("/", methods=["GET"])
def index():
    return render_template("home.html")

# @main.route("/profile/setup-dropbox", methods=["POST"])
# @login_required
# def setup_dropbox():
#     job = q.enqueue(dropbox_setup_member, member=current_user)

#     message = f"Task with id {job.id} to set up {current_user.email} with Dropbox at {job.enqueued_at}"

#     flash(message)

#     return message


@main.route("/profile", methods=["GET"])
@login_required
def profile_view():

    return render_template("profile.html")


@main.route("/admin", methods=["GET", "POST"])
def admin():
    test_email_form = SendTestEmailForm()

    if test_email_form.validate_on_submit():
        print("Sending email now!")
        recipient = test_email_form.email.data
        print(recipient)
        send_email(recipient=recipient, subject="[ENDURANCE] TEST EMAIL", template="mail/test_email")

        


    return render_template("admin.html", test_email_form=test_email_form)

@main.route("/login", methods=["GET"])
def login():
    email = request.args.get("email")
    token = request.args.get("token")

    if not email:
        return "Invalid link, must provide email in parameters"
    if not token:
        # TODO show login error page
        return "Must provide token"

    member = Member.query.filter_by(email=email).first()
    # member.generate_magic_link_token(reset=True)
    if member is None:
        return f"No member with email {email}. Make sure you are using the correct magic link that was emailed to you, or that `email=` in the URL shows the email you used to sign up to submit content."
    elif member.verify_magic_link_token(token):
        print("Verified")
        login_user(member, remember=True)

        next = request.args.get("next")
        # is_safe_url should check if the url is safe for redirects.
        # See http://flask.pocoo.org/snippets/62/ for an example.
        # if not is_safe_url(next):
        #     return flask.abort(400)

        return redirect(next or url_for("main.profile_view"))

    return "Unable to login"

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
    form = MemberForm()

    csrf.protect()

    if form.validate_on_submit():
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
            app.logger.debug(f"User {member.email} deleted due to errors with creation")
            db.session.delete(member)
            db.session.commit()

    return render_template("signup.html", form=form)
