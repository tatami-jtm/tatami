from flask import Blueprint, render_template, abort, flash, g
from flask_security import login_required, current_user

from ..models import db, Event, EventClass

eventmgr_view = Blueprint('event_manager', __name__)


def check_and_apply_event(func):
    def inner_func(event, *args, **kwargs):
        event = Event.from_slug(event)

        g.event = event

        return func(event, *args, **kwargs)
    
    inner_func.__name__ = func.__name__
    return inner_func

def check_is_event_supervisor(func):
    def inner_func(event, *args, **kwargs):
        if not g.event.is_supervisor(current_user) and not current_user.has_privilege('create_tournaments'):
            abort(404)

        return func(event, *args, **kwargs)
    
    inner_func.__name__ = func.__name__
    return inner_func


@eventmgr_view.route('/')
@login_required
@check_and_apply_event
@check_is_event_supervisor
def index(event):
    return render_template("event-manager/index.html")

@eventmgr_view.route('/classes')
@login_required
@check_and_apply_event
@check_is_event_supervisor
def classes(event):
    return render_template("event-manager/classes/index.html")
