from flask import Blueprint, render_template, flash, g, session, \
    request, redirect, url_for

from datetime import datetime as dt

from .event_manager import check_and_apply_event
from .devices import check_is_registered

from ..models import db, Registration

mod_weighin_view = Blueprint('mod_weighin', __name__)

@mod_weighin_view.route('/')
@check_and_apply_event
@check_is_registered
def index():
    if not g.device.event_role.may_use_weigh_in:
        flash('Sie haben keine Berechtigung, hierauf zuzugreifen.', 'danger')
        return redirect(url_for('devices.index', event=g.event.slug))
    
    query = g.event.registrations.filter_by(confirmed=True, weighed_in=False)
    quarg = None

    if "query" in request.values:
        query = query.filter(Registration.last_name.ilike(f"{request.values['query']}%"))
        quarg = request.values['query']

    query = query.order_by('weighed_in', 'registered', 'last_name', 'first_name').all()

    # only currently weighing classes:
    query = [q for q in query if q.event_class.begin_weigh_in and not q.event_class.begin_placement]
    
    return render_template("mod_weighin/index.html", query=query, quarg=quarg)