from flask import Blueprint, render_template, flash, g, session, \
    request, redirect, url_for, abort

from datetime import datetime as dt

from .event_manager import check_and_apply_event
from .devices import check_is_registered

from ..models import db, EventClass, Group, ListSystem, Participant

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
    group = Group(created_manually=True, event=g.event, event_class=event_class)

    if request.method == 'POST':
        group.title = event_class.short_title + ' ' + request.form['name']
        group.assign_by_logic = 'assign_by_logic' in request.form
        group.min_weight = int(float(request.form['min_weight']) * 1000) if request.form['min_weight'] else None
        group.max_weight = int(float(request.form['max_weight']) * 1000) if request.form['max_weight'] else None

        if request.form['system']:
            group.system_id = int(request.form['system'])
        else:
            group.system_id = None

        db.session.add(group)
        db.session.commit()

        flash(f"Neue Gruppe {group.title} erfolgreich erstellt.", 'success')

        return redirect(url_for('mod_placement.for_class', event=g.event.slug, id=event_class.id, group=group.id))

    return render_template("mod_placement/add_group.html", event_class=event_class, group=group, systems=ListSystem.all_enabled())


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
        else:
            group.system_id = None

        db.session.commit()

        flash(f"Gruppe {group.title} erfolgreich aktualisiert.", 'success')

        return redirect(url_for('mod_placement.for_class', event=g.event.slug, id=event_class.id, group=group.id))

    return render_template("mod_placement/edit_group.html", event_class=event_class, group=group, systems=ListSystem.all_enabled())


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

        flash(f"Gruppe {group.title} erfolgreich gelöscht.", 'success')

        return redirect(url_for('mod_placement.for_class', event=g.event.slug, id=event_class.id))

    return render_template("mod_placement/delete_group.html", event_class=event_class, group=group)


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
                participant.association_name = registration.club
                participant.registration = registration

                registration.placed = True

            elif request.form['participant'] == 'custom':
                participant.full_name = request.form['custom-full_name']
                participant.association_name = request.form['custom-association']
                participant.registration = None
            
            group = event_class.groups.filter_by(id=request.form['group']).one()
            participant.group = group

            db.session.add(participant)
            db.session.commit()

            return redirect(url_for('mod_placement.for_class', event=g.event.slug, id=event_class.id, group=group.id))
        
        flash("Es wurden nicht alle notwendigen Felder ausgefüllt.", 'danger')

    registrations = event_class.registrations.filter_by(confirmed=True, registered=True, weighed_in=True).order_by('last_name', 'first_name', 'verified_weight')
    
    group = event_class.groups.filter_by(id=request.values.get('group', None)).one_or_none()
    registration = g.event.registrations.filter_by(id=request.values.get('registration', None)).one_or_none()

    return render_template("mod_placement/assign.html", event_class=event_class, group=group, registration=registration, registrations=registrations)


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

        db.session.delete(participant)
        db.session.commit()

        return redirect(url_for('mod_placement.for_class', event=g.event.slug, id=event_class.id, group=group.id))

    return render_template("mod_placement/unassign.html", event_class=event_class, participant=participant, registration=registration)


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
                group = Group(created_manually=False, event=g.event, event_class=event_class)
                group.title = event_class.short_title + ' ' + cl[0]
                group.assign_by_logic = True
                group.min_weight = cl[1][0] * 1000 if cl[1][0] else None
                group.max_weight = cl[1][1] * 1000 if cl[1][1] else None
                group.system_id = None

                db.session.add(group)
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

                    group = Group(created_manually=False, event=g.event, event_class=event_class)
                    group.title = event_class.short_title + ' ' + cl[0]
                    group.assign_by_logic = True
                    group.min_weight = cl[1][0] * 1000 if cl[1][0] else None
                    group.max_weight = cl[1][1] * 1000 if cl[1][1] else None
                    group.system_id = None

                    db.session.add(group)
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
    
                registration = registration
                participant.full_name = f"{registration.first_name} {registration.last_name}"
                participant.association_name = registration.club
                participant.registration = registration

                registration.placed = True

                db.session.add(participant)
                participants_created += 1

        db.session.commit()

        flash(f"Verbleibende TN erfolgreich zugewiesen. Erstellt wurden {groups_created} Gruppe(n) und {participants_created} TN.", 'success')

        return redirect(url_for('mod_placement.for_class', event=g.event.slug, id=event_class.id))

    defaults_to_all_new_classes = event_class.groups.filter_by(created_manually=False).count() == 0

    return render_template("mod_placement/assign_all-predefined.html", event_class=event_class, weight_classes=weight_classes, defaults_to_all_new_classes=defaults_to_all_new_classes)


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