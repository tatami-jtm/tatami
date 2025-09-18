from flask import Blueprint, render_template, flash, g, session, \
    request, redirect, url_for, abort

from datetime import datetime as dt

import random

from .event_manager import check_and_apply_event
from .devices import check_is_registered

from ..models import db, EventClass, Group, ListSystem, Participant

from .. import helpers

mod_placement_view = Blueprint('mod_placement', __name__)

@mod_placement_view.context_processor
def provide_classes_query():
    return {
        "classes_query": g.event.classes.order_by(EventClass.begin_fighting,
                                                  EventClass.begin_placement.desc(),
                                                  EventClass.title)
    }

@mod_placement_view.route('/')
@check_and_apply_event
@check_is_registered
def index():
    if not g.device.event_role.may_use_placement_tool:
        flash('Sie haben keine Berechtigung, hierauf zuzugreifen.', 'danger')
        return redirect(url_for('devices.index', event=g.event.slug))

    return render_template("mod_placement/index.html")


@mod_placement_view.route('/class/<id>')
@check_and_apply_event
@check_is_registered
def for_class(id):
    if not g.device.event_role.may_use_placement_tool:
        flash('Sie haben keine Berechtigung, hierauf zuzugreifen.', 'danger')
        return redirect(url_for('devices.index', event=g.event.slug))

    event_class = g.event.classes.filter_by(id=id).one_or_404()

    if not event_class.begin_placement:
        flash(f"Die Kampfklasse {event_class.title} wurde noch nicht freigegeben.", 'danger')
        return redirect(url_for('mod_placement.index', event=g.event.slug))

    registrations = event_class.registrations.filter_by(confirmed=True, registered=True, weighed_in=True, placed=False).order_by('verified_weight')
    groups = event_class.groups
    current_group = None

    if 'group' in request.values:
        current_group = groups.filter_by(id=request.values['group']).one_or_404()

    return render_template("mod_placement/for_class.html", event_class=event_class, registrations=registrations, groups=groups, proximity=event_class.use_proximity_weight_mode, current_group=current_group)


@mod_placement_view.route('/class/<id>/group/new', methods=['GET', 'POST'])
@check_and_apply_event
@check_is_registered
def add_group(id):
    if not g.device.event_role.may_use_placement_tool:
        flash('Sie haben keine Berechtigung, hierauf zuzugreifen.', 'danger')
        return redirect(url_for('devices.index', event=g.event.slug))

    event_class = g.event.classes.filter_by(id=id).one_or_404()
    group = Group(created_manually=True, event=g.event, event_class=event_class,
                  assigned=False, marked_ready=False, opened=False, completed=False)

    if request.method == 'POST':
        group.title = event_class.short_title + ' ' + request.form['name']
        group.assign_by_logic = 'assign_by_logic' in request.form
        group.min_weight = int(float(request.form['min_weight']) * 1000) if request.form['min_weight'] else None
        group.max_weight = int(float(request.form['max_weight']) * 1000) if request.form['max_weight'] else None

        if request.form['system']:
            system = ListSystem.all_enabled().filter_by(id=request.form['system']).one_or_none()
            group.system_id = system.id
            group.list_break_count = system.break_count
        else:
            group.system_id = None

        db.session.add(group)
        db.session.commit()
        g.event.log(g.device.title, 'DEBUG', f'Neue Gruppe {group.title} erstellt.')

        flash(f"Neue Gruppe {group.title} erfolgreich erstellt.", 'success')

        return redirect(url_for('mod_placement.for_class', event=g.event.slug, id=event_class.id, group=group.id))

    return render_template("mod_placement/group/add.html", event_class=event_class, group=group, systems=ListSystem.all_enabled())


