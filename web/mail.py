import os

from flask import render_template, current_app, flash
from flask_login import current_user
from flask_mail import Message
from web import app, mail, q

def send_registration_confirmation(member):
    recipient=member.email
    subject="Registration Confirmation"
    template="mail/registration_confirmation"

    # copy `current_user` object since redis doesn't become happy when we provide 
    #   it with flask_login objects
    member_copy = member.__dict__
    member_copy["full_name_for_path"] = member.full_name_for_path()
    member_copy["full_name"] = member.full_name()
    member_copy["magic_link"] = member.magic_link()
    member_copy["dropbox_file_upload_url"] = member.dropbox_file_upload_url
    member_copy["dropbox_shared_folder_url"] = member.dropbox_shared_folder_url

    job = q.enqueue(
        send_email,
        recipient=recipient,
        subject=subject,
        template=template,
        member=member_copy
    )

    app.logger.debug(f"Job with ID {job.id} created to send confirmation email to {member.email} added to queue at {job.enqueued_at}")

    flash("Confirmation Email Sent!")

    return


def send_email(recipient, subject, template, **kwargs):
    with app.app_context():
        msg = Message(
            subject,
            sender=("MIT Endurance Project", "mitendurance@gmail.com"),
            recipients=[recipient])
        # msg.body = render_template(template + '.txt', **kwargs)
        msg.html = render_template(template + '.html', **kwargs)
        result = mail.send(msg)
        print("RESULT\n\n\n\n")
        print(result)
