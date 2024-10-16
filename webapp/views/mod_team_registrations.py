from flask import Blueprint, render_template, flash, g, session, \
    request, redirect, url_for

from datetime import datetime as dt

from .event_manager import check_and_apply_event
from .devices import check_is_registered

from ..models import db, TeamRegistration

mod_team_registrations_view = Blueprint('mod_team_registrations', __name__)

@mod_team_registrations_view.route('/')
@check_and_apply_event
@check_is_registered
def index():
    if not g.device.event_role.may_use_registration:
        flash('Sie haben keine Berechtigung, hierauf zuzugreifen.', 'danger')
        return redirect(url_for('devices.index', event=g.event.slug))
    
    query = g.event.team_registrations.filter_by(confirmed=True)
    quarg = None
    qclid = None

    if "query" in request.values:
        quarg = request.values['query']

        if len(quarg):
            print(quarg)
            query = query.filter(TeamRegistration.team_name.ilike(f"%{quarg}%") |
                                 TeamRegistration.club.ilike(f"{quarg}"))

    if "event_class" in request.values:
        qclid = request.values['event_class']

        if len(qclid):
            query = query.filter(TeamRegistration.event_class_id==qclid)
            qclid = int(qclid)
        else:
            qclid = None

    query = query.order_by('event_class_id', 'club', 'team_name').all()
    
    return render_template("mod_team_registration/index.html", query=query, quarg=quarg, qclid=qclid)


@mod_team_registrations_view.route('/confirm/<id>')
@check_and_apply_event
@check_is_registered
def confirm(id):
    if not g.device.event_role.may_use_registration:
        flash('Sie haben keine Berechtigung, hierauf zuzugreifen.', 'danger')
        return redirect(url_for('devices.index', event=g.event.slug))
    
    tr = TeamRegistration.query.filter_by(event=g.event, id=id).one_or_404()
    tr.registered = True
    tr.registered_at = dt.now()
    db.session.commit()
    g.event.log(g.device.title, 'DEBUG', f'Team {tr.team_name} wurde akkreditiert.')

    return redirect(url_for('mod_team_registrations.index', event=g.event.slug))


@mod_team_registrations_view.route('/unconfirm/<id>')
@check_and_apply_event
@check_is_registered
def unconfirm(id):
    if not g.device.event_role.may_use_registration:
        flash('Sie haben keine Berechtigung, hierauf zuzugreifen.', 'danger')
        return redirect(url_for('devices.index', event=g.event.slug))
    
    tr = TeamRegistration.query.filter_by(event=g.event, id=id).one_or_404()
    tr.registered = False
    tr.registered_at = None
    db.session.commit()
    g.event.log(g.device.title, 'DEBUG', f'Team-Akkreditierung von {tr.team_name} wurde aufgehoben.')

    return redirect(url_for('mod_team_registrations.index', event=g.event.slug))