@mod_placement_view.route('/class/<id>/group/edit/<group_id>', methods=['GET', 'POST'])
@check_and_apply_event
@check_is_registered
def edit_group(id, group_id):
    if not g.device.event_role.may_use_placement_tool:
        flash('Sie haben keine Berechtigung, hierauf zuzugreifen.', 'danger')
        return redirect(url_for('devices.index', event=g.event.slug))

    event_class = g.event.classes.filter_by(id=id).one_or_404()
    group = event_class.groups.filter_by(id=group_id).one_or_404()

    if request.method == 'POST':
        group.title = event_class.short_title + ' ' + request.form['name']
        group.assign_by_logic = 'assign_by_logic' in request.form
        group.min_weight = int(float(request.form['min_weight']) * 1000) if request.form['min_weight'] else None
        group.max_weight = int(float(request.form['max_weight']) * 1000) if request.form['max_weight'] else None

        if request.form['system']:
            group.system_id = int(request.form['system'])
            group.list_break_count = group.list_system().break_count
        else:
            group.system_id = None

        db.session.commit()
        g.event.log(g.device.title, 'DEBUG', f'Gruppe {group.title} bearbeitet.')

        flash(f"Gruppe {group.title} erfolgreich aktualisiert.", 'success')

        return redirect(url_for('mod_placement.for_class', event=g.event.slug, id=event_class.id, group=group.id))

    return render_template("mod_placement/group/edit.html", event_class=event_class, group=group, systems=ListSystem.all_enabled())


@mod_placement_view.route('/class/<id>/group/delete/<group_id>', methods=['GET', 'POST'])
@check_and_apply_event
@check_is_registered
def delete_group(id, group_id):
    if not g.device.event_role.may_use_placement_tool:
        flash('Sie haben keine Berechtigung, hierauf zuzugreifen.', 'danger')
        return redirect(url_for('devices.index', event=g.event.slug))

    event_class = g.event.classes.filter_by(id=id).one_or_404()
    group = event_class.groups.filter_by(id=group_id).one_or_404()

    if request.method == 'POST':
        if not group.participants.count() == 0:
            abort(400)

        db.session.delete(group)
        db.session.commit()
        g.event.log(g.device.title, 'DEBUG', f'Gruppe {group.title} gelöscht.')

        flash(f"Gruppe {group.title} erfolgreich gelöscht.", 'success')

        return redirect(url_for('mod_placement.for_class', event=g.event.slug, id=event_class.id))

    return render_template("mod_placement/group/delete.html", event_class=event_class, group=group)


@mod_placement_view.route('/class/<id>/assign', methods=['GET', 'POST'])
@check_and_apply_event
@check_is_registered
def assign(id):
    if not g.device.event_role.may_use_placement_tool:
        flash('Sie haben keine Berechtigung, hierauf zuzugreifen.', 'danger')
        return redirect(url_for('devices.index', event=g.event.slug))

    event_class = g.event.classes.filter_by(id=id).one_or_404()

    if request.method == 'POST':
        if 'group' in request.form and 'participant' in request.form and (request.form['participant'] == 'custom' or 'registration' in request.form):
            participant = Participant(event=g.event)
            participant.placement_index = None
            participant.manually_placed = None
            participant.final_placement = None
            participant.final_points = None
            participant.final_score = None
            participant.removed = False
            participant.disqualified = False
            participant.removal_cause = None

            if request.form['participant'] == 'registration':
                registration = event_class.registrations.filter_by(id=request.form['registration']).one()
                participant.full_name = f"{registration.first_name} {registration.last_name}"

                if len(participant.full_name) > 21:
                    participant.full_name = f"{registration.first_name[0]}. {registration.last_name}"

                participant.registration = registration

                if g.event.setting('use_association_instead_of_club', False) and registration.association:
                    participant.association_name = registration.association.name
                else:
                    participant.association_name = registration.club

                registration.placed = True
                registration.placed_at = registration.placed_at or dt.now()

            elif request.form['participant'] == 'custom':
                participant.full_name = request.form['custom-full_name']
                participant.association_name = request.form['custom-association']
                participant.registration = None
            
            group = event_class.groups.filter_by(id=request.form['group']).one()
            participant.group = group

            db.session.add(participant)
            db.session.commit()

            if request.form['participant'] == 'registration':
                g.event.log(g.device.title, 'DEBUG', f'Angemeldeter TN {participant.full_name} wurde Gruppe {group.title} zugewiesen.')
            else:
                g.event.log(g.device.title, 'DEBUG', f'TN {participant.full_name} wurde erstellt und Gruppe {group.title} zugewiesen.')

            return redirect(url_for('mod_placement.for_class', event=g.event.slug, id=event_class.id, group=group.id))
        
        flash("Es wurden nicht alle notwendigen Felder ausgefüllt.", 'danger')

    registrations = event_class.registrations.filter_by(confirmed=True, registered=True, weighed_in=True).order_by('last_name', 'first_name', 'verified_weight')
    
    group = event_class.groups.filter_by(id=request.values.get('group', None)).one_or_none()
    registration = g.event.registrations.filter_by(id=request.values.get('registration', None)).one_or_none()

    return render_template("mod_placement/registration/assign.html", event_class=event_class, group=group, registration=registration, registrations=registrations)


