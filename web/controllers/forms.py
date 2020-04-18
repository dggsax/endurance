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

    name_ok = BooleanField(label="OK to make your name public?", default=True)

    affiliation_choices = [[key.value, key.value] for key in AffiliationEnum]
    affiliation = SelectField(
        label="Affiliation",
        choices=affiliation_choices,
        description='This just allows us to figure out where to store your submissions, it has no bearing on you and your story. However, if you are an alumni and currently work for MIT, please select "Student or Alumni" and then tell us about your position below!',
        default=AffiliationEnum.StudentOrAlumni,
    )

    class_year = StringField(
        label="Class Year",
        validators=[DataRequired(), Length(max=4, min=4)],
        render_kw={"placeholder": 1861},
    )
    class_year_ok = BooleanField(label="OK to make your class year public?", default=True)

    
    major_choices = sorted([ [major.name, str(major)] for major in Major.query.all()])
    major = SelectMultipleField(
        label="What Major(s) were you?",
        validators=[Length(max=2, message="You have selected more than two majors. MIT only gives out double majors ;-)")],
        choices=major_choices,
        description="Hold Ctrl or Cmd to select multiple. Drag bottom-right hand corner to expand the table."
    )
    major_ok = BooleanField(label="OK to make your major(s) public?", default=True)

    minor_choices = sorted([ [minor.name, str(minor)] for minor in Minor.query.all()])
    minor = SelectMultipleField(
        label="What Minor(s) were you?",
        choices=minor_choices,
        description="Hold Ctrl or Cmd to select multiple. Drag bottom-right hand corner to expand the table."
    )
    minor_ok = BooleanField(label="OK to make your minor(s) public?", default=True)

    lg = StringField(
        "Living Group",
        validators=[Length(max=128)],
        description="Please use the full name, e.g. \"Bexley Hall\"",
        render_kw={"placeholder": "Bexley Hall"},
    )
    lg_ok = BooleanField(label="OK to make your living group public?", default=True)

    activities = TextAreaField(
        label="Clubs and Other Activities",
        validators=[Length(max=500)],
        description="500 Characters Max. This is very open-ended, what are you/were you involved while you were at MIT? What clubs did you partake in? Which Committees were you on, etc."
    )
    activities_ok = BooleanField(label="OK to make your clubs & activities public?", default=True)

