from . import db

class Event(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    title = db.Column(db.String(150))
    slug = db.Column(db.String(65))

    first_day = db.Column(db.DateTime())
    last_day = db.Column(db.DateTime())