@mod_placement_view.route('/class/<id>/unassign/<participant_id>', methods=['GET', 'POST'])
@check_and_apply_event
@check_is_registered
def unassign(id, participant_id):
    if not g.device.event_role.may_use_placement_tool:
        flash('Sie haben keine Berechtigung, hierauf zuzugreifen.', 'danger')
        return redirect(url_for('devices.index', event=g.event.slug))

    event_class = g.event.classes.filter_by(id=id).one_or_404()
    participant = g.event.participants.filter_by(id=participant_id).one_or_404()
    group = participant.group
    registration = participant.registration

    if request.method == 'POST':
        if registration and registration.participants.count() == 1:
            registration.placed = False
            registration.placed_at = None

        db.session.delete(participant)
        db.session.commit()
        g.event.log(g.device.title, 'DEBUG', f'TN {participant.full_name} ist nicht der Gruppe {group.title} mehr zugewiesen und ggf. gelöscht.')

        return redirect(url_for('mod_placement.for_class', event=g.event.slug, id=event_class.id, group=group.id))

    return render_template("mod_placement/registration/unassign.html", event_class=event_class, participant=participant, registration=registration)


@mod_placement_view.route('/class/<id>/assign/predefined', methods=['GET', 'POST'])
@check_and_apply_event
@check_is_registered
def assign_all_predefined(id):
    if not g.device.event_role.may_use_placement_tool:
        flash('Sie haben keine Berechtigung, hierauf zuzugreifen.', 'danger')
        return redirect(url_for('devices.index', event=g.event.slug))

    event_class = g.event.classes.filter_by(id=id).one_or_404()
    weight_classes = _get_weight_classes(event_class)

    if request.method == 'POST':
        groups_created = participants_created = 0

        registrations = event_class.registrations.filter_by(confirmed=True, registered=True, weighed_in=True, placed=False)

        if request.form['create_new'] == 'yes':
            for cl in weight_classes:
                group = Group(created_manually=False, event=g.event, event_class=event_class,
                              assigned=False, marked_ready=False, opened=False, completed=False)
                group.title = event_class.short_title + ' ' + cl[0]
                group.assign_by_logic = True
                group.min_weight = cl[1][0] * 1000 if cl[1][0] else None
                group.max_weight = cl[1][1] * 1000 if cl[1][1] else None
                group.system_id = None

                db.session.add(group)
                g.event.log(g.device.title, 'DEBUG', f'Neue Gruppe {group.title} erstellt.')
                groups_created += 1


        for registration in registrations:
            actual_weight = registration.verified_weight - int(float(request.form['tolerance']) * 1000)
            applicable_groups = event_class.groups.filter(
                Group.min_weight.is_(None) | (Group.min_weight < actual_weight),
                Group.max_weight.is_(None) | (Group.max_weight >= actual_weight)
            )

            if request.form['use_old'] != 'yes':
                applicable_groups = applicable_groups.filter_by(created_manually=False)

            if not applicable_groups.count():
                if request.form['create_new'] != 'if-required':
                    continue

                for cl in weight_classes:
                    if not cl[1][0] or cl[1][0] * 1000 >= actual_weight or not cl[1][1] or cl[1][1] * 1000 < actual_weight:
                        continue

                    group = Group(created_manually=False, event=g.event, event_class=event_class,
                                  assigned=False, marked_ready=False, opened=False, completed=False)
                    group.title = event_class.short_title + ' ' + cl[0]
                    group.assign_by_logic = True
                    group.min_weight = cl[1][0] * 1000 if cl[1][0] else None
                    group.max_weight = cl[1][1] * 1000 if cl[1][1] else None
                    group.system_id = None

                    db.session.add(group)
                    g.event.log(g.device.title, 'DEBUG', f'Neue Gruppe {group.title} erstellt.')
                    groups_created += 1
            
            applicable_groups = applicable_groups.all()

            for ag in applicable_groups:
                participant = Participant(event=g.event, group=ag)
                participant.placement_index = None
                participant.manually_placed = None
                participant.final_placement = None
                participant.final_points = None
                participant.final_score = None
                participant.removed = False
                participant.disqualified = False
                participant.removal_cause = None
    
                participant.full_name = f"{registration.first_name} {registration.last_name}"

                if len(participant.full_name) > 21:
                    participant.full_name = f"{registration.first_name[0]}. {registration.last_name}"

                participant.registration = registration

                if g.event.setting('use_association_instead_of_club', False) and registration.association:
                    participant.association_name = registration.association.name
                else:
                    participant.association_name = registration.club

                registration.placed = True
                registration.placed_at = registration.placed_at or dt.now()

                db.session.add(participant)
                g.event.log(g.device.title, 'DEBUG', f'Angemeldeter TN {participant.full_name} wurde Gruppe {ag.title} zugewiesen.')
                participants_created += 1

        db.session.commit()
        g.event.log(g.device.title, 'DEBUG', f'Verbleibende TN wurden zugewiesen. Erstellt wurden {groups_created} Gruppe(n) und {participants_created} TN.')

        flash(f"Verbleibende TN erfolgreich zugewiesen. Erstellt wurden {groups_created} Gruppe(n) und {participants_created} TN.", 'success')

        return redirect(url_for('mod_placement.for_class', event=g.event.slug, id=event_class.id))

    defaults_to_all_new_classes = event_class.groups.filter_by(created_manually=False).count() == 0

    return render_template("mod_placement/registration/assign_all-predefined.html", event_class=event_class, weight_classes=weight_classes, defaults_to_all_new_classes=defaults_to_all_new_classes)


