from flask import current_app, url_for, request
from flask_login import UserMixin
from itsdangerous import JSONWebSignatureSerializer as Serializer
from itsdangerous import BadSignature, SignatureExpired
from web import login_manager
from web.models import db
from web.models.enums import AffiliationEnum

import datetime


class TimeStampMixin(object):
    created = db.Column(db.DateTime, nullable=False, default=datetime.datetime.utcnow)
    updated = db.Column(db.DateTime, onupdate=datetime.datetime.utcnow)


major_association_table = db.Table(
    "major_association",
    db.Model.metadata,
    db.Column("member_id", db.Integer, db.ForeignKey("member.id")),
    db.Column("major_id", db.Integer, db.ForeignKey("major.id")),
)

minor_association_table = db.Table(
    "minor_association",
    db.Model.metadata,
    db.Column("member_id", db.Integer, db.ForeignKey("member.id")),
    db.Column("minor_id", db.Integer, db.ForeignKey("minor.id")),
)

class Member(TimeStampMixin, UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)

    email = db.Column(db.String(128), unique=True)
    admin = db.Column(db.Boolean, default=False)

    first_name = db.Column(db.String(64), nullable=False)
    initials = db.Column(db.String(12))
    last_name = db.Column(db.String(64), nullable=False)
    name_ok = db.Column(db.Boolean, default=False)

    affiliation = db.Column(
        db.Enum(AffiliationEnum), default=AffiliationEnum.StudentOrAlumni
    )

    class_year = db.Column(db.Integer, default=1861)
    class_year_ok = db.Column(db.Boolean, default=False)

    lg = db.Column(db.String(128))
    lg_ok = db.Column(db.Boolean, default=False)

    major = db.relationship(
        lambda: Major, secondary=major_association_table, back_populates="victims"
    )
    major_ok = db.Column(db.Boolean, default=False)

    minor = db.relationship(
        lambda: Minor, secondary=minor_association_table, back_populates="victims"
    )
    minor_ok = db.Column(db.Boolean, default=False)

    # TODO create activities table and establish many-to-many relationship
    #   among restricted set of activities
    activities = db.Column(db.String(500))
    activities_ok = db.Column(db.Boolean, default=False)

    bio = db.Column(db.String(500))
    bio_ok = db.Column(db.Boolean, default=False)

    dropbox_file_request_id = db.Column(db.String(32))
    dropbox_file_upload_url = db.Column(db.String(128))
    dropbox_shared_folder_url = db.Column(db.String(128))

    # Authentication
    magic_token = db.Column(db.String(500))

    def magic_link(self):
        """
        magic_link Generate and return a magic link URL
        """

        magic_link = f"{request.base_url}/login?email={self.email}&token={self.magic_token}"

        return magic_link


    def generate_magic_link_token(self, reset=False):
        """
        Generate a magic login token to email to an existing user THAT DOES NOT EXPIRE.
        If this method is called and the user already have an magic_token, it will replace
        the existing auth token.
        """

        if reset or self.magic_token is None:
            s = Serializer(current_app.config['SECRET_KEY'])
            self.magic_token = s.dumps({'member_id': self.id}).decode('utf-8')
            # self.last_edited = datetime.datetime.utcnow()
            db.session.commit()

        return self.magic_token

    def verify_magic_link_token(self, token):
        """Verify the auth token for this user."""
        s = Serializer(current_app.config['SECRET_KEY'])

        try:
            data = s.loads(token)
            print(data)
        except (BadSignature, SignatureExpired) as e:
            return False
        if data.get('member_id') != self.id:
            return False
        return True

    def pretty_print(self):
        return f"<Member name='{self.full_name_for_path()}' ({self.name_ok}) \
            \n\temail='{self.email}' affiliation='{self.affiliation}' \
            \n\tyear='{self.class_year}' ({self.class_year_ok}) \
            \n\tmajors={self.major} ({self.major_ok}) \
            \n\tminors={self.minor} ({self.minor_ok}) \
            \n\tlg='{self.lg}' ({self.lg_ok}) \
            \n\tbio='{self.bio}' ({self.bio_ok}' \
            \n\tactivities='{self.activities}' ({self.activities_ok})"

    def full_name(self, initials=False):
        """
        full_name Returns the full name of the member. If `initials` is set to True, initials are included, otherwise it is just first and last name.
        
        :param initials: whether or not to include initials in string, defaults to False
        :type initials: bool, optional
        :return: full name for member
        :rtype: str
        """
        if initials:
            return f"{self.first_name} {self.initials} {self.last_name}"
        else:
            return f"{self.first_name} {self.last_name}"

    def full_name_for_path(self):
        """Generate name formatted by Last, First Initials, used for path generation"""
        if self.initials:
            return f"{self.last_name}, {self.first_name} {self.initials}"
        else:
            return f"{self.last_name}, {self.first_name}"


class Major(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    shorthand = db.Column(db.String(32))
    name = db.Column(db.String(256), unique=True)
    victims = db.relationship(
        lambda: Member, secondary=major_association_table, back_populates="major"
    )

    def __repr__(self):
        return f"<Major name={self.name}>"

    def __str__(self):
        return f"{self.shorthand} - {self.name}"


class Minor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    shorthand = db.Column(db.String(32))
    name = db.Column(db.String(256), unique=True)
    victims = db.relationship(
        lambda: Member, secondary=minor_association_table, back_populates="minor"
    )

    def __repr__(self):
        return f"<Minor name={self.name}>"

    def __str__(self):
        return f"{self.shorthand} - {self.name}"

@login_manager.user_loader
def load_user(user_id):
    return Member.query.get(int(user_id))