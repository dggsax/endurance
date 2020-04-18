from web.models import db
from .member import Member

class Major(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    member_id = db.Column(db.Integer, db.ForeignKey(Member.id))
    shorthand = db.Column(db.String(16), unique=True)
    name = db.Column(db.String(64), unique=True)

class Minor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    shorthand = db.Column(db.String(16), unique=True)
    name = db.Column(db.String(64), unique=True)