@mod_placement_view.route('/class/<id>/assign/proximity', methods=['GET', 'POST'])
@check_and_apply_event
@check_is_registered
def assign_all_proximity(id):
    if not g.device.event_role.may_use_placement_tool:
        flash('Sie haben keine Berechtigung, hierauf zuzugreifen.', 'danger')
        return redirect(url_for('devices.index', event=g.event.slug))

    event_class = g.event.classes.filter_by(id=id).one_or_404()
    registrations = event_class.registrations.filter_by(confirmed=True, registered=True, weighed_in=True, placed=False).order_by('verified_weight')

    if request.method == 'POST':
        segmentation = list(map(int, request.values.getlist('before')))
        allowed_registrations = list(map(int, request.values.getlist('allow')))
        group = None
        current_initial = None
        groups_created = 0
        participants_created = 0

        for registration in registrations.all():
            if not group or (registration.id in segmentation and group.participants.count() > 0):
                current_initial = registration

                group = Group(created_manually=False, event=g.event, event_class=event_class,
                              assigned=False, marked_ready=False, opened=False, completed=False)
                group.assign_by_logic = True
                group.min_weight = current_initial.verified_weight
                group.system_id = None

                db.session.add(group)
                g.event.log(g.device.title, 'DEBUG', f'Neue Gruppe {group.title} erstellt.')
                groups_created += 1

            if registration.id not in allowed_registrations:
                continue

            group.max_weight = registration.verified_weight
            group.title = f"{event_class.short_title} -{group.max_weight / 1000}kg"

            participant = Participant(event=g.event, group=group)
            participant.placement_index = None
            participant.manually_placed = None
            participant.final_placement = None
            participant.final_points = None
            participant.final_score = None
            participant.removed = False
            participant.disqualified = False
            participant.removal_cause = None

            participant.full_name = f"{registration.first_name} {registration.last_name}"

            if len(participant.full_name) > 21:
                participant.full_name = f"{registration.first_name[0]}. {registration.last_name}"

            participant.registration = registration

            if g.event.setting('use_association_instead_of_club', False) and registration.association:
                participant.association_name = registration.association.name
            else:
                participant.association_name = registration.club

            registration.placed = True
            registration.placed_at = registration.placed_at or dt.now()

            db.session.add(participant)
            g.event.log(g.device.title, 'DEBUG', f'Angemeldeter TN {participant.full_name} wurde Gruppe {group.title} zugewiesen.')
            participants_created += 1

        db.session.commit()

        g.event.log(g.device.title, 'DEBUG', f'Verbleibende TN wurden zugewiesen. Erstellt wurden {groups_created} Gruppe(n) und {participants_created} TN.')
        flash(f"Verbleibende TN erfolgreich zugewiesen. Erstellt wurden {groups_created} Gruppe(n) und {participants_created} TN.", 'success')

        return redirect(url_for('mod_placement.for_class', event=g.event.slug, id=event_class.id))
    
    else:
        default_segmentation = {}
        max_proximity = event_class.default_maximal_proximity
        use_percentage = event_class.proximity_uses_percentage_instead_of_absolute
        max_size = event_class.default_maximal_size or 0
        max_count = event_class.default_maximal_group_count or 0

        proximity = 'count' if event_class.proximity_prefer_group_count_over_proximity else 'size'

        if use_percentage:
            delta_match_func = (lambda w1, w2, max_delta: w2 * (1 + max_delta/100) >= w1)
        
        else:
            delta_match_func = (lambda w1, w2, max_delta: w1 - w2 <= max_delta / 1000)
        

        grouping = helpers.group_by_proximity(registrations.all(),
                                              max_proximity, max_size, max_count, proximity,
                                              delta_match_func=delta_match_func,
                                              item_weight_func=lambda reg: reg.verified_weight / 1000)

        group_count = len(grouping)
        for group in grouping:
            default_segmentation[group[0].id] = True

            for item in group[1:]:
                default_segmentation[item.id] = False
        

        return render_template("mod_placement/registration/assign_all-proximity.html", event_class=event_class,
                               registrations=registrations, default_segmentation=default_segmentation, group_count=group_count)


