from . import db


class Event(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    title = db.Column(db.String(150))
    slug = db.Column(db.String(65))

    first_day = db.Column(db.DateTime())
    last_day = db.Column(db.DateTime())

    supervising_user_id = db.Column(db.Integer(), db.ForeignKey('user.id'))
    supervising_user = db.relationship(
        'User', backref=db.backref('supervised_events', lazy='dynamic'))

    supervising_role_id = db.Column(db.Integer(), db.ForeignKey('role.id'))
    supervising_role = db.relationship(
        'Role', backref=db.backref('supervised_events', lazy='dynamic'))

    def is_supervisor(self, user):
        return user == self.supervising_user or any(self.supervising_role == role for role in user.roles)
    
    @classmethod
    def from_slug(cls, slug):
        return cls.query.where(cls.slug==slug).one()