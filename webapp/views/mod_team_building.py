from flask import Blueprint, render_template, flash, g, session, \
    request, redirect, url_for

from datetime import datetime as dt

from .event_manager import check_and_apply_event, check_event_is_in_team_mode
from .devices import check_is_registered
from .mod_placement import provide_classes_query, _get_weight_classes

from ..models import db, TeamRegistration, TeamRow, Team, TeamMember, Registration

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
    registrations = event_class.registrations.filter_by(placed=False)

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

        registrations = registrations.order_by(Registration.verified_weight)

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


@mod_team_building_view.route('/class/<id>/team/<team>/print', methods=['GET'])
@check_and_apply_event
@check_is_registered
@check_event_is_in_team_mode
def print_team(id, team):
    if not g.device.event_role.may_use_placement_tool and not g.device.event_role.may_use_global_list:
        flash('Sie haben keine Berechtigung, hierauf zuzugreifen.', 'danger')
        return redirect(url_for('devices.index', event=g.event.slug))

    event_class = g.event.classes.filter_by(id=id).one_or_404()

    team = event_class.teams.filter_by(id=team).one_or_404()

    return render_template('mod_team_building/print_team.html', team=team)


@mod_team_building_view.route('/class/<id>/team/all/print', methods=['GET'])
@check_and_apply_event
@check_is_registered
@check_event_is_in_team_mode
def print_all_teams(id):
    if not g.device.event_role.may_use_placement_tool and not g.device.event_role.may_use_global_list:
        flash('Sie haben keine Berechtigung, hierauf zuzugreifen.', 'danger')
        return redirect(url_for('devices.index', event=g.event.slug))

    event_class = g.event.classes.filter_by(id=id).one_or_404()

    teams = event_class.teams.all()

    return render_template('mod_team_building/print_all_teams.html', teams=teams, event_class=event_class)


@mod_team_building_view.route('/class/<id>/create_for_teams')
@check_and_apply_event
@check_is_registered
@check_event_is_in_team_mode
def create_for_all_teams(id):
    if not g.device.event_role.may_use_placement_tool:
        flash('Sie haben keine Berechtigung, hierauf zuzugreifen.', 'danger')
        return redirect(url_for('devices.index', event=g.event.slug))

    event_class = g.event.classes.filter_by(id=id).one_or_404()

    if not event_class.begin_placement:
        flash(f"Die Kampfklasse {event_class.title} wurde noch nicht freigegeben.", 'danger')
        return redirect(url_for('mod_team_building.index', event=g.event.slug))
    
    team_registrations = event_class.team_registrations.all()

    teams = []

    for team_registration in team_registrations:
        success, team = _create_for_team_registration(team_registration)

        if success:
            teams.append(team.team_name)

    if len(teams) > 0:
        flash(f"Es wurden erfolgreich {len(teams)} Teams erstellt.", 'success')
        return redirect(url_for('mod_team_building.for_class',
                                event=g.event.slug, id=event_class.id))
    else:
        flash(f"Es konnte kein Team erstellt werden; ggf. wurden die Teams schon erstellt.", 'warning')
        return redirect(url_for('mod_team_building.for_class',
                                event=g.event.slug, id=event_class.id))



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
    
    team_registration = event_class.team_registrations.filter_by(id=registration).one_or_404()

    success, team = _create_for_team_registration(team_registration)

    if success:
        flash(f"Team {team.team_name} wurde erfolgreich erstellt.", 'success')
        return redirect(url_for('mod_team_building.for_class',
                                event=g.event.slug, id=event_class.id, team=team.id))
    else:
        flash(f"Für diese Team-Anmeldung wurde bereits ein Team erstellt.", 'danger')
        return redirect(url_for('mod_team_building.for_class',
                                event=g.event.slug, id=event_class.id))



