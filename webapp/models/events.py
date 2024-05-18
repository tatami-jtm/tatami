from . import db
from .matches import Match
from .participants import Group

import json
import hashlib
import datetime


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

    def setting(self, key, default_value=None, is_json=True):
        item = self.settings.filter_by(key=key).one_or_none()
        
        if item is None:
            return default_value
        
        else:
            if is_json:
                return json.loads(item.value)
            else:
                return item.value
            
    def save_setting(self, key, value, is_json=True):
        item = self.settings.filter_by(key=key).one_or_none()
        
        if item is None:
            item = EventSetting(event=self, key=key)
            db.session.add(item)
        
        if is_json:
            item.value = json.dumps(value)
        else:
            item.value = value

        db.session.commit()

    def reset_setting(self, key):
        item = self.settings.filter_by(key=key).one_or_none()
        if item is not None:
            db.session.delete(item)
        db.session.commit()

    def is_supervisor(self, user):
        return user == self.supervising_user or any(
            self.supervising_role == role for role in user.roles)
    
    def total_registrations_count(self):
        total_all = 0
        for cl in self.classes:
            total_all += cl.total_registrations_count()
        
        return total_all
    
    def confirmed_registrations_count(self):
        total_confirmed = 0
        for cl in self.classes:
            total_confirmed += cl.confirmed_registrations_count()
        
        return total_confirmed
    
    def registered_registrations_count(self):
        total_registered = 0
        for cl in self.classes:
            total_registered += cl.registered_registrations_count()
        
        return total_registered
    
    def weighed_registrations_count(self):
        total_weighed = 0
        for cl in self.classes:
            total_weighed += cl.weighed_registrations_count()
        
        return total_weighed
    
    def placed_registrations_count(self):
        total_placed = 0
        for cl in self.classes:
            total_placed += cl.placed_registrations_count()
        
        return total_placed
    
    def total_participants_count(self):
        return self.participants.count()
    
    def placed_participants_count(self):
        return self.total_participants_count() - self.participants.filter_by(placement_index=None).count()
    
    def placed_ratio(self):
        assigned_ratio = self.placed_registrations_count() / max(1, self.weighed_registrations_count())
        placed_ratio = self.placed_participants_count() / max(1, self.total_participants_count())

        return (assigned_ratio + placed_ratio) / 2
    
    def estimated_current_end(self):
        longest_running_mat_time = -1

        for mat in self.device_positions.filter_by(is_mat=True):
            this_mat_time = 0
            for group in mat.assigned_groups:
                this_mat_time += group.estimated_remaining_fight_duration()
            
            if this_mat_time > longest_running_mat_time:
                longest_running_mat_time = this_mat_time
        
        now = datetime.datetime.now()
        then = now + datetime.timedelta(0, longest_running_mat_time)

        return then

    def log(self, who, type, message):
        eli = EventLogItem(event=self)
        eli.log_type = type
        eli.log_value = message
        eli.log_creator = who
        eli.created_at = datetime.datetime.now()

        db.session.add(eli)
        db.session.commit()

    @classmethod
    def from_slug(cls, slug):
        return cls.query.where(cls.slug == slug).one()

    @classmethod
    def that_allows_registration(cls):
        return cls.query.where(cls.allow_device_registration).all()


class EventClass(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    title = db.Column(db.String(150))
    short_title = db.Column(db.String(30))

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
    default_maximal_size = db.Column(db.Integer())
    weight_generator = db.Column(db.Text())

    is_template = db.Column(db.Boolean())
    template_name = db.Column(db.String(75))

    event_id = db.Column(db.Integer(), db.ForeignKey('event.id'))
    event = db.relationship(
        'Event', backref=db.backref('classes', lazy='dynamic'))
    
    def total_registrations_count(self):
        return self.registrations.count()
    
    def confirmed_registrations_count(self):
        return self.registrations.filter_by(confirmed=True).count()
    
    def registered_registrations_count(self):
        return self.registrations.filter_by(confirmed=True, registered=True).count()
    
    def weighed_registrations_count(self):
        return self.registrations.filter_by(confirmed=True, registered=True, weighed_in=True).count()
    
    def placed_registrations_count(self):
        return self.registrations.filter_by(confirmed=True, registered=True, weighed_in=True, placed=True).count()

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
    may_use_beamer = db.Column(db.Boolean)
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
    
    def current_match(self):
        return Match.query.filter_by(running=True, completed=False).join(Match.group) \
            .join(Group.assigned_to_position) \
            .filter(DevicePosition.id==self.id).one_or_none()
    
    def waiting_match(self):
        return Match.query.filter_by(called_up=True, running=False).join(Match.group) \
            .join(Group.assigned_to_position) \
            .filter(DevicePosition.id==self.id).one_or_none()
    
    def scheduled_matches(self, include_called_up=True):
        query = Match.query.filter_by(scheduled=True, completed=False).join(Match.group) \
            .join(Group.assigned_to_position) \
            .filter(DevicePosition.id==self.id).order_by(Match.match_schedule_key.asc())
        
        if not include_called_up:
            query = query.filter(Match.called_up!=True)
        
        return query.all()


class EventSetting(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    key = db.Column(db.String(50))

    value = db.Column(db.Text())

    event_id = db.Column(db.Integer(), db.ForeignKey('event.id'))
    event = db.relationship('Event', backref=db.backref(
        'settings', lazy='dynamic'))


class EventLogItem(db.Model):
    id = db.Column(db.Integer(), primary_key=True)

    event_id = db.Column(db.Integer(), db.ForeignKey('event.id'))
    event = db.relationship('Event', backref=db.backref(
        'log_items', lazy='dynamic'))
    
    log_type = db.Column(db.String(50))
    log_value = db.Column(db.Text)
    log_creator = db.Column(db.String(150))
    created_at = db.Column(db.DateTime())