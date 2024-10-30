from flask import Blueprint, render_template, flash, g, session, \
    request, redirect, url_for

from datetime import datetime as dt

from .event_manager import check_and_apply_event, check_event_is_in_team_mode
from .devices import check_is_registered
from .mod_placement import provide_classes_query, _get_weight_classes

from ..models import db, TeamRegistration, TeamRow, Team

mod_team_building_view = Blueprint('mod_team_building', __name__)

mod_team_building_view.context_processor(provide_classes_query)

@mod_team_building_view.route('/')
@check_and_apply_event
@check_is_registered
@check_event_is_in_team_mode
def index():
    if not g.device.event_role.may_use_placement_tool:
        flash('Sie haben keine Berechtigung, hierauf zuzugreifen.', 'danger')
        return redirect(url_for('devices.index', event=g.event.slug))

    return render_template("mod_team_building/index.html")


@mod_team_building_view.route('/class/<id>')
@check_and_apply_event
@check_is_registered
@check_event_is_in_team_mode
def for_class(id):
    if not g.device.event_role.may_use_placement_tool:
        flash('Sie haben keine Berechtigung, hierauf zuzugreifen.', 'danger')
        return redirect(url_for('devices.index', event=g.event.slug))

    event_class = g.event.classes.filter_by(id=id).one_or_404()

    if not event_class.begin_placement:
        flash(f"Die Kampfklasse {event_class.title} wurde noch nicht freigegeben.", 'danger')
        return redirect(url_for('mod_team_building.index', event=g.event.slug))
    
    if not event_class.team_rows.count() > 0 and not event_class.use_proximity_weight_mode:
        return redirect(url_for('mod_team_building.initialize', event=g.event.slug, id=event_class.id))
    
    current_team = None
    registration_filter = None
    registrations = event_class.registrations

    if 'team' in request.values:
        current_team = event_class.teams.filter_by(id=request.values['team']).one_or_404()

        if 'registration_filter' in request.values:
            registration_filter = request.values['registration_filter']

        elif current_team.team_registration:
            registration_filter = current_team.team_registration.id
        
        else:
            registration_filter = 'all'

        if registration_filter == 'all':
            pass # registrations are already correctly filtered

        elif registration_filter == 'none':
            registrations = registrations.filter_by(team_registration_id=None)

        else:
            registration_filter = int(registration_filter)
            registrations = registrations.filter_by(team_registration_id=registration_filter)

    return render_template("mod_team_building/for_class.html", event_class=event_class, current_team=current_team, registration_filter=registration_filter, registrations=registrations)


@mod_team_building_view.route('/class/<id>/initialize', methods=['GET', 'POST'])
@check_and_apply_event
@check_is_registered
@check_event_is_in_team_mode
def initialize(id):
    if not g.device.event_role.may_use_placement_tool:
        flash('Sie haben keine Berechtigung, hierauf zuzugreifen.', 'danger')
        return redirect(url_for('devices.index', event=g.event.slug))

    event_class = g.event.classes.filter_by(id=id).one_or_404()

    if not event_class.begin_placement:
        flash(f"Die Kampfklasse {event_class.title} wurde noch nicht freigegeben.", 'danger')
        return redirect(url_for('mod_team_building.index', event=g.event.slug))
    
    if event_class.team_rows.count() > 0 or event_class.use_proximity_weight_mode:
        return redirect(url_for('mod_team_building.for_class', event=g.event.slug, id=event_class.id))

    weight_classes = _get_weight_classes(event_class)

    if request.method == 'POST':
        
        if request.form['mode'] == 'predefined':
            lower_row = None
            match_order_key = 0
            for cl in weight_classes:
                lower_row = TeamRow(
                    event = g.event,
                    event_class = event_class,
                    lower_row = lower_row,

                    title = event_class.short_title + ' ' + cl[0],
                    match_order_key = match_order_key,

                    created_manually = False,
                    assign_by_logic = True,
                    min_weight = cl[1][0] * 1000 if cl[1][0] else None,
                    max_weight = cl[1][1] * 1000 if cl[1][1] else None,
                )
                db.session.add(lower_row)
                match_order_key += 1

        elif request.form['mode'] == 'manual':
            db.session.add(TeamRow(
                event = g.event,
                event_class = event_class,
                lower_row = None,

                title = event_class.short_title + ' ' + request.form['name'],
                match_order_key = 0,

                created_manually = True,
                assign_by_logic = 'assign_by_logic' in request.form,
                min_weight = int(float(request.form['min_weight']) * 1000) if request.form['min_weight'] else None,
                max_weight = int(float(request.form['max_weight']) * 1000) if request.form['max_weight'] else None
            ))
            
        db.session.commit()

        return redirect(url_for('mod_team_building.for_class', event=g.event.slug, id=event_class.id))

    return render_template("mod_team_building/initialize.html",
                               event_class=event_class, weight_classes=weight_classes)


@mod_team_building_view.route('/class/<id>/create_for_team/<registration>')
@check_and_apply_event
@check_is_registered
@check_event_is_in_team_mode
def create_for_team(id, registration):
    if not g.device.event_role.may_use_placement_tool:
        flash('Sie haben keine Berechtigung, hierauf zuzugreifen.', 'danger')
        return redirect(url_for('devices.index', event=g.event.slug))

    event_class = g.event.classes.filter_by(id=id).one_or_404()

    if not event_class.begin_placement:
        flash(f"Die Kampfklasse {event_class.title} wurde noch nicht freigegeben.", 'danger')
        return redirect(url_for('mod_team_building.index', event=g.event.slug))
    
    team_registration = TeamRegistration.query.filter_by(id=registration).one_or_404()

    if team_registration.teams.count() != 0:
        flash(f"Für diese Team-Anmeldung wurde bereits ein Team erstellt.", 'danger')
        return redirect(url_for('mod_team_building.for_class',
                                event=g.event.slug, id=event_class))
    
    team = Team(event=g.event, event_class=event_class)
    team.team_name = team_registration.team_name
    team.team_registration = team_registration

    team.manually_placed = False
    team.removed = False
    team.disqualified = False

    db.session.add(team)
    db.session.commit()

    flash(f"Team {team.team_name} wurde erfolgreich erstellt.", 'success')
    return redirect(url_for('mod_team_building.for_class',
                            event=g.event.slug, id=event_class.id, team=team.id))