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


# Class of 2020
# Class of 1970
# Other (MIT Community)
# tell us about in 500 characters -
# activities - 500 characters


class Member(TimeStampMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)

    email = db.Column(db.String(128), unique=True)

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

    dropbox_file_upload_url = db.Column(db.String(128))
    dropbox_shared_folder_url = db.Column(db.String(128))

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
