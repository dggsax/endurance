from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SelectField, BooleanField, SelectMultipleField, TextAreaField
from wtforms.validators import Length, DataRequired, Regexp, Email, Optional

from web.models.enums import AffiliationEnum
from web.models import Major, Minor


class MemberForm(FlaskForm):
    email = StringField(
        label="Email",
        validators=[DataRequired(), Email()],
        description="Please use an email that won't be expiring in the next year (e.g. if you are a senior this applies to you because your account will be deactivated afte commencement)",
        render_kw={"placeholder": "nerdsrule@mit.edu"},
    )

    first_name = StringField(
        "First name",
        validators=[DataRequired(), Length(max=(64))],
        render_kw={"placeholder": "Tim"},
    )

    initials = StringField(
        "Initials",
        validators=[
            Optional(),
            Regexp(
                r"([A-Z]\.(\s{1}[A-Z]\.)*)$",
                message="Initials must be in all caps followed by a period. If you have multiple initials, please separate them with a space.",
            ),
        ],
    )

    last_name = StringField(
        "Last name",
        validators=[DataRequired(), Length(max=64)],
        render_kw={"placeholder": "Beaver"},
    )

    name_ok = BooleanField(label="OK to make your name public?", default=False)

    affiliation_choices = [[key.value, key.value] for key in AffiliationEnum]
    affiliation = SelectField(
        label="Affiliation",
        choices=affiliation_choices,
        description='This just allows us to figure out where to store your submissions, it has no bearing on you and your story. However, if you are an alumni and currently work for MIT, please select "Student or Alumni" and then tell us about your position below!',
        default=AffiliationEnum.StudentOrAlumni,
    )

    class_year = StringField(
        label="Class Year",
        validators=[Length(max=4, min=4, message="Please input the full year of your graduation (if you have multiple degrees, please use your earliest graduation date from MIT (typically undergrad)")],
        render_kw={"placeholder": 1861},
    )
    class_year_ok = BooleanField(label="OK to make your class year public?", default=False)

    
    major_choices = [ [major.name, str(major)] for major in Major.query.all()]
    major = SelectMultipleField(
        label="What Major(s) were you?",
        validators=[Length(max=2, message="You have selected more than two majors. MIT only gives out double majors ;-)")],
        choices=major_choices,
        description="Start typing your major, press the Enter key once your major is highlighted, otherwise select it with your mouse. On mobile, just scroll through the options wheel and tap on the one(s) you want."
    )
    major_ok = BooleanField(label="OK to make your major(s) public?", default=False)

    minor_choices = [ [minor.name, str(minor)] for minor in Minor.query.all()]
    minor = SelectMultipleField(
        label="What Minor(s) were you?",
        choices=minor_choices,
        description="Start typing your minor, press the Enter key once your major is highlighted, otherwise select it with your mouse. On mobile, just scroll through the options wheel and tap on the one(s) you want."
    )
    minor_ok = BooleanField(label="OK to make your minor(s) public?", default=False)

    lg = StringField(
        "Living Group",
        validators=[Length(max=128)],
        description="Please use the full name, e.g. \"Bexley Hall\"",
        render_kw={"placeholder": "Bexley Hall"},
    )
    lg_ok = BooleanField(label="OK to make your living group public?", default=False)

    activities = TextAreaField(
        label="Clubs and Other Activities",
        validators=[Length(max=500)],
        description="500 Characters Max. This is very open-ended, what are you/were you involved while you were at MIT? What clubs did you partake in? Which Committees were you on, etc."
    )
    activities_ok = BooleanField(label="OK to make your clubs & activities public?", default=False)

    bio = TextAreaField(
        label="Tell us about yourself!",
        validators=[Length(max=500)],
        description="This is very open ended, we included this as a way to allow people to let us know things that may not be covered by our basic questions. If you work at MIT, what do you do? If you're not a student or an alumni, what is your relationship to MIT? Have fun with this field! Otherwise, if we need information from you, we'll just reach out to you!"
    )
    bio_ok = BooleanField(label="OK to make your brief bio?", default=False)

class SendTestEmailForm(FlaskForm):
    email = StringField(
        label="Recipient Email",
        validators=[DataRequired(), Email()],
        description="Email to send test email to",
        default="dggsax@gmail.com"
    )