@mod_placement_view.route('/class/<id>/participant/<participant_id>/place', methods=['GET', 'POST'])
@check_and_apply_event
@check_is_registered
def place(id, participant_id):
    if not g.device.event_role.may_use_placement_tool:
        flash('Sie haben keine Berechtigung, hierauf zuzugreifen.', 'danger')
        return redirect(url_for('devices.index', event=g.event.slug))

    event_class = g.event.classes.filter_by(id=id).one_or_404()
    participant = g.event.participants.filter_by(id=participant_id).one_or_404()
    group = participant.group
    list_system = group.list_system()

    if not list_system:
        flash("Setzen in dieser Gruppe nicht möglich, da noch kein Listensystem zugewiesen ist.", 'danger')

        return redirect(url_for('mod_placement.for_class', event=g.event.slug, id=event_class.id, group=group.id))

    if request.method == 'POST':
        participant.placement_index = int(request.values['position'])
        participant.manually_placed = True

        db.session.commit()
        g.event.log(g.device.title, 'DEBUG', f'TN {participant.full_name} an Position #{participant.placement_index + 1} gesetzt.')

        return redirect(url_for('mod_placement.for_class', event=g.event.slug, id=event_class.id, group=group.id))

    return render_template("mod_placement/participant/place.html", event_class=event_class, group=group, participant=participant, list_system=list_system)


@mod_placement_view.route('/class/<id>/participant/<participant_id>/unplace', methods=['GET', 'POST'])
@check_and_apply_event
@check_is_registered
def unplace(id, participant_id):
    if not g.device.event_role.may_use_placement_tool:
        flash('Sie haben keine Berechtigung, hierauf zuzugreifen.', 'danger')
        return redirect(url_for('devices.index', event=g.event.slug))

    event_class = g.event.classes.filter_by(id=id).one_or_404()
    participant = g.event.participants.filter_by(id=participant_id).one_or_404()
    group = participant.group

    participant.placement_index = None
    participant.manually_placed = False

    db.session.commit()

    g.event.log(g.device.title, 'DEBUG', f'TN {participant.full_name} abgesetzt.')

    return redirect(url_for('mod_placement.for_class', event=g.event.slug, id=event_class.id, group=group.id))


@mod_placement_view.route('/class/<id>/group/<group_id>/switch_placements', methods=['GET', 'POST'])
@check_and_apply_event
@check_is_registered
def switch_placements(id, group_id):
    if not g.device.event_role.may_use_placement_tool:
        flash('Sie haben keine Berechtigung, hierauf zuzugreifen.', 'danger')
        return redirect(url_for('devices.index', event=g.event.slug))

    event_class = g.event.classes.filter_by(id=id).one_or_404()
    group = event_class.groups.filter_by(id=group_id).one_or_404()
    list_system = group.list_system()

    if not list_system:
        flash("Setzen in dieser Gruppe nicht möglich, da noch kein Listensystem zugewiesen ist.", 'danger')

        return redirect(url_for('mod_placement.for_class', event=g.event.slug, id=event_class.id, group=group.id))

    if request.method == 'POST':
        positions = request.form.getlist('position')
        if len(positions) == 2:
            first_participant = group.participants.filter_by(placement_index=positions[0]).first()
            second_participant = group.participants.filter_by(placement_index=positions[1]).first()

            if first_participant:
                first_participant.placement_index = positions[1]
                first_participant.manually_placed = True
            
            if second_participant:
                second_participant.placement_index = positions[0]
                second_participant.manually_placed = True
            
            db.session.commit()

            if "stay-on-page" not in request.values:
                return redirect(url_for('mod_placement.for_class', event=g.event.slug, id=event_class.id,
                                        group=group.id))

        else:
            flash("Wählen Sie genau zwei Positionen aus, die vertauscht werden sollen", 'danger')

    return render_template("mod_placement/participant/switch_placement.html", event_class=event_class, group=group, list_system=list_system)


