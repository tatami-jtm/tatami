from . import db
import base64
import re

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
    
    external_id = db.Column(db.String(50))

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
    
    def anon_name(self):
        return base64.b16encode(f"{self.id}".encode() + self.last_name.encode() + b" " + self.first_name.encode()).decode()[:24]
    
    def anon_club(self):
        if self.association:
            return base64.b16encode(self.club.encode() + b"+" + self.association.short_name.encode()).decode()[:18]
        else:
            return base64.b16encode(self.club.encode()).decode()[:18]
    
    def matches_status(self, filter):
        # All registrations match no filter
        if filter is None:
            return True
        
        if filter == 'not_yet_confirmed':
            return not self.confirmed
        
        elif filter == 'confirmed':
            return self.confirmed
        
        elif filter == 'not_yet_registered':
            return not self.registered
        
        elif filter == 'registered':
            return self.registered
        
        elif filter == 'registered_not_weighed_in':
            return self.registered and not self.weighed_in
        
        elif filter == 'weighed_in':
            return self.registered and self.weighed_in
        
        elif filter == 'weighed_in_without_registration':
            return not self.registered and self.weighed_in
        
        # No registrations match any other filter
        return False
    
    @classmethod
    def filter(cls, event, class_filter=None, event_class=None, status=None, name=None,
               club=None, order_by=None, external_id=None):
        query = cls.query.filter(cls.event_id==event.id)

        # Doing some db-black magic to prevent circular import issues
        EventClass = cls.event_class.mapper.class_

        if class_filter == 'single':
            query = query.filter(cls.event_class_id==event_class.id)
        elif class_filter == 'pending':
            data = map(lambda c: c.id, EventClass.query.filter_by(begin_weigh_in=False).all())
            query = query.filter(cls.event_class_id.in_(data))
        elif class_filter == 'weighing_in':
            data = map(lambda c: c.id, EventClass.query.filter_by(begin_weigh_in=True, begin_placement=False).all())
            query = query.filter(cls.event_class_id.in_(data))
        elif class_filter == 'weighed_in':
            data = map(lambda c: c.id, EventClass.query.filter_by(begin_placement=True, begin_fighting=False).all())
            query = query.filter(cls.event_class_id.in_(data))
        elif class_filter == 'fighting':
            data = map(lambda c: c.id, EventClass.query.filter_by(begin_fighting=True, ended_fighting=False).all())
            query = query.filter(cls.event_class_id.in_(data))
        elif class_filter == 'completed':
            data = map(lambda c: c.id, EventClass.query.filter_by(ended_fighting=True).all())
            query = query.filter(cls.event_class_id.in_(data))

        if name:
            name = name.replace('*', '%')
            if name.startswith('^'): # Filter for first name only
                query = query.filter(cls.first_name.ilike(f"{name[1:]}%"))
            elif name.startswith('$'): # Filter for last name only
                query = query.filter(cls.last_name.ilike(f"{name[1:]}%"))
            else:
                query = query.filter(cls.first_name.ilike(f"{name}%") | cls.last_name.ilike(f"{name}%"))

        if club:
            query = query.filter(cls.club.ilike(f"%{club}%"))

        if external_id:
            query = query.filter(cls.external_id.ilike(f"{external_id}%"))

        if order_by == 'first_name':
            query = query.order_by('first_name')
        elif order_by == 'last_name':
            query = query.order_by('last_name')
        elif order_by == 'club':
            query = query.order_by('club')
        elif order_by == 'verified_weight':
            query = query.order_by('verified_weight')
        else:
            query = query.order_by('last_name', 'first_name', 'club')

        query = query.all()

        if status:
            query = [*filter(lambda o: o.matches_status(status), query)]

        return query



class Association(db.Model):
    id = db.Column(db.Integer(), primary_key=True)

    event_id = db.Column(db.Integer(), db.ForeignKey('event.id'))
    event = db.relationship('Event', backref=db.backref(
        'associations', lazy='dynamic'))

    short_name = db.Column(db.String(10))
    name = db.Column(db.String(80))