@mod_team_building_view.route('/class/<id>/team/<team>/include', methods=['GET', 'POST'])
@check_and_apply_event
@check_is_registered
@check_event_is_in_team_mode
def include_to_team(id, team):
    if not g.device.event_role.may_use_placement_tool:
        flash('Sie haben keine Berechtigung, hierauf zuzugreifen.', 'danger')
        return redirect(url_for('devices.index', event=g.event.slug))

    event_class = g.event.classes.filter_by(id=id).one_or_404()

    if not event_class.begin_placement:
        flash(f"Die Kampfklasse {event_class.title} wurde noch nicht freigegeben.", 'danger')
        return redirect(url_for('mod_team_building.index', event=g.event.slug))
    
    team = event_class.teams.filter_by(id=team).one_or_404()

    success = 0
    errors = []

    for incluse in request.values.getlist('include'):
        tr = event_class.registrations.filter_by(id=incluse).one_or_none()

        if tr:
            if tr.team_members.count() > 0:
                continue

            tm = _create_member_for_registration(team, tr)
        
            if tm:
                success += 1
            else:
                errors.append(tr.first_name + ' ' + tr.last_name)
        
        else:
            errors.append(f"TN#{incluse}")

    if success > 0:
        flash(f"Erfolgreich {success} TN zugewiesen.",
              'success')

    if len(errors) > 0:
        flash(f"Fehler sind aufgetreten bei bei der Zuweisung von: " + ', '.join(errors),
              'danger')

    return redirect(url_for('mod_team_building.for_class',
                            event=g.event.slug, id=event_class.id, team=team.id))



@mod_team_building_view.route('/class/<id>/team/<team>/exclude/<member>', methods=['GET', 'POST'])
@check_and_apply_event
@check_is_registered
@check_event_is_in_team_mode
def exclude_from_team(id, team, member):
    if not g.device.event_role.may_use_placement_tool:
        flash('Sie haben keine Berechtigung, hierauf zuzugreifen.', 'danger')
        return redirect(url_for('devices.index', event=g.event.slug))

    event_class = g.event.classes.filter_by(id=id).one_or_404()

    if not event_class.begin_placement:
        flash(f"Die Kampfklasse {event_class.title} wurde noch nicht freigegeben.", 'danger')
        return redirect(url_for('mod_team_building.index', event=g.event.slug))
    
    team = event_class.teams.filter_by(id=team).one_or_404()

    member = team.members.filter_by(id=member).one_or_404()

    if request.method == 'POST':
        member.registration.placed = False
        db.session.delete(member)
        db.session.commit()

        flash(f"TN wurde gelöscht.", 'success')
        return redirect(url_for('mod_team_building.for_class',
                                event=g.event.slug, id=event_class.id, team=team.id))
    
    return render_template('mod_team_building/exclude.html',
                           event_class=event_class, team=team, member=member)


@mod_team_building_view.route('/class/<id>/team/<team>/include_all', methods=['GET', 'POST'])
@check_and_apply_event
@check_is_registered
@check_event_is_in_team_mode
def include_all_of_team(id, team):
    if not g.device.event_role.may_use_placement_tool:
        flash('Sie haben keine Berechtigung, hierauf zuzugreifen.', 'danger')
        return redirect(url_for('devices.index', event=g.event.slug))

    event_class = g.event.classes.filter_by(id=id).one_or_404()

    if not event_class.begin_placement:
        flash(f"Die Kampfklasse {event_class.title} wurde noch nicht freigegeben.", 'danger')
        return redirect(url_for('mod_team_building.index', event=g.event.slug))
    
    team = event_class.teams.filter_by(id=team).one_or_404()

    success, errors = _include_all_of_team(team)

    if success > 0:
        flash(f"Erfolgreich {success} TN zugewiesen.",
              'success')

    if len(errors) > 0:
        flash(f"Fehler sind aufgetreten bei der Zuweisung von: " + ', '.join(errors),
              'danger')

    return redirect(url_for('mod_team_building.for_class',
                            event=g.event.slug, id=event_class.id, team=team.id))


@mod_team_building_view.route('/class/<id>/team/all/include_all', methods=['GET', 'POST'])
@check_and_apply_event
@check_is_registered
@check_event_is_in_team_mode
def include_all_for_all_teams(id):
    if not g.device.event_role.may_use_placement_tool:
        flash('Sie haben keine Berechtigung, hierauf zuzugreifen.', 'danger')
        return redirect(url_for('devices.index', event=g.event.slug))

    event_class = g.event.classes.filter_by(id=id).one_or_404()

    if not event_class.begin_placement:
        flash(f"Die Kampfklasse {event_class.title} wurde noch nicht freigegeben.", 'danger')
        return redirect(url_for('mod_team_building.index', event=g.event.slug))
    
    teams = event_class.teams.all()

    success, errors = 0, []

    for team in teams:
        suc, err = _include_all_of_team(team)
        success += success
        errors += errors

    if success > 0:
        flash(f"Erfolgreich {success} TN zugewiesen.",
              'success')

    if len(errors) > 0:
        flash(f"Fehler sind aufgetreten bei der Zuweisung von: " + ', '.join(errors),
              'danger')

    return redirect(url_for('mod_team_building.for_class',
                            event=g.event.slug, id=event_class.id))


