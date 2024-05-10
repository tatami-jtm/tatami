from . import db

from datetime import datetime

from flask_security import UserMixin, RoleMixin

roles_users = db.Table(
    'roles_users',
    db.Column(
        'user_id',
        db.Integer(),
        db.ForeignKey('user.id')),
    db.Column(
        'role_id',
        db.Integer(),
        db.ForeignKey('role.id')))


class Role(db.Model, RoleMixin):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))

    is_admin = db.Column(db.Boolean)
    may_create_tournaments = db.Column(db.Boolean)
    may_manage_users = db.Column(db.Boolean)
    may_alter_presets = db.Column(db.Boolean)


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True)
    password = db.Column(db.String(255))
    active = db.Column(db.Boolean())
    confirmed_at = db.Column(db.DateTime())
    roles = db.relationship('Role', secondary=roles_users,
                            backref=db.backref('users', lazy='dynamic'))
    fs_uniquifier = db.Column(db.String(255), unique=True, nullable=False)

    display_name = db.Column(db.String(50))
    prefers_dark_mode = db.Column(db.Boolean)

    _privilege = None

    def qualified_name(self):
        if self.display_name:
            return self.display_name
        else:
            return self.email

    def has_privilege(self, priv):
        if self._privilege is None:
            self._privilege = {
                "admin": False,
                "create_tournaments": False,
                "manage_users": False,
                "alter_presets": False,
            }

            for role in self.roles:
                if role.is_admin:
                    self._privilege['admin'] = True
                if role.may_create_tournaments:
                    self._privilege['create_tournaments'] = True
                if role.may_manage_users:
                    self._privilege['manage_users'] = True
                if role.may_alter_presets:
                    self._privilege['alter_presets'] = True

        return priv in self._privilege.keys() and (
            self._privilege['admin'] or self._privilege[priv])

    def get_all_supervised_events(self, in_the_future=False):
        evt_list = self.supervised_events[:]
        for role in self.roles:
            for evt in role.supervised_events:
                if evt not in evt_list:
                    evt_list.append(evt)

        if in_the_future:
            now = datetime.now()
            evt_list = filter(lambda e: now <= e.last_day, evt_list)

        return evt_list
