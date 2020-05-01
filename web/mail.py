import os

from flask import render_template, current_app, flash
from flask_login import current_user
from flask_mail import Message
from web import app, mail


def send_registration_confirmation(member):
    recipient = member.email
    subject = "Registration Confirmation"
    template = "mail/registration_confirmation"

    # copy `current_user` object since redis doesn't become happy when we provide
    #   it with flask_login objects
    member_copy = member.__dict__
    member_copy["full_name_for_path"] = member.full_name_for_path()
    member_copy["full_name"] = member.full_name()
    member_copy["magic_link"] = member.magic_link()
    member_copy["dropbox_file_upload_url"] = member.dropbox_file_upload_url
    member_copy["dropbox_shared_folder_url"] = member.dropbox_shared_folder_url

    send_email(
        recipient=recipient, subject=subject, template=template, member=member_copy
    )

    flash(message="Confirmation Email Sent!", category="info")

    return


def resend_magic_link(member):
    # generate new magic link token
    member.generate_magic_link_token(reset=True)

    # generate email variables
    recipient = member.email
    subject = "MIT Endurance Magic Link"
    template = "mail/resend_magic_link"
    name = member.first_name
    magic_link = member.magic_link()

    send_email(
        recipient=recipient,
        subject=subject,
        template=template,
        name=name,
        magic_link=magic_link
    )

    flash(
        message=f"Magic link sent to {recipient}, it may take a few minutes to recieve the email. Any previous magic links you had will no longer work. If you don't get an email, reach out to endurance-help@mit.edu and we'll help get you straightened out.",
        category="info"
    )

    return


def send_email(recipient, subject, template, **kwargs):
    with app.app_context():
        msg = Message(
            subject,
            sender=("MIT Endurance Project", "endurance@mit.edu"),
            recipients=[recipient],
        )
        # msg.body = render_template(template + '.txt', **kwargs)
        msg.html = render_template(template + ".html", **kwargs)
        result = mail.send(msg)
        print("RESULT\n\n\n\n")
        print(result)
