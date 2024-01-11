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


class ListSystem(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    title = db.Column(db.String(50))
    list_file = db.Column(db.String(80))
    mandatory_minimum = db.Column(db.Integer())
    mandatory_maximum = db.Column(db.Integer())
    estimated_fight_count = db.Column(db.Integer())
    enabled = db.Column(db.Boolean)

    @classmethod
    def all_enabled(cls):
        return cls.query.filter_by(enabled=True)


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