@mod_placement_view.route('/class/<id>/group/<group_id>/place_all', methods=['GET', 'POST'])
@check_and_apply_event
@check_is_registered
def place_all(id, group_id):
    if not g.device.event_role.may_use_placement_tool:
        flash('Sie haben keine Berechtigung, hierauf zuzugreifen.', 'danger')
        return redirect(url_for('devices.index', event=g.event.slug))

    event_class = g.event.classes.filter_by(id=id).one_or_404()
    group = g.event.groups.filter_by(id=group_id).one_or_404()
    list_system = group.list_system()

    if not list_system:
        flash("Setzen in dieser Gruppe nicht möglich, da noch kein Listensystem zugewiesen ist.", 'danger')

        return redirect(url_for('mod_placement.for_class', event=g.event.slug, id=event_class.id, group=group.id))

    if request.method == 'POST':
        _randomly_place_group(group, method=request.form.get('method', 'random'))
        g.event.log(g.device.title, 'DEBUG', f'Gruppe {group.title} gelost.')
        flash(f"Gruppe {group.title} erfolgreich gelost.", 'success')

        return redirect(url_for('mod_placement.for_class', event=g.event.slug, id=event_class.id, group=group.id))

    return render_template("mod_placement/participant/place_all.html", event_class=event_class, group=group, list_system=list_system)


@mod_placement_view.route('/class/<id>/place_for_all_groups', methods=['GET', 'POST'])
@check_and_apply_event
@check_is_registered
def place_for_all_groups(id):
    if not g.device.event_role.may_use_placement_tool:
        flash('Sie haben keine Berechtigung, hierauf zuzugreifen.', 'danger')
        return redirect(url_for('devices.index', event=g.event.slug))

    event_class = g.event.classes.filter_by(id=id).one_or_404()
    groups = event_class.groups

    unresolved_for_error_of_no_system = []
    unresolved_for_no_participants = []
    unresolved_for_already_resolved = []
    resolved_successfully = []

    if request.method == 'POST':
        for group in groups:
            list_system = group.list_system()

            if group.participants.count() == 0:
                unresolved_for_no_participants.append(group.title)
            elif not list_system:
                unresolved_for_error_of_no_system.append(group.title)
            
            elif group.all_participants_have_been_placed():
                unresolved_for_already_resolved.append(group.title)

            else:
                _randomly_place_group(group, method=request.form.get('method', 'random'))
                resolved_successfully.append(group.title)

        if len(resolved_successfully):
            g.event.log(g.device.title, 'DEBUG', f"Gruppe(n) {', '.join(resolved_successfully)} wurden gelost.")
            flash(f"Die Gruppe(n) {', '.join(resolved_successfully)} wurden erfolgreich gelost.", 'success')

        if len(unresolved_for_no_participants):
            flash(f"Die Gruppe(n) {', '.join(unresolved_for_no_participants)} wurden nicht gelost, da keine TN zugewiesen sind.", 'info')

        if len(unresolved_for_already_resolved):
            flash(f"Die Gruppe(n) {', '.join(unresolved_for_already_resolved)} wurden nicht gelost, da bereits alle TN gesetzt oder gelost sind.", 'info')

        if len(unresolved_for_error_of_no_system):
            flash(f"Die Gruppe(n) {', '.join(unresolved_for_error_of_no_system)} konnten nicht gelost werden, da kein Listensystem zugewiesen ist.", 'danger')

            

        return redirect(url_for('mod_placement.for_class', event=g.event.slug, id=event_class.id))

    return render_template("mod_placement/participant/place_for_all_groups.html", event_class=event_class, groups=groups)


