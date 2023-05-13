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
    

class EventClass(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    title = db.Column(db.String(150))

    begin_weigh_in = db.Column(db.Boolean())
    begin_weigh_in_at = db.Column(db.DateTime())

    begin_placement = db.Column(db.Boolean())
    begin_placement_at = db.Column(db.DateTime())

    begin_fighting = db.Column(db.Boolean())
    begin_fighting_at = db.Column(db.DateTime())

    ended_fighting = db.Column(db.Boolean())
    ended_fighting_at = db.Column(db.DateTime())

    fighting_time = db.Column(db.Integer())
    golden_score_time = db.Column(db.Integer())
    between_fights_time = db.Column(db.Integer())

    use_proximity_weight_mode = db.Column(db.Boolean()) # gewichtsnahe Gruppen
    default_maximal_proximity = db.Column(db.Integer())
    weight_generator = db.Column(db.Text())

    event_id = db.Column(db.Integer(), db.ForeignKey('event.id'))
    event = db.relationship('Event', backref=db.backref('classes', lazy='dynamic'))