from . import db

class Match(db.Model):
    id = db.Column(db.Integer(), primary_key=True)

    event_id = db.Column(db.Integer(), db.ForeignKey('event.id'))
    event = db.relationship('Event', backref=db.backref(
        'matches', lazy='dynamic'))
    
    event_class_id = db.Column(db.Integer(), db.ForeignKey('event_class.id'))
    event_class = db.relationship('EventClass', backref=db.backref(
        'matches', lazy='dynamic'))

    group_id = db.Column(db.Integer(), db.ForeignKey('group.id'))
    group = db.relationship('Group', backref=db.backref(
        'matches', lazy='dynamic'))

    white_id = db.Column(db.Integer(), db.ForeignKey('participant.id'))
    white = db.relationship('Participant', foreign_keys=[white_id], backref=db.backref(
        'white_matches', lazy='dynamic'))

    blue_id = db.Column(db.Integer(), db.ForeignKey('participant.id'))
    blue = db.relationship('Participant', foreign_keys=[blue_id], backref=db.backref(
        'blue_matches', lazy='dynamic'))
    
    match_schedule_key = db.Column(db.Integer())
    listslib_match_id = db.Column(db.String(35))
    
    scheduled = db.Column(db.Boolean)
    scheduled_at = db.Column(db.DateTime())

    called_up = db.Column(db.Boolean)
    called_up_at = db.Column(db.DateTime())

    running = db.Column(db.Boolean)
    running_since = db.Column(db.DateTime())

    completed = db.Column(db.Boolean)
    completed_at = db.Column(db.DateTime())


class MatchResult(db.Model):
    id = db.Column(db.Integer(), primary_key=True)

    match_id = db.Column(db.Integer(), db.ForeignKey('match.id'))
    match = db.relationship('Match', backref=db.backref(
        'results', lazy='dynamic'))
    
    white_points = db.Column(db.Integer()) # 1 if winner 0 else
    white_score = db.Column(db.Integer()) # 10/7/1 for winner 0 else
    is_white_winner = db.Column(db.Boolean())
    is_white_disqualified = db.Column(db.Boolean()) # direct hansoku make
    is_white_removed = db.Column(db.Boolean()) # e. g. injury

    blue_points = db.Column(db.Integer()) # 1 if winner 0 else
    blue_score = db.Column(db.Integer()) # 10/7/1 for winner 0 else
    is_blue_winner = db.Column(db.Boolean())
    is_blue_disqualified = db.Column(db.Boolean()) # direct hansoku make
    is_blue_removed = db.Column(db.Boolean()) # e. g. injury

    scoreboard_data = db.Column(db.Text())
    full_time = db.Column(db.Integer())
    