from . import db

class Registration(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    first_name = db.Column(db.String(80))
    last_name = db.Column(db.String(80))
    contact_details = db.Column(db.Text())
    club = db.Column(db.String(150))

    event_id = db.Column(db.Integer(), db.ForeignKey('event.id'))
    event = db.relationship('Event', backref=db.backref(
        'registrations', lazy='dynamic'))

    event_class_id = db.Column(db.Integer(), db.ForeignKey('event_class.id'))
    event_class = db.relationship('EventClass', backref=db.backref(
        'registrations', lazy='dynamic'))

    association_id = db.Column(db.Integer(), db.ForeignKey('association.id'))
    association = db.relationship('Association', backref=db.backref(
        'registrations', lazy='dynamic'))

    created_at = db.Column(db.DateTime())
    confirmed_at = db.Column(db.DateTime())
    registered_at = db.Column(db.DateTime())
    weighed_in_at = db.Column(db.DateTime())
    placed_at = db.Column(db.DateTime())

    confirmed = db.Column(db.Boolean())
    registered = db.Column(db.Boolean())
    weighed_in = db.Column(db.Boolean())
    placed = db.Column(db.Boolean())

    suggested_group = db.Column(db.String(150))
    verified_weight = db.Column(db.Integer()) # in 1g

    def short_name(self):
        assoc_pt = ""
        if self.association:
            assoc_pt = f" ({self.association.short_name})"

        return self.first_name[0].upper() + ". " + self.last_name.upper() + assoc_pt


class Association(db.Model):
    id = db.Column(db.Integer(), primary_key=True)

    event_id = db.Column(db.Integer(), db.ForeignKey('event.id'))
    event = db.relationship('Event', backref=db.backref(
        'associations', lazy='dynamic'))

    short_name = db.Column(db.String(10))
    name = db.Column(db.String(80))


class Group(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    title = db.Column(db.String(50))

    created_manually = db.Column(db.Boolean)
    assign_by_logic = db.Column(db.Boolean)
    min_weight = db.Column(db.Integer()) # in 1g
    max_weight = db.Column(db.Integer()) # in 1g

    event_id = db.Column(db.Integer(), db.ForeignKey('event.id'))
    event = db.relationship('Event', backref=db.backref(
        'groups', lazy='dynamic'))

    event_class_id = db.Column(db.Integer(), db.ForeignKey('event_class.id'))
    event_class = db.relationship('EventClass', backref=db.backref(
        'groups', lazy='dynamic'))


class Participant(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    full_name = db.Column(db.String(80))
    association_name = db.Column(db.String(80))

    placement_index = db.Column(db.Integer)
    manually_placed = db.Column(db.Boolean)

    final_placement = db.Column(db.Integer)
    final_points = db.Column(db.Integer) # 1 for each won fight
    final_score = db.Column(db.Integer) # 1, 7 or 10 pts. depending on the result for each won fight

    removed = db.Column(db.Boolean)
    disqualified = db.Column(db.Boolean)
    removal_cause = db.Column(db.Text(250))

    event_id = db.Column(db.Integer(), db.ForeignKey('event.id'))
    event = db.relationship('Event', backref=db.backref(
        'participants', lazy='dynamic'))

    group_id = db.Column(db.Integer(), db.ForeignKey('group.id'))
    group = db.relationship('Group', backref=db.backref(
        'participants', lazy='dynamic'))

    registration_id = db.Column(db.Integer(), db.ForeignKey('registration.id'))
    registration = db.relationship('Registration', backref=db.backref(
        'participants', lazy='dynamic'))