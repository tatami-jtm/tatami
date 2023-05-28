from . import db

import hashlib


class Event(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    title = db.Column(db.String(150))
    slug = db.Column(db.String(65))

    first_day = db.Column(db.DateTime())
    last_day = db.Column(db.DateTime())

    allow_device_registration = db.Column(db.Boolean())

    supervising_user_id = db.Column(db.Integer(), db.ForeignKey('user.id'))
    supervising_user = db.relationship(
        'User', backref=db.backref('supervised_events', lazy='dynamic'))

    supervising_role_id = db.Column(db.Integer(), db.ForeignKey('role.id'))
    supervising_role = db.relationship(
        'Role', backref=db.backref('supervised_events', lazy='dynamic'))

    def is_supervisor(self, user):
        return user == self.supervising_user or any(
            self.supervising_role == role for role in user.roles)

    @classmethod
    def from_slug(cls, slug):
        return cls.query.where(cls.slug == slug).one()

    @classmethod
    def that_allows_registration(cls):
        return cls.query.where(cls.allow_device_registration).all()


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

    use_proximity_weight_mode = db.Column(db.Boolean())  # gewichtsnahe Gruppen
    default_maximal_proximity = db.Column(db.Integer())
    weight_generator = db.Column(db.Text())

    is_template = db.Column(db.Boolean())
    template_name = db.Column(db.String(75))

    event_id = db.Column(db.Integer(), db.ForeignKey('event.id'))
    event = db.relationship(
        'Event', backref=db.backref('classes', lazy='dynamic'))


class EventRole(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))

    may_use_registration = db.Column(db.Boolean)
    may_use_weigh_in = db.Column(db.Boolean)
    may_use_placement_tool = db.Column(db.Boolean)
    may_use_global_list = db.Column(db.Boolean)
    may_use_assigned_lists = db.Column(db.Boolean)
    may_use_scoreboard = db.Column(db.Boolean)
    may_use_display = db.Column(db.Boolean)
    may_use_results = db.Column(db.Boolean)


class DeviceRegistration(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    title = db.Column(db.String(150))
    token = db.Column(db.String(60), unique=True)

    event_id = db.Column(db.Integer(), db.ForeignKey('event.id'))
    event = db.relationship('Event', backref=db.backref(
        'device_registrations', lazy='dynamic'))

    registered_at = db.Column(db.DateTime())
    confirmed_at = db.Column(db.DateTime())
    last_used_at = db.Column(db.DateTime())

    confirmed = db.Column(db.Boolean())

    registered_by_id = db.Column(db.Integer(), db.ForeignKey('user.id'))
    registered_by = db.relationship('User')

    event_role_id = db.Column(db.Integer(), db.ForeignKey('event_role.id'))
    event_role = db.relationship('EventRole')

    position_id = db.Column(db.Integer(), db.ForeignKey('device_position.id'))
    position = db.relationship(
        'DevicePosition', backref=db.backref('devices', lazy='dynamic'))

    def get_human_readable_code(self):
        token_hash = hashlib.md5(self.token.encode()).hexdigest()
        return token_hash[:6]


class DevicePosition(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    title = db.Column(db.String(150))
    position = db.Column(db.Integer())

    is_mat = db.Column(db.Boolean())

    event_id = db.Column(db.Integer(), db.ForeignKey('event.id'))
    event = db.relationship('Event', backref=db.backref(
        'device_positions', lazy='dynamic'))
