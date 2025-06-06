from flask import Blueprint, render_template, flash, g, session, \
    request, redirect, url_for

from .event_manager import check_and_apply_event
from .devices import check_is_registered

from ..models import db, Registration, EventClass

from datetime import datetime

mod_participants_view = Blueprint('mod_participants', __name__)

@mod_participants_view.route('/')
@check_and_apply_event
@check_is_registered
def index():
    if not g.device.event_role.may_use_participants:
        flash('Sie haben keine Berechtigung, hierauf zuzugreifen.', 'danger')
        return redirect(url_for('devices.index', event=g.event.slug))
    
    class_filter = None
    filtered_class = None
    status_filter = request.values.get('status_filter', None)
    name_filter = request.values.get('name_filter', None)
    externalid_filter = request.values.get('externalid_filter', None)
    club_filter = request.values.get('club_filter', None)
    order_by = request.values.get('order_by', None)

    if request.values.get('class_filter', None):
        if request.values['class_filter'] not in ['pending', 'weighing_in', 'weighed_in', 'fighting', 'completed']:
            filtered_class = EventClass.query.filter_by(id=request.values['class_filter']).one_or_404()
            class_filter = 'single'
        else:
            class_filter = request.values['class_filter']

    filtered = filtered_class is not None or status_filter is not None or name_filter is not None or club_filter is not None or externalid_filter is not None
    query = Registration.filter(g.event, class_filter=class_filter, event_class=filtered_class,
                                status=status_filter, name=name_filter, club=club_filter, order_by=order_by,
                                external_id=externalid_filter)

    return render_template("mod_participants/index.html", filtered=filtered, class_filter=class_filter,
                           filtered_class=filtered_class, status_filter=status_filter, name_filter=name_filter,
                           club_filter=club_filter, externalid_filter=externalid_filter, order_by=order_by,
                           query=query)



@mod_participants_view.route('/<id>/edit')
@check_and_apply_event
@check_is_registered
def edit(id):
    if not g.device.event_role.may_use_participants:
        flash('Sie haben keine Berechtigung, hierauf zuzugreifen.', 'danger')
        return redirect(url_for('devices.index', event=g.event.slug))

    registration = Registration.query.filter_by(id=id).one_or_404()
    return render_template("mod_participants/edit.html", registration=registration)


@mod_participants_view.route('/<id>/edit', methods=["POST"])
@check_and_apply_event
@check_is_registered
def update(id):
    if not g.device.event_role.may_use_participants:
        flash('Sie haben keine Berechtigung, hierauf zuzugreifen.', 'danger')
        return redirect(url_for('devices.index', event=g.event.slug))

    registration = Registration.query.filter_by(id=id).one_or_404()
    registration.first_name = request.form['first_name']
    registration.last_name = request.form['last_name']
    registration.club = request.form['club']
    registration.contact_details = request.form['contact_details']
    registration.external_id = request.form['external_id']
    registration.suggested_group = request.form['suggested_group']

    registration.confirmed = "confirmed" in request.form
    registration.registered = "registered" in request.form
    registration.weighed_in = "weighed_in" in request.form

    if len(request.form['association']) and request.form['association'] != '-':
        registration.association_id = int(request.form['association'])
    else:
        registration.association_id = None

    if len(request.form['event_class']):
        registration.event_class_id = int(request.form['event_class'])
    else:
        registration.event_class_id = None

    if request.form['verified_weight']:
        registration.verified_weight = int(float(request.form['verified_weight']) * 1000)
    else:
        registration.verified_weight = None

    db.session.commit()
    g.event.log(g.device.title, 'DEBUG', f'TN-Anmeldung {registration.short_name()} wurde bearbeitet.')

    return redirect(url_for('mod_participants.edit', event=g.event.slug, id=registration.id))


