from flask import Blueprint, render_template, abort, flash, g
from flask_security import login_required, current_user

from ..models import db, Event, EventClass, DevicePosition, EventRole

eventmgr_view = Blueprint('event_manager', __name__)


def check_and_apply_event(func):
    def inner_func(event, *args, **kwargs):
        event = Event.from_slug(event)

        g.event = event

        return func(*args, **kwargs)
    
    inner_func.__name__ = func.__name__
    return inner_func

def check_is_event_supervisor(func):
    def inner_func(*args, **kwargs):
        if not g.event.is_supervisor(current_user) and not current_user.has_privilege('create_tournaments'):
            abort(404)

        return func(*args, **kwargs)
    
    inner_func.__name__ = func.__name__
    return inner_func


@eventmgr_view.route('/')
@login_required
@check_and_apply_event
@check_is_event_supervisor
def index():
    return render_template("event-manager/index.html")

@eventmgr_view.route('/classes')
@login_required
@check_and_apply_event
@check_is_event_supervisor
def classes():
    return render_template("event-manager/classes/index.html")

@eventmgr_view.route('/devices')
@login_required
@check_and_apply_event
@check_is_event_supervisor
def devices():
    mat_pos = DevicePosition.query.filter_by(event=g.event, is_mat=True).order_by('position').all()
    admin_pos = DevicePosition.query.filter_by(event=g.event, is_mat=False).order_by('position').all()
    roles = EventRole.query.all()
    return render_template("event-manager/devices.html", mat_pos=mat_pos, roles=roles, admin_pos=admin_pos)
