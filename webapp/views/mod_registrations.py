from flask import Blueprint, render_template, flash, g, session, \
    request, redirect, url_for, jsonify

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
    the_one_registration = None

    if "query" in request.values:
        query = query.filter(Registration.last_name.ilike(f"{request.values['query']}%") |
                             Registration.external_id.ilike(f"{request.values['query']}%") |
                             Registration.club.ilike(f"{request.values['query']}%") |
                             Registration.club.ilike(f"% {request.values['query']}%") |
                             Registration.club.ilike(f"%-{request.values['query']}%"))
        quarg = request.values['query']

    query = query.order_by('registered', 'last_name', 'first_name')

    if quarg:
        if query.count() == 1:
            the_one_registration = query.one()
        
        elif query.filter_by(external_id=quarg).count() == 1:
            the_one_registration = query.filter_by(external_id=quarg).one()
        
        elif query.filter_by(last_name=quarg).count() == 1:
            the_one_registration = query.filter_by(last_name=quarg).one()

    query = query.all()
    
    return render_template("mod_registration/index.html", query=query, quarg=quarg, the_one_registration=the_one_registration)


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
    g.event.log(g.device.title, 'DEBUG', f'{reg.short_name()} wurde akkreditiert.')

    query = None

    if 'query' in request.args:
        query = request.args['query']

    return redirect(url_for('mod_registrations.index', event=g.event.slug, query=query))


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
    g.event.log(g.device.title, 'DEBUG', f'Akkreditierung von {reg.short_name()} wurde aufgehoben.')

    query = None

    if 'query' in request.args:
        query = request.args['query']

    return redirect(url_for('mod_registrations.index', event=g.event.slug, query=query))


@mod_registrations_view.route('/api', methods=['POST'])
@check_and_apply_event
@check_is_registered
def api():
    if not g.device.event_role.may_use_registration:
        return jsonify({
            "result": "error",
            "message": "Sie haben keine Berechtigung, hierauf zuzugreifen"
        }), 401

    external_id = request.form.get('id', None)

    if not external_id:
        return jsonify({
            "result": "error",
            "message": "Fügen Sie die externe ID (Pass-ID) mit dem Formularfeld ?id bei."
        }), 400

    registration = Registration.query.filter_by(event=g.event, external_id=external_id).all()

    if len(registration) == 0:
        return jsonify({
            "result": "error",
            "message": "Kein TN mit dieser ID gefunden."
        }), 404
    
    elif len(registration) != 1:
        return jsonify({
            "result": "error",
            "message": "Mehrere TN mit dieser ID gefunden -- bitte wenden Sie sich an die Veranstaltungsleitung."
        }), 400
    
    registration = registration[0]

    registration.registered = True
    registration.registered_at = dt.now()
    db.session.commit()

    g.event.log(g.device.title, 'DEBUG', f'{registration.short_name()} wurde akkreditiert.')

    return jsonify({
        "result": "success"
    })