@mod_team_building_view.route('/class/<id>/delete_all', methods=['GET', 'POST'])
@check_and_apply_event
@check_is_registered
def delete_all_for_class(id):
    if not g.device.event_role.may_use_placement_tool:
        flash('Sie haben keine Berechtigung, hierauf zuzugreifen.', 'danger')
        return redirect(url_for('devices.index', event=g.event.slug))

    event_class = g.event.classes.filter_by(id=id).one_or_404()

    if request.method == 'POST':
        if 'confirm' in request.form:
            # TODO: reset team_group progress

            team_counter = team_member_counter = team_row_counter = registration_counter = 0
            for team in event_class.teams:
                for member in team.members:
                    db.session.delete(member)
                    team_member_counter += 1

                db.session.delete(team)
                team_counter += 1
            
            for registration in event_class.registrations:
                registration.placed = False
                registration.placed_at = None
                registration_counter += 1

            for row in event_class.team_rows:
                db.session.delete(row)
                team_row_counter += 1

            db.session.commit()
                    
            g.event.log(g.device.title, 'DANGER', f'Für die Kampklasse {event_class.title} wurde die Team-Einteilung zurückgesetzt: {team_counter} Teams, {team_member_counter} TN wurden gelöscht, {team_row_counter} Zeilen wurden entfernt und {registration_counter} TN-Registrierungen wurden zurückgesetzt')
            flash(f'Für die Kampklasse {event_class.title} wurde die Team-Einteilung zurückgesetzt: {team_counter} Teams, {team_member_counter} TN wurden gelöscht, {team_row_counter} Zeilen wurden entfernt und {registration_counter} TN-Registrierungen wurden zurückgesetzt', 'success')

            return redirect(url_for('mod_team_building.for_class', event=g.event.slug, id=event_class.id))
        else:
            flash(f"Fehler: Sie müssen die Checkbox zur Bestätigung betätigen", 'danger')

    return render_template("mod_team_building/delete_all_for_class.html", event_class=event_class)


def _create_member_for_registration(team, registration, row=None):
    tm = TeamMember(event=team.event, team=team, registration=registration)

    tm.full_name = registration.first_name + ' ' + registration.last_name
    tm.association_name = registration.club
    tm.removed = False
    tm.disqualified = False
    tm.removal_cause = None
    tm.last_fight_at = None

    if row is not None:
        tm.row = row
    
    else:
        actual_weight = registration.verified_weight

        applicable_rows = team.event_class.team_rows.filter(
            TeamRow.min_weight.is_(None) | (TeamRow.min_weight < actual_weight),
            TeamRow.max_weight.is_(None) | (TeamRow.max_weight >= actual_weight)
        )

        if applicable_rows.count() == 1:
            tm.row = applicable_rows.first()
        
        else:
            return None
    
    db.session.add(tm)

    registration.placed = True

    db.session.commit()

    return tm


def _include_all_of_team(team):
    event_class = team.event_class

    success = 0
    errors = []
    team_registration = team.team_registration

    if not team_registration:
        flash(f"Kann nicht TN von Team {team.team_name} zuweisen, da keine Anmeldedaten für dieses "
              f"Team angelegt wurden.")

        return redirect(url_for('mod_team_building.for_class',
                                event=g.event.slug, id=event_class.id, team=team.id))

    for tr in team_registration.members:
        if tr.team_members.count() > 0:
            continue

        tm = _create_member_for_registration(team, tr)
    
        if tm:
            success += 1
        else:
            errors.append(tr.first_name + ' ' + tr.last_name)

    return success, errors


def _create_for_team_registration(team_registration):
    if team_registration.teams.count() != 0:
        return False, None
    
    team = Team(event=g.event, event_class=team_registration.event_class)
    team.team_name = team_registration.team_name
    team.team_registration = team_registration

    team.manually_placed = False
    team.removed = False
    team.disqualified = False

    db.session.add(team)
    db.session.commit()

    return True, team