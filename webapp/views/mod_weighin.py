from flask import Blueprint, render_template, flash, g, session, \
    request, redirect, url_for, jsonify

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
        query = query.filter(Registration.last_name.ilike(f"{request.values['query']}%") |
                             Registration.external_id.ilike(f"{request.values['query']}%"))
        quarg = request.values['query']

    query = query.order_by('weighed_in', 'registered', 'last_name', 'first_name').all()

    # only currently weighing classes:
    query = [q for q in query if q.event_class.begin_weigh_in and not q.event_class.begin_placement]
    
    return render_template("mod_weighin/index.html", query=query, quarg=quarg)


@mod_weighin_view.route('/for/<id>', methods=['GET', 'POST'])
@check_and_apply_event
@check_is_registered
def for_participant(id):
    if not g.device.event_role.may_use_weigh_in:
        flash('Sie haben keine Berechtigung, hierauf zuzugreifen.', 'danger')
        return redirect(url_for('devices.index', event=g.event.slug))
    
    registration = Registration.query.filter_by(event=g.event, id=id, confirmed=True, weighed_in=False).one_or_404()

    if request.method == 'POST':
        registration.weighed_in = True
        registration.weighed_in_at = dt.now()

        if not registration.registered and g.event.setting('count_weighin_as_registration', False):
            registration.registered = True
            registration.registered_at = dt.now()
        
        registration.verified_weight = int(float(request.form['verified_weight']) * 1000)

        db.session.commit()
        g.event.log(g.device.title, 'DEBUG', f'{registration.short_name()} auf {registration.verified_weight / 1000} kg eingewogen')

        return redirect(url_for("mod_weighin.index", event=g.event.slug))
    
    return render_template("mod_weighin/for_participant.html", registration=registration)


@mod_weighin_view.route('/api', methods=['POST'])
@check_and_apply_event
@check_is_registered
def api():
    if not g.device.event_role.may_use_weigh_in:
        return jsonify({
            "result": "error",
            "message": "Sie haben keine Berechtigung, hierauf zuzugreifen"
        }), 401
    
    external_id = request.form.get('id', None)
    weight = request.form.get('weight', None)

    if not external_id:
        return jsonify({
            "result": "error",
            "message": "Fügen Sie die externe ID (Pass-ID) mit dem Formularfeld ?id bei."
        }), 400
    
    if not weight:
        return jsonify({
            "result": "error",
            "message": "Fügen Sie das Gewicht mit dem Formularfeld ?weight als Float in 1kg bei."
        }), 400
    
    registration = Registration.query.filter_by(event=g.event, external_id=external_id, confirmed=True, weighed_in=False).all()

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
    
    registration.weighed_in = True
    registration.weighed_in_at = dt.now()

    if not registration.registered and g.event.setting('count_weighin_as_registration', False):
        registration.registered = True
        registration.registered_at = dt.now()
    
    registration.verified_weight = int(float(weight) * 1000)

    db.session.commit()
    g.event.log(g.device.title, 'DEBUG', f'{registration.short_name()} auf {registration.verified_weight / 1000} kg eingewogen')

    return jsonify({
        "result": "success",
        "is_registered": registration.registered
    })
