from flask import Blueprint, render_template, flash, g, session, \
    request, redirect, url_for

from datetime import datetime as dt

from .event_manager import check_and_apply_event
from .devices import check_is_registered

from ..models import db, Group

from .. import helpers

mod_global_list_view = Blueprint('mod_global_list', __name__)

@mod_global_list_view.route('/')
@check_and_apply_event
@check_is_registered
def index():
    if not g.device.event_role.may_use_global_list:
        flash('Sie haben keine Berechtigung, hierauf zuzugreifen.', 'danger')
        return redirect(url_for('devices.index', event=g.event.slug))
    
    free_groups = []
    for event_class in g.event.classes.filter_by(begin_fighting=True, ended_fighting=False).all():
        free_groups += event_class.groups.filter_by(assigned=None).all()
        free_groups += event_class.groups.filter_by(assigned=False).all()


    current_group = None
    scheduled_matches = None
    not_scheduled_matches = None
    completed_matches = None
    if 'group' in request.values:
        current_group = g.event.groups.filter_by(id=request.values['group']).one_or_404()
        if current_group.marked_ready:
            helpers.force_create_list(current_group)
            scheduled_matches = current_group.matches.filter_by(scheduled=True, completed=False).order_by('match_schedule_key')
            not_scheduled_matches = current_group.matches.filter_by(scheduled=False, completed=False)
            completed_matches = current_group.matches.filter_by(completed=True)

    mats = g.event.device_positions.filter_by(is_mat=True).all()
    
    return render_template("mod_global_list/index.html", mats=mats, current_group=current_group, free_groups=free_groups, scheduled_matches=scheduled_matches, not_scheduled_matches=not_scheduled_matches,completed_matches=completed_matches)


@mod_global_list_view.route('/group/<id>/edit', methods=['POST'])
@check_and_apply_event
@check_is_registered
def update_group(id):
    if not g.device.event_role.may_use_global_list:
        flash('Sie haben keine Berechtigung, hierauf zuzugreifen.', 'danger')
        return redirect(url_for('devices.index', event=g.event.slug))
    
    group = g.event.groups.filter_by(id=id).one_or_404()

    if request.form['assignment'] == 'none':
        group.assigned = False
        group.assigned_to_position = None
    else:
        position = g.event.device_positions.filter_by(id=request.form['assignment']).one_or_404()
        group.assigned = True
        group.assigned_to_position = position

    if 'marked_ready' in request.form:
        if not group.marked_ready:
            group.marked_ready_at = dt.now()
            group.marked_ready = True
            helpers.force_create_list(group)
    else:
        group.marked_ready = False
        group.marked_ready_at = None
    
    db.session.commit()

    return redirect(url_for('mod_global_list.index', event=g.event.slug, group_list=request.form['group_list']))


@mod_global_list_view.route('/rotate-all', methods=['GET', 'POST'])
@check_and_apply_event
@check_is_registered
def rotate_all_groups():
    if not g.device.event_role.may_use_global_list:
        flash('Sie haben keine Berechtigung, hierauf zuzugreifen.', 'danger')
        return redirect(url_for('devices.index', event=g.event.slug))

    free_groups = []
    for event_class in g.event.classes.filter_by(begin_fighting=True, ended_fighting=False).all():
        free_groups += event_class.groups.filter_by(assigned=None).all()
        free_groups += event_class.groups.filter_by(assigned=False).all()

    free_groups = sorted(free_groups, key=lambda group: group.estimated_fight_count())[::-1]
    mats = g.event.device_positions.filter_by(is_mat=True).all()

    if request.method == "POST":
        if len(request.form.getlist('to')):
            mat_index = -1
            used_mats = { m.id: m for m in mats if str(m.id) in request.form.getlist('to')}
            matlist = { mi: 0 for mi in used_mats.keys() }

            for group in free_groups:
                emptiest_mat = used_mats[sorted(matlist.items(), key=lambda mi: mi[1])[0][0]]
                group.assigned = True
                group.assigned_to_position = emptiest_mat
                group.marked_ready = False
                group.marked_ready_at = None

                matlist[emptiest_mat.id] += group.estimated_fight_count()
            
            db.session.commit()

            return redirect(url_for('mod_global_list.index', event=g.event.slug))
        
        else:
            flash('Sie müssen wenigstens eine Liste auswählen.', 'danger')

    fight_count = sum([group.estimated_fight_count() for group in free_groups])
    
    return render_template('mod_global_list/rotate_all_groups.html', fight_count=fight_count, mats=mats, free_groups=free_groups)


@mod_global_list_view.route('/mat/<id>/mark-all-ready', methods=['GET', 'POST'])
@check_and_apply_event
@check_is_registered
def mark_all_at_mat_as_ready(id):
    if not g.device.event_role.may_use_global_list:
        flash('Sie haben keine Berechtigung, hierauf zuzugreifen.', 'danger')
        return redirect(url_for('devices.index', event=g.event.slug))
    
    mat = g.event.device_positions.filter_by(id=id).one_or_404()

    for group in mat.assigned_groups:
        if not group.marked_ready:
            group.marked_ready_at = dt.now()
            group.marked_ready = True
            helpers.force_create_list(group)
    
    db.session.commit()

    return redirect(url_for('mod_global_list.index', event=g.event.slug))



@mod_global_list_view.route('/preview/mat/<id>')
@check_and_apply_event
@check_is_registered
def preview_mat(id):
    if not g.device.event_role.may_use_global_list:
        flash('Sie haben keine Berechtigung, hierauf zuzugreifen.', 'danger')
        return redirect(url_for('devices.index', event=g.event.slug))
    
    mat = g.event.device_positions.filter_by(id=id).one_or_404()
    matches = []

    for group in mat.assigned_groups:
        if group.marked_ready:
            matches += group.matches.filter_by(scheduled=True, completed=False).all()

        print(group, helpers.get_next_match(group))
    
    matches = sorted(matches, key=lambda f: f.match_schedule_key)
    
    return render_template('mod_global_list/preview_mat.html', mat=mat, matches=matches)