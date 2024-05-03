from . import db
from ..listslib.match_result import MatchResult as ListMatchResult
from datetime import datetime as dt
import json

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
    list_tags = db.Column(db.String(85))
    is_playoff = db.Column(db.Boolean)
    
    scheduled = db.Column(db.Boolean)
    scheduled_at = db.Column(db.DateTime())

    called_up = db.Column(db.Boolean)
    called_up_at = db.Column(db.DateTime())

    running = db.Column(db.Boolean)
    running_since = db.Column(db.DateTime())

    completed = db.Column(db.Boolean)
    completed_at = db.Column(db.DateTime())

    def get_result(self):
        if self.results.count() != 1:
            return True, MatchResult(match=self)
        
        else:
            return False, self.results.first()
        
    def has_result(self):
        return self.results.count() == 1
    
    def schedulable(self):
        now = dt.now()
        break_time = self.group.event_class.between_fights_time

        if self.white.last_fight_at is not None:
            if (now - self.white.last_fight_at).total_seconds() < break_time:
                return False
        
        if self.blue.last_fight_at is not None:
            if (now - self.blue.last_fight_at).total_seconds() < break_time:
                return False
        
        return True


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

    def winner(self):
        if self.is_white_winner:
            return 'white'
        elif self.is_blue_winner:
            return 'blue'
    
    def score(self):
        winner = self.winner()
        if winner == 'white':
            return self.white_score
        elif winner == 'blue':
            return self.blue_score
        
    def loser_disqualified(self):
        winner = self.winner()
        if winner == 'white':
            return self.is_blue_disqualified
        elif winner == 'blue':
            return self.is_white_disqualified

    def loser_removed(self):
        winner = self.winner()
        if winner == 'white':
            return self.is_blue_removed
        elif winner == 'blue':
            return self.is_white_removed
    
    def _make_list_result(self):
        return ListMatchResult.mk(self.white_points, self.white_score, None,
                                  self.blue_points, self.blue_score, None,
                                  None, None)
    
    def data(self):
        data = {}

        if self.scoreboard_data:
            data.update(json.loads(self.scoreboard_data))
        
        if self.full_time is not None:
            data['full_time'] = f"{self.full_time // 60}:" + f"00{self.full_time % 60}"[-2:]

        if len(data.keys()) == 0:
            return None
        
        return data