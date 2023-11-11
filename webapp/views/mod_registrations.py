from flask import Blueprint, render_template, flash, g, session, \
    request, redirect, url_for

from datetime import datetime as dt

from .event_manager import check_and_apply_event
from .devices import check_is_registered

from ..models import db, Registration

mod_registrations_view = Blueprint('mod_registrations', __name__)

@mod_registrations_view.route('/')
@check_and_apply_event
@check_is_registered
def index():
    if not g.device.event_role.may_use_registration:
        flash('Sie haben keine Berechtigung, hierauf zuzugreifen.', 'danger')
        return redirect(url_for('devices.index', event=g.event.slug))
    
    query = g.event.registrations.filter_by(confirmed=True)
    quarg = None

    if "query" in request.values:
        query = query.filter(Registration.last_name.ilike(f"{request.values['query']}%"))
        quarg = request.values['query']

    query = query.order_by('registered', 'last_name', 'first_name').all()
    
    return render_template("mod_registration/index.html", query=query, quarg=quarg)


@mod_registrations_view.route('/confirm/<id>')
@check_and_apply_event
@check_is_registered
def confirm(id):
    if not g.device.event_role.may_use_registration:
        flash('Sie haben keine Berechtigung, hierauf zuzugreifen.', 'danger')
        return redirect(url_for('devices.index', event=g.event.slug))
    
    reg = Registration.query.filter_by(event=g.event, id=id).one_or_404()
    reg.registered = True
    reg.registered_at = dt.now()
    db.session.commit()

    return redirect(url_for('mod_registrations.index', event=g.event.slug))


@mod_registrations_view.route('/unconfirm/<id>')
@check_and_apply_event
@check_is_registered
def unconfirm(id):
    if not g.device.event_role.may_use_registration:
        flash('Sie haben keine Berechtigung, hierauf zuzugreifen.', 'danger')
        return redirect(url_for('devices.index', event=g.event.slug))
    
    reg = Registration.query.filter_by(event=g.event, id=id).one_or_404()
    reg.registered = False
    reg.registered_at = None
    db.session.commit()

    return redirect(url_for('mod_registrations.index', event=g.event.slug))