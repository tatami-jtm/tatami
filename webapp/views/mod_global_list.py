from flask import Blueprint, render_template, flash, g, session, \
    request, redirect, url_for, abort

from datetime import datetime as dt, timedelta as td

from .event_manager import check_and_apply_event
from .devices import check_is_registered

from ..models import db, Group, Match

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
    obsolete_matches = None
    if 'group' in request.values:
        current_group = g.event.groups.filter_by(id=request.values['group']).one_or_404()
        if current_group.marked_ready:
            helpers.force_create_list(current_group)
            scheduled_matches = current_group.matches.filter(
                Match.scheduled==True,
                Match.completed==False,
                (Match.obsolete==False) | (Match.obsolete==None)
            ).order_by('match_schedule_key')
            not_scheduled_matches = current_group.matches.filter(
                Match.scheduled==False,
                Match.completed==False,
                (Match.obsolete==False) | (Match.obsolete==None)
            )
            completed_matches = current_group.matches.filter(
                Match.completed==True,
                (Match.obsolete==False) | (Match.obsolete==None)
            )
            obsolete_matches = current_group.matches.filter(
                Match.obsolete==True,
                Match.completed==True
            )

    mats = g.event.device_positions.filter_by(is_mat=True).all()
    now = dt.now()
    
    return render_template("mod_global_list/index.html", mats=mats, current_group=current_group, free_groups=free_groups, scheduled_matches=scheduled_matches, not_scheduled_matches=not_scheduled_matches,completed_matches=completed_matches, obsolete_matches=obsolete_matches, now=now)


@mod_global_list_view.route('/group/<id>/edit', methods=['POST'])
@check_and_apply_event
@check_is_registered
def update_group(id):
    if not g.device.event_role.may_use_global_list:
        flash('Sie haben keine Berechtigung, hierauf zuzugreifen.', 'danger')
        return redirect(url_for('devices.index', event=g.event.slug))
    
    group = g.event.groups.filter_by(id=id).one_or_404()

    if group.participants.count() == 0:
        abort(400)

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

            g.event.log(g.device.title, 'DEBUG', f'Die Gruppe {group.title} wird freigegeben')
    else:
        group.marked_ready = False
        group.marked_ready_at = None
    
    db.session.commit()
    g.event.log(g.device.title, 'DEBUG', f'Die Gruppe {group.title} wurde bearbeitet')

    return redirect(url_for('mod_global_list.index', event=g.event.slug, group_list=request.form['group_list']))


@mod_global_list_view.route('/group/<id>/parameters', methods=['GET', 'POST'])
@check_and_apply_event
@check_is_registered
def parameters(id):
    if not g.device.event_role.may_use_global_list:
        flash('Sie haben keine Berechtigung, hierauf zuzugreifen.', 'danger')
        return redirect(url_for('devices.index', event=g.event.slug))
    
    group = g.event.groups.filter_by(id=id).one_or_404()

    break_time = group.event_class.between_fights_time
    diff_delta = td(0, break_time)
    saved_participant = None

    if group.participants.count() == 0:
        abort(400)

    if request.method == 'POST':
        participant = group.participants.filter_by(id=request.form['participant_id']).one_or_404()
        participant.disqualified = 'disqualified' in request.form
        participant.removed = 'removed' in request.form
        participant.removal_cause = request.form['removal_cause']

        if request.form['last_fight_at'] == '':
            participant.last_fight_at = None
        else:
            participant.last_fight_at = (dt.fromisoformat(request.form['last_fight_at']) - diff_delta)

        db.session.commit()

        saved_participant = participant.id

    return render_template('mod_global_list/parameters.html', group=group, diff_delta=diff_delta,
                           saved_participant=saved_participant)


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

    free_groups = filter(lambda gr: gr.list_system(), free_groups)
    free_groups = sorted(free_groups, key=lambda group: group.estimated_fight_count())[::-1]
    mats = g.event.device_positions.filter_by(is_mat=True).all()

    if request.method == "POST":
        if len(request.form.getlist('to')):
            used_mats = { m.id: m for m in mats if str(m.id) in request.form.getlist('to')}
            matlist = { mi: 0 for mi in used_mats.keys() }

            for group in free_groups:
                if group.participants.count() == 0:
                    continue

                emptiest_mat = used_mats[sorted(matlist.items(), key=lambda mi: mi[1])[0][0]]
                group.assigned = True
                group.assigned_to_position = emptiest_mat
                group.marked_ready = False
                group.marked_ready_at = None

                matlist[emptiest_mat.id] += group.estimated_fight_count()
            
            db.session.commit()
            g.event.log(g.device.title, 'DEBUG', f'Es wurden {len(free_groups)} Gruppen auf {len(used_mats)} Matten verteilt.')

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
            g.event.log(g.device.title, 'DEBUG', f'Die Gruppe {group.title} wird freigegeben')
    
    db.session.commit()
    g.event.log(g.device.title, 'DEBUG', f'Es wurden alle Gruppen auf {mat.title} freigegeben.')

    return redirect(url_for('mod_global_list.index', event=g.event.slug))