@mod_participants_view.route('/new', methods=["GET", "POST"])
@check_and_apply_event
@check_is_registered
def new():
    if not g.device.event_role.may_use_participants:
        flash('Sie haben keine Berechtigung, hierauf zuzugreifen.', 'danger')
        return redirect(url_for('devices.index', event=g.event.slug))

    registration = Registration(event=g.event)

    if request.method == "POST":
        registration.first_name = request.form['first_name']
        registration.last_name = request.form['last_name']
        registration.club = request.form['club']
        registration.contact_details = request.form['contact_details']
        registration.external_id = request.form['external_id']
        registration.suggested_group = request.form['suggested_group']

        registration.confirmed = "confirmed" in request.form
        registration.registered = "registered" in request.form
        registration.weighed_in = "weighed_in" in request.form
        registration.placed = False

        if len(request.form['association']):
            registration.association_id = int(request.form['association'])
        else:
            registration.association_id = None

        if len(request.form['event_class']):
            registration.event_class_id = int(request.form['event_class'])
        else:
            registration.event_class_id = None

        if request.form['verified_weight']:
            registration.verified_weight = int(float(request.form['verified_weight']) * 1000)
        else:
            registration.verified_weight = None

        db.session.add(registration)
        db.session.commit()
        g.event.log(g.device.title, 'DEBUG', f'Neue TN-Anmeldung für {registration.short_name()} angelegt.')

        return redirect(url_for('mod_participants.edit', event=g.event.slug, id=registration.id))

    return render_template("mod_participants/new.html", registration=registration)


@mod_participants_view.route('/print')
@check_and_apply_event
@check_is_registered
def print_all():
    if not g.device.event_role.may_use_participants:
        flash('Sie haben keine Berechtigung, hierauf zuzugreifen.', 'danger')
        return redirect(url_for('devices.index', event=g.event.slug))

    filtered_class = None

    if request.values.get('id', None):
        filtered_class = EventClass.query.filter_by(id=request.values['id']).one_or_404()

    return render_template("event-manager/registrations/print_all.html", filtered_class=filtered_class)


@mod_participants_view.route('/print/cards')
@check_and_apply_event
@check_is_registered
def print_cards():
    if not g.device.event_role.may_use_participants:
        flash('Sie haben keine Berechtigung, hierauf zuzugreifen.', 'danger')
        return redirect(url_for('devices.index', event=g.event.slug))

    filtered_class = None
    filtered_registrations = None

    if request.values.get('id', None):
        filtered_class = EventClass.query.filter_by(id=request.values['id']).one_or_404()
    
    if (queried_registrations := request.values.getlist("registrations")):
        filtered_registrations = map(lambda id: g.event.registrations.filter_by(id=id).one_or_none(),
                                     queried_registrations)

    return render_template("event-manager/registrations/print_cards.html", filtered_class=filtered_class, filtered_registrations=filtered_registrations)


@mod_participants_view.route('/action/<action>', methods=["POST"])
@check_and_apply_event
@check_is_registered
def action(action):
    if not g.device.event_role.may_use_participants:
        flash('Sie haben keine Berechtigung, hierauf zuzugreifen.', 'danger')
        return redirect(url_for('devices.index', event=g.event.slug))

    if (queried_registrations := request.values.getlist("registrations")):
        filtered_registrations = map(lambda id: g.event.registrations.filter_by(id=id).one_or_none(),
                                     queried_registrations)
    else:
        filtered_registrations = g.event.registrations.all()

    relevant_registrations = []
    
    for registration in filtered_registrations:
        if action == "confirm":
            if not registration.confirmed:
                registration.confirmed = True
                relevant_registrations.append(str(registration.id))
        
        elif action == "weigh-in":
            if not registration.verified_weight:
                guessed_weight = registration.guess_weight()

                if guessed_weight:
                    registration.verified_weight = int(guessed_weight * 1000)
                    registration.weighed_in = True

                    if not registration.registered and \
                        g.event.setting('count_weighin_as_registration', False):
                        registration.registered = True
                        registration.registered_at = datetime.now()
                relevant_registrations.append(str(registration.id))

            elif not registration.weighed_in:
                registration.weighed_in = True

                if not registration.registered and \
                    g.event.setting('count_weighin_as_registration', False):
                    registration.registered = True
                    registration.registered_at = datetime.now()

                relevant_registrations.append(str(registration.id))

            else:
                if not registration.registered and \
                    g.event.setting('count_weighin_as_registration', False):
                    registration.registered = True
                    registration.registered_at = datetime.now()
                    relevant_registrations.append(str(registration.id))

    db.session.commit()
    g.event.log(g.device.title, 'DEBUG',
                f'Massenaktion {action} ausgeführt für Registrierungen {", ".join(relevant_registrations)}.')

    if action == "confirm":
        flash("Voranmeldung für die TN wurde bestätigt.", 'success')
    elif action == "weigh-in":
        flash("TN wurden eingewogen wie angemeldet.", 'success')

    return redirect(url_for('event_manager.registrations', event=g.event.slug))