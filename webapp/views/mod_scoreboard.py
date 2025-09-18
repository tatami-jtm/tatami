from flask import Blueprint, render_template, flash, g, session, \
    request, redirect, url_for, jsonify

from .event_manager import check_and_apply_event
from .devices import check_is_registered
from .. import helpers

mod_scoreboard_view = Blueprint('mod_scoreboard', __name__)

@mod_scoreboard_view.route('/standalone')
@check_and_apply_event
@check_is_registered
def standalone():
    if not g.device.event_role.may_use_scoreboard:
        flash('Sie haben keine Berechtigung, hierauf zuzugreifen.', 'danger')
        return redirect(url_for('devices.index', event=g.event.slug))

    return render_template("mod_scoreboard/standalone.html")


@mod_scoreboard_view.route('/managed')
@check_and_apply_event
@check_is_registered
def managed():
    if not g.device.event_role.may_use_scoreboard or \
        not g.device.event_role.may_use_assigned_lists:
        flash('Sie haben keine Berechtigung, hierauf zuzugreifen.', 'danger')
        return redirect(url_for('devices.index', event=g.event.slug))

    g.mat = g.device.position
    assigned_lists = g.mat.assigned_groups.filter_by(marked_ready=True).all()

    # Make sure all assigned lists are created (if not already)
    for assigned_list in assigned_lists:
        helpers.force_create_list(assigned_list)

    break_time = None
    if g.event.setting('scheduling.use', True):
        break_time = helpers.do_match_schedule(g.mat) or None

    if break_time is not None:
        break_time = f"{break_time//60}min {break_time%60}s"

    helpers.do_promote_scheduled_fights(g.mat)

    return render_template("mod_scoreboard/managed.html", assigned_lists=assigned_lists, break_time=break_time)


@mod_scoreboard_view.route('/managed/api/reload')
@check_and_apply_event
@check_is_registered
def api_reload():
    if not (g.device.event_role.may_use_global_list or g.device.event_role.may_use_assigned_lists):
        return jsonify({
            'status': 'error',
            'message': 'Sie haben keine Berechtigung, hierauf zuzugreifen.'
        }), 401
    
    g.mat = g.device.position
    assigned_lists = g.mat.assigned_groups.filter_by(marked_ready=True, completed=False).all()

    # Make sure all assigned lists are created (if not already)
    for assigned_list in assigned_lists:
        helpers.force_create_list(assigned_list)

    break_time = None
    if g.event.setting('scheduling.use', True):
        break_time = helpers.do_match_schedule(g.mat) or None

    if break_time is not None:
        break_time = f"{break_time//60}min {break_time%60}s"

    helpers.do_promote_scheduled_fights(g.mat)

    return render_template("mod_scoreboard/_schedule.html", assigned_lists=assigned_lists, break_time=break_time)