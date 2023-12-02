from flask import Blueprint, render_template, flash, g, session, \
    request, redirect, url_for, abort

from datetime import datetime as dt

from .event_manager import check_and_apply_event
from .devices import check_is_registered

from ..models import db, EventClass, Group, ListSystem

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