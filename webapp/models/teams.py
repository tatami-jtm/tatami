from . import db

class TeamRegistration(db.Model):
    id = db.Column(db.Integer(), primary_key=True)

    team_name = db.Column(db.String(80))
    club = db.Column(db.String(150))

    event_id = db.Column(db.Integer(), db.ForeignKey('event.id'))
    event = db.relationship('Event', backref=db.backref(
        'team_registrations', lazy='dynamic'))

    event_class_id = db.Column(db.Integer(), db.ForeignKey('event_class.id'))
    event_class = db.relationship('EventClass', backref=db.backref(
        'team_registrations', lazy='dynamic'))

    association_id = db.Column(db.Integer(), db.ForeignKey('association.id'))
    association = db.relationship('Association', backref=db.backref(
        'team_registrations', lazy='dynamic'))

    created_at = db.Column(db.DateTime())
    confirmed_at = db.Column(db.DateTime())
    registered_at = db.Column(db.DateTime())
    placed_at = db.Column(db.DateTime())

    confirmed = db.Column(db.Boolean())
    registered = db.Column(db.Boolean())
    placed = db.Column(db.Boolean())



class Team(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    team_name = db.Column(db.String(80))

    team_registration_id = db.Column(db.Integer(), db.ForeignKey('team_registration.id'))
    team_registration = db.relationship('TeamRegistration', backref=db.backref(
        'teams', lazy='dynamic'))

    event_id = db.Column(db.Integer(), db.ForeignKey('event.id'))
    event = db.relationship('Event', backref=db.backref(
        'teams', lazy='dynamic'))

    event_class_id = db.Column(db.Integer(), db.ForeignKey('event_class.id'))
    event_class = db.relationship('EventClass', backref=db.backref(
        'teams', lazy='dynamic'))

    placement_index = db.Column(db.Integer)
    manually_placed = db.Column(db.Boolean)

    final_placement = db.Column(db.Integer)
    final_points = db.Column(db.Integer) # 1 for each won fight
    final_score = db.Column(db.Integer) # num of pts. depending on team fight result

    removed = db.Column(db.Boolean)
    disqualified = db.Column(db.Boolean)
    removal_cause = db.Column(db.Text(250))