@mod_global_list_view.route('/preview/mat/<id>')
@check_and_apply_event
@check_is_registered
def preview_mat(id):
    if not g.device.event_role.may_use_global_list:
        flash('Sie haben keine Berechtigung, hierauf zuzugreifen.', 'danger')
        return redirect(url_for('devices.index', event=g.event.slug))
    
    mat = g.event.device_positions.filter_by(id=id).one_or_404()
    return render_template('mod_global_list/preview_mat.html', mat=mat)



@mod_global_list_view.route('/classes/progress')
@check_and_apply_event
@check_is_registered
def class_progress():
    if not g.device.event_role.may_use_global_list:
        flash('Sie haben keine Berechtigung, hierauf zuzugreifen.', 'danger')
        return redirect(url_for('devices.index', event=g.event.slug))

    return render_template('mod_global_list/class_progress.html')




@mod_global_list_view.route('/classes/<id>/progress/next', methods=['GET', 'POST'])
@check_and_apply_event
@check_is_registered
def class_step_forward(id):
    if not g.device.event_role.may_use_global_list:
        flash('Sie haben keine Berechtigung, hierauf zuzugreifen.', 'danger')
        return redirect(url_for('devices.index', event=g.event.slug))

    event_class = g.event.classes.filter_by(id=id).one_or_404()

    if not event_class.begin_weigh_in:
        event_class.begin_weigh_in = True
        event_class.begin_weigh_in_at = dt.now()
    elif not event_class.begin_placement:
        event_class.begin_placement = True
        event_class.begin_placement_at = dt.now()
    elif not event_class.begin_fighting:
        event_class.begin_fighting = True
        event_class.begin_fighting_at = dt.now()
    elif not event_class.ended_fighting:
        event_class.ended_fighting = True
        event_class.ended_fighting_at = dt.now()

    db.session.commit()
    g.event.log(g.device.title, 'DEBUG', f'Kampfklasse {event_class.title} wurde in den nächsten Zustand gesetzt.')
    return redirect(url_for('mod_global_list.class_progress', event=g.event.slug))


@mod_global_list_view.route('/classes/<id>/progress/back', methods=['GET', 'POST'])
@check_and_apply_event
@check_is_registered
def class_step_back(id):
    if not g.device.event_role.may_use_global_list:
        flash('Sie haben keine Berechtigung, hierauf zuzugreifen.', 'danger')
        return redirect(url_for('devices.index', event=g.event.slug))

    event_class = g.event.classes.filter_by(id=id).one_or_404()

    if event_class.ended_fighting:
        event_class.ended_fighting = False
        event_class.ended_fighting_at = None
    elif event_class.begin_fighting:
        event_class.begin_fighting = False
        event_class.begin_fighting_at = None
    elif event_class.begin_placement:
        event_class.begin_placement = False
        event_class.begin_placement_at = None
    elif event_class.begin_weigh_in:
        event_class.begin_weigh_in = False
        event_class.begin_weigh_in_at = None

    db.session.commit()
    g.event.log(g.device.title, 'DEBUG', f'Kampfklasse {event_class.title} wurde in den früheren Zustand zurückgesetzt.')
    return redirect(url_for('mod_global_list.class_progress', event=g.event.slug))


@mod_global_list_view.route('/group/<id>/reset', methods=['GET', 'POST'])
@check_and_apply_event
@check_is_registered
def reset_group(id):
    if not g.device.event_role.may_use_global_list:
        flash('Sie haben keine Berechtigung, hierauf zuzugreifen.', 'danger')
        return redirect(url_for('devices.index', event=g.event.slug))
    
    group = g.event.groups.filter_by(id=id).one_or_404()

    if request.method == 'POST':
        if 'confirm' in request.form:
            helpers.reset_list(group)

            g.event.log(g.device.title, 'DANGER', f'Die Gruppe {group.title} wurde zurückgesetzt')
            flash(f"Gruppe {group.title} wurde erfolgreich zurückgesetzt.", 'success')

            return redirect(url_for('mod_global_list.index', event=g.event.slug, group=group.id))
        else:
            flash(f"Fehler: Sie müssen die Checkbox zur Bestätigung betätigen", 'danger')
    
    return render_template('mod_global_list/reset_group.html', group=group)