class ListSystem(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    title = db.Column(db.String(50))
    list_file = db.Column(db.String(80))
    mandatory_minimum = db.Column(db.Integer())
    mandatory_maximum = db.Column(db.Integer())
    estimated_fight_count = db.Column(db.Integer())
    break_count = db.Column(db.Integer())
    display_page_count = db.Column(db.Integer(), default=1)
    enabled = db.Column(db.Boolean)

    @classmethod
    def all_enabled(cls):
        return cls.query.filter_by(enabled=True)
    
    @classmethod
    def for_range(cls, min, max):
        return cls.all_enabled().filter(
            (cls.mandatory_minimum <= min) & (cls.mandatory_maximum >= max)
        )


class ListSystemRule(db.Model):
    id = db.Column(db.Integer(), primary_key=True)

    event_id = db.Column(db.Integer(), db.ForeignKey('event.id'))
    event = db.relationship('Event', backref=db.backref(
        'list_system_rules', lazy='dynamic'))
    
    system_id = db.Column(db.Integer(), db.ForeignKey('list_system.id'))
    system = db.relationship('ListSystem')

    minimum = db.Column(db.Integer())
    maximum = db.Column(db.Integer())


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
    
    assigned = db.Column(db.Boolean)
    assigned_to_position_id = db.Column(db.Integer(), db.ForeignKey('device_position.id'))
    assigned_to_position = db.relationship('DevicePosition', backref=db.backref(
        'assigned_groups', lazy='dynamic'))
    
    system_id = db.Column(db.Integer(), db.ForeignKey('list_system.id'))
    system = db.relationship('ListSystem')

    marked_ready = db.Column(db.Boolean)
    marked_ready_at = db.Column(db.DateTime())

    opened = db.Column(db.Boolean)
    opened_at = db.Column(db.DateTime())

    completed = db.Column(db.Boolean)
    completed_at = db.Column(db.DateTime())

    random_seed = db.Column(db.Integer())

    currently_used = db.Column(db.Boolean)
    last_used_at = db.Column(db.DateTime())

    _system = (None, None) # for memoizing calculated system
    
    def cut_title(self):
        if not self.title:
            return ""
        
        return self.title[len(self.event_class.short_title) + 1:]


    def list_system(self):
        if self.system_id:
            return self.system
        
        participant_count = self.participants.count()

        if self._system[1] and self._system[0] == participant_count:
            return self._system[1]
        
        systems = ListSystemRule.query.filter_by(event=self.event)
        query = systems.filter(
            ListSystemRule.minimum <= participant_count,
            ListSystemRule.maximum >= participant_count)
        
        if query.count():
            self._system = participant_count, query.one().system

        return self._system[1]
    
    def estimated_fight_count(self):
        if self.participants.count() == 0:
            return 0

        return max(self.matches.count(), self.list_system().estimated_fight_count)
    
    def estimated_remaining_fight_count(self):
        completed_matches = self.matches.filter_by(completed=True).count()
        estimated_total_matches = self.estimated_fight_count()

        return max(0, estimated_total_matches - completed_matches)
    
    def estimated_remaining_fight_duration(self, in_minutes = False):
        # Don't overestimate when we're done already
        if self.completed:
            return 0

        estimated_match_count = self.estimated_remaining_fight_count()

        # Presumption:
        # 1/3rd of all matches will take only 1/2 of the fighting time
        # 1/3rd of all matches will take exactly the fighting time
        # 1/3rd of all matches will take 3/2 of the fighting time limited to the max golden score time
        fighting_time = self.event_class.fighting_time
        golden_score_time = self.event_class.golden_score_time

        short_match_duration = fighting_time / 2

        middle_match_duration = fighting_time

        if golden_score_time == -1:
            long_match_duration = fighting_time * 3 / 2
        
        else:
            long_match_duration = fighting_time + min(fighting_time * 1 / 2, golden_score_time)
        
        average_match_duration = (short_match_duration + middle_match_duration + long_match_duration) / 3

        if in_minutes:
            return int(0.5 + (estimated_match_count * average_match_duration) / 60)
        else:
            return estimated_match_count * average_match_duration
    
    def placements(self):
        return self.participants.filter(Participant.final_placement != None).order_by(Participant.final_placement).all()
    
    def all_participants_have_been_placed(self):
        return self.participants.filter(Participant.placement_index != None).count() > 0
    
    def download_name(self, file_suffix):
        name = self.cut_title()
        name = name.replace(".", "-")
        name = re.sub('[^a-zA-Z0-9_-]', '', name)
        return self.event_class.download_name(f"{name}_{file_suffix}")


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

    last_fight_at = db.Column(db.DateTime())

    event_id = db.Column(db.Integer(), db.ForeignKey('event.id'))
    event = db.relationship('Event', backref=db.backref(
        'participants', lazy='dynamic'))

    group_id = db.Column(db.Integer(), db.ForeignKey('group.id'))
    group = db.relationship('Group', backref=db.backref(
        'participants', lazy='dynamic'))

    registration_id = db.Column(db.Integer(), db.ForeignKey('registration.id'))
    registration = db.relationship('Registration', backref=db.backref(
        'participants', lazy='dynamic'))
    
    def matches(self):
        return self.white_matches + self.blue_matches