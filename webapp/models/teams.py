from . import db


class TeamRow(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    title = db.Column(db.String(40))
    match_order_key = db.Column(db.Integer())

    created_manually = db.Column(db.Boolean)
    assign_by_logic = db.Column(db.Boolean)
    min_weight = db.Column(db.Integer()) # in 1g
    max_weight = db.Column(db.Integer()) # in 1g

    event_id = db.Column(db.Integer(), db.ForeignKey('event.id'))
    event = db.relationship('Event', backref=db.backref(
        'team_rows', lazy='dynamic'))

    event_class_id = db.Column(db.Integer(), db.ForeignKey('event_class.id'))
    event_class = db.relationship('EventClass', backref=db.backref(
        'team_rows', lazy='dynamic'))
    
    lower_row_id = db.Column(db.Integer(), db.ForeignKey('team_row.id'))
    lower_row = db.relationship('TeamRow', backref=db.backref(
        'higher_row', lazy='dynamic'))


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


class TeamMember(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    full_name = db.Column(db.String(80))
    association_name = db.Column(db.String(80))

    removed = db.Column(db.Boolean)
    disqualified = db.Column(db.Boolean)
    removal_cause = db.Column(db.Text(250))

    last_fight_at = db.Column(db.DateTime())

    event_id = db.Column(db.Integer(), db.ForeignKey('event.id'))
    event = db.relationship('Event', backref=db.backref(
        'participants', lazy='dynamic'))

    team_id = db.Column(db.Integer(), db.ForeignKey('team.id'))
    team = db.relationship('Team', backref=db.backref(
        'members', lazy='dynamic'))
    
    row_id = db.Column(db.Integer(), db.ForeignKey('team_row.id'))
    row = db.relationship('TeamRow', backref=db.backref(
        'team_members', lazy='dynamic'))

    registration_id = db.Column(db.Integer(), db.ForeignKey('registration.id'))
    registration = db.relationship('Registration', backref=db.backref(
        'participants', lazy='dynamic'))