@mod_placement_view.route('/class/<id>/delete_all', methods=['GET', 'POST'])
@check_and_apply_event
@check_is_registered
def delete_all_for_class(id):
    if not g.device.event_role.may_use_placement_tool:
        flash('Sie haben keine Berechtigung, hierauf zuzugreifen.', 'danger')
        return redirect(url_for('devices.index', event=g.event.slug))

    event_class = g.event.classes.filter_by(id=id).one_or_404()

    if request.method == 'POST':
        if 'confirm' in request.form:
            group_counter = participant_counter = registration_counter = 0
            for group in event_class.groups:
                helpers.reset_list(group)

                for participant in group.participants:
                    db.session.delete(participant)
                    participant_counter += 1

                db.session.delete(group)
                group_counter += 1
            
            for registration in event_class.registrations:
                registration.placed = False
                registration.placed_at = None
                registration_counter += 1

            db.session.commit()
                    
            g.event.log(g.device.title, 'DANGER', f'Für die Kampklasse {event_class.title} wurde die Einteilung zurückgesetzt: {group_counter} Gruppen, {participant_counter} TN wurden gelöscht und {registration_counter} TN-Registrierungen wurden zurückgesetzt')
            flash(f"Für die Kampklasse {event_class.title} wurde die Einteilung zurückgesetzt. {group_counter} Gruppen, {participant_counter} TN wurden gelöscht und {registration_counter} TN-Registrierungen wurden zurückgesetzt.", 'success')

            return redirect(url_for('mod_placement.for_class', event=g.event.slug, id=event_class.id))
        else:
            flash(f"Fehler: Sie müssen die Checkbox zur Bestätigung betätigen", 'danger')

    return render_template("mod_placement/delete_all_for_class.html", event_class=event_class)



@mod_placement_view.route('/class/<id>/refresh', methods=['GET', 'POST'])
@check_and_apply_event
@check_is_registered
def refresh_for_class(id):
    if not g.device.event_role.may_use_placement_tool:
        flash('Sie haben keine Berechtigung, hierauf zuzugreifen.', 'danger')
        return redirect(url_for('devices.index', event=g.event.slug))

    event_class = g.event.classes.filter_by(id=id).one_or_404()

    if request.method == 'POST':
        groups_needing_refreshing = set()
        for group in event_class.groups:
            needs_to_clear_group = False

            for participant in group.participants:
                if participant.registration is None:
                    # This participant was manually added and cannot be refreshed
                    continue

                registration = participant.registration

                # Refresh participant names
                if 'update_names' in request.form:
                    _refresh_participant_name(participant, registration)

                # Check for unfitting group
                if 'update_weight' in request.form:
                    groups_needing_refreshing.update(
                        _refresh_participant_weight(event_class, participant, registration, group)
                    )
        
        # Refresh groups
        for group in event_class.groups:
            if group in groups_needing_refreshing:
                _refresh_group(group)

        db.session.commit()
            
        # g.event.log(g.device.title, 'DANGER', f'Für die Kampklasse {event_class.title} wurde die Einteilung zurückgesetzt: {group_counter} Gruppen, {participant_counter} TN wurden gelöscht und {registration_counter} TN-Registrierungen wurden zurückgesetzt')
        # flash(f"Für die Kampklasse {event_class.title} wurde die Einteilung zurückgesetzt. {group_counter} Gruppen, {participant_counter} TN wurden gelöscht und {registration_counter} TN-Registrierungen wurden zurückgesetzt.", 'success')

        return redirect(url_for('mod_placement.for_class', event=g.event.slug, id=event_class.id))

    return render_template("mod_placement/refresh_for_class.html", event_class=event_class)


def _get_weight_classes(event_class):
    classes = []
    raw_classes = event_class.weight_generator.strip().split("\n")
    raw_classes = sorted(raw_classes, key=lambda cl: abs(int(cl)) if not cl.startswith('+') else 9999 + int(cl))
    
    current_minimum = None

    for cl in raw_classes:
        weight = abs(int(cl))
        if cl.startswith("+"):
            classes.append((f"+{weight} kg", (weight, None)))
        else:
            classes.append((f"-{weight} kg", (current_minimum, weight)))
            current_minimum = weight
    
    return classes


def _randomly_place_group(group, method='random'):
    participants = group.participants.filter_by(placement_index=None)
    list_system = group.list_system()
    list_max_count = list_system.mandatory_maximum
    current_count = 0

    current_club = None
    clubs = [i[0] for i in participants.with_entities(Participant.association_name)
             .group_by(Participant.association_name).all()]
    
    # shuffle clubs already
    random.shuffle(clubs)

    group.system = list_system
    group.list_break_count = group.list_system().break_count

    while current_count < list_max_count:
        # Is there already a participant at this position
        if group.participants.filter_by(placement_index=current_count).count():
            current_count += 1
            continue

        # If there is no next participant (exhausted)
        if not participants.count():
            break

        if method == 'smallest_weight' or method == 'largest_weight':
            all_participants = participants.all()
            data_pairs = []

            for participant in all_participants:
                if participant.registration is None: continue
                data_pairs.append([participant, participant.registration.verified_weight])
            
            data_pairs = sorted(data_pairs, key=lambda p: p[1])

        elif method == 'club_random':
            if current_club and not participants.filter_by(association_name=current_club).count():
                current_club = None

            if current_club is None:
                current_club = clubs.pop()
    
        if method == 'random':
            next_participant = random.choice(participants.all())
        elif method == 'club_random':
            next_participant = random.choice(
                participants.filter_by(association_name=current_club).all())
        elif method == 'smallest_weight':
            next_participant = data_pairs[0][0]
        elif method == 'largest_weight':
            next_participant = data_pairs[-1][0]


        next_participant.placement_index = current_count
        db.session.commit()

        current_count += 1


def _refresh_participant_name(participant, registration):
    participant.full_name = f"{registration.first_name} {registration.last_name}"

    if len(participant.full_name) > 21:
         participant.full_name = f"{registration.first_name[0]}. {registration.last_name}"

    if g.event.setting('use_association_instead_of_club', False) and registration.association:
        participant.association_name = registration.association.name
    else:
        participant.association_name = registration.club


def _refresh_participant_weight(event_class, participant, registration, group):
    groups_that_need_refreshing = []
    tolerance = int(float(request.form['tolerance']) * 1000)
    actual_weight = registration.verified_weight - tolerance

    # Delete from unfitting groups
    if ((group.min_weight is not None and group.min_weight >= actual_weight) or \
        (group.max_weight is not None and group.max_weight < actual_weight)) and \
            not group.marked_ready:

        if registration.participants.count() == 1:
            registration.placed = False

        db.session.delete(participant)
        db.session.commit()

        groups_that_need_refreshing.append(group)

    # Assign to new fitting groups

    applicable_groups = event_class.groups.filter(
        Group.min_weight.is_(None) | (Group.min_weight < actual_weight),
        Group.max_weight.is_(None) | (Group.max_weight >= actual_weight)
    ).all()

    for newgroup in applicable_groups:
        # Ignore groups that are already marked as ready
        if newgroup.marked_ready:
            continue

        # Skip if we already have the participant here
        if newgroup.participants.filter_by(registration=registration).count() > 0:
            continue

        participant = Participant(event=g.event, group=newgroup)
        participant.placement_index = None
        participant.manually_placed = None
        participant.final_placement = None
        participant.final_points = None
        participant.final_score = None
        participant.removed = False
        participant.disqualified = False
        participant.removal_cause = None

        participant.full_name = f"{registration.first_name} {registration.last_name}"

        if len(participant.full_name) > 21:
            participant.full_name = f"{registration.first_name[0]}. {registration.last_name}"

        participant.registration = registration

        if g.event.setting('use_association_instead_of_club', False) and registration.association:
            participant.association_name = registration.association.name
        else:
            participant.association_name = registration.club

        registration.placed = True
        registration.placed_at = registration.placed_at or dt.now()

        db.session.add(participant)
        groups_that_need_refreshing.append(newgroup)

    db.session.commit()

    return groups_that_need_refreshing

def _refresh_group(group):
    group.system_id = None

    has_autoplaced_participant = False

    for participant in group.participants:
        if participant.placement_index is None:
            continue

        if not participant.manually_placed:
            has_autoplaced_participant = True

        if participant.placement_index >= group.list_system().mandatory_maximum:
            participant.placement_index = None
            participant.manually_placed = False

    if has_autoplaced_participant:
        _randomly_place_group(group, method=request.form.get('method', 'random'))
    
    db.session.commit()