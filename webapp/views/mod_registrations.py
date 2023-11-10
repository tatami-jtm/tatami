from flask import Blueprint, render_template, flash, g, session, \
    request, redirect, url_for

from .event_manager import check_and_apply_event
from .devices import check_is_registered

from ..models import Registration

mod_registrations_view = Blueprint('mod_registrations', __name__)

@mod_registrations_view.route('/', methods=['GET', 'POST'])
@check_and_apply_event
@check_is_registered
def index():
    if not g.device.event_role.may_use_registration:
        flash('Sie haben keine Berechtigung, hierauf zuzugreifen.', 'danger')
        return redirect(url_for('devices.index', event=g.event.slug))
    
    query = g.event.registrations
    quarg = None

    if "query" in request.values:
        query = query.filter(Registration.last_name.ilike(f"{request.values['query']}%"))
        quarg = request.values['query']

    query = query.order_by('registered', 'last_name', 'first_name').all()
    
    return render_template("mod_registration/index.html", query=query, quarg=quarg)