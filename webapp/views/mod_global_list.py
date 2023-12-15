from flask import Blueprint, render_template, flash, g, session, \
    request, redirect, url_for

from datetime import datetime as dt

from .event_manager import check_and_apply_event
from .devices import check_is_registered

from ..models import db, Group

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
        print(free_groups)


    current_group = None
    if 'group' in request.values:
        current_group = g.event.groups.filter_by(id=request.values['group']).one_or_404()

    mats = g.event.device_positions.filter_by(is_mat=True).all()
    
    return render_template("mod_global_list/index.html", mats=mats, current_group=current_group, free_groups=free_groups)


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
    else:
        group.marked_ready = False
        group.marked_ready_at = None
    
    db.session.commit()

    return redirect(url_for('mod_global_list.index', event=g.event.slug, group_list=request.form['group_list']))


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
    
    db.session.commit()

    return redirect(url_for('mod_global_list.index', event=g.event.slug))