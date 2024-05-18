from flask import Blueprint, render_template, flash, g, session, \
    request, redirect, url_for, send_file, Response, jsonify

import io, zipfile, random, time, json
from datetime import datetime

from .event_manager import check_and_apply_event
from .devices import check_is_registered

from ..models import db, Match

from .. import helpers

mod_list_view = Blueprint('mod_list', __name__)


@mod_list_view.route('/')
@check_and_apply_event
@check_is_registered
def index():
    if not g.device.event_role.may_use_assigned_lists:
        flash('Sie haben keine Berechtigung, hierauf zuzugreifen.', 'danger')
        return redirect(url_for('devices.index', event=g.event.slug))

    g.mat = g.device.position
    assigned_lists = g.mat.assigned_groups.filter_by(marked_ready=True, completed=False).all()

    # Make sure all assigned lists are created (if not already)
    for assigned_list in assigned_lists:
        helpers.force_create_list(assigned_list)

    if g.event.setting('scheduling.use', True):
        helpers.do_match_schedule(g.mat)

    helpers.do_promote_scheduled_fights(g.mat)

    if 'shown_list' in request.values:
        shown_list = g.mat.assigned_groups.filter_by(marked_ready=True, id=request.values['shown_list']).one_or_404()
    else:
        current_match = g.mat.current_match()
        if current_match:
            shown_list = current_match.group
        elif len(assigned_lists):
            shown_list = assigned_lists[0]
        else:
            shown_list = None

    return render_template("mod_list/index.html", assigned_lists=assigned_lists, shown_list=shown_list)


@mod_list_view.route('/display/<id>/list.png')
@check_and_apply_event
@check_is_registered
def display_image(id):
    if not (g.device.event_role.may_use_global_list or
            g.device.event_role.may_use_assigned_lists or
            g.device.event_role.may_use_placement_tool):
        flash('Sie haben keine Berechtigung, hierauf zuzugreifen.', 'danger')
        return redirect(url_for('devices.index', event=g.event.slug))
    
    group = g.event.groups.filter_by(id=id).one_or_404()
    group_list = helpers.load_list(group)

    if 'cumult' in request.values:
        time.sleep(random.random())

    if 'draft' in request.values:
        image = group_list.make_image(title=g.event.title,
                                      event_class=group.event_class.short_title,
                                      group=group.cut_title(),
                                      draft=True)
    elif group.assigned_to_position:
        image = group_list.make_image(title=g.event.title,
                                      event_class=group.event_class.short_title,
                                      group=group.cut_title(),
                                      mat=group.assigned_to_position.title)
    else:
        image = group_list.make_image(title=g.event.title,
                                      event_class=group.event_class.short_title,
                                      group=group.cut_title())
    image_io = io.BytesIO()
    image.save(image_io, 'PNG', quality=70)
    image_io.seek(0)

    return send_file(image_io, mimetype='image/png')


@mod_list_view.route('/display/<id>/list.pdf')
@check_and_apply_event
@check_is_registered
def display_pdf(id):
    if not (g.device.event_role.may_use_global_list or
            g.device.event_role.may_use_assigned_lists or
            g.device.event_role.may_use_placement_tool):
        flash('Sie haben keine Berechtigung, hierauf zuzugreifen.', 'danger')
        return redirect(url_for('devices.index', event=g.event.slug))
    
    group = g.event.groups.filter_by(id=id).one_or_404()
    group_list = helpers.load_list(group)

    if 'draft' in request.values:
        pdf = group_list.make_pdf(title=g.event.title,
                                  event_class=group.event_class.short_title,
                                  group=group.cut_title(),
                                  draft=True)
    elif group.assigned_to_position:
        pdf = group_list.make_pdf(title=g.event.title,
                                  event_class=group.event_class.short_title,
                                  group=group.cut_title(),
                                  mat=group.assigned_to_position.title)
    else:
        pdf = group_list.make_pdf(title=g.event.title,
                                  event_class=group.event_class.short_title,
                                  group=group.cut_title())

    pdf_io = io.BytesIO()
    pdf.write(pdf_io)
    pdf_io.seek(0)

    return send_file(pdf_io, mimetype='application/pdf')


@mod_list_view.route('/display/all_lists.zip')
@check_and_apply_event
@check_is_registered
def display_all():
    if not g.device.event_role.may_use_global_list:
        flash('Sie haben keine Berechtigung, hierauf zuzugreifen.', 'danger')
        return redirect(url_for('devices.index', event=g.event.slug))
    
    collected_groups = []
    for event_class in g.event.classes.filter_by(begin_fighting=True, ended_fighting=False).all():
        for group in event_class.groups.all():
            collected_groups.append([
                group,
                helpers.load_list(group)
            ])

    zip_io = io.BytesIO()
    zip_file = zipfile.ZipFile(zip_io, mode='w')

    for group, group_list in collected_groups:
        if group.assigned_to_position:
            pdf = group_list.make_pdf(title=g.event.title,
                                    event_class=group.event_class.short_title,
                                    group=group.cut_title(),
                                    mat=group.assigned_to_position.title)
        else:
            pdf = group_list.make_pdf(title=g.event.title,
                                    event_class=group.event_class.short_title,
                                    group=group.cut_title())

        pdf_io = io.BytesIO()
        pdf.write(pdf_io)
        pdf_io.seek(0)

        title = group.title
        title = title.replace(":", "_").replace(".", "").replace(",", "").replace(" ", "_")
        title = title.replace("+", "_plus_")

        print(title)

        zip_file.writestr(f"{title}.pdf", pdf_io.getbuffer())
    
    zip_file.close()

    return Response(zip_io.getvalue(), mimetype='application/zip', headers={
        'Content-Disposition': 'attachment;filename=all_lists.zip'
    })


@mod_list_view.route('/group/<id>/match/<match_id>/schedule')
@check_and_apply_event
@check_is_registered
def schedule_match(id, match_id):
    if not (g.device.event_role.may_use_global_list or
            g.device.event_role.may_use_assigned_lists):
        flash('Sie haben keine Berechtigung, hierauf zuzugreifen.', 'danger')
        return redirect(url_for('devices.index', event=g.event.slug))
    
    group = g.event.groups.filter_by(id=id).one_or_404()

    match = group.matches.filter_by(id=match_id).one_or_404()
    if not match.scheduled:
        if match.schedulable():
            match.scheduled = True
            match.scheduled_at = datetime.now()
            max_schedule_key = group.event_class.matches.filter_by(scheduled=True).order_by(Match.match_schedule_key.desc()).first()
            match.match_schedule_key = (max_schedule_key.match_schedule_key if max_schedule_key is not None else 0) + 1
            match.white.last_fight_at = datetime.now()
            match.blue.last_fight_at = datetime.now()

            db.session.commit()
            g.event.log(g.device.title, 'DEBUG', f'Der Kampf {group.title} - {match.white.full_name}/{match.blue.full_name} wurde auf Nr. {match.match_schedule_key} angesetzt.')

            if not 'do_not_add_flash_message' in request.values:
                flash("Kampf erfolgreich angesetzt.", 'success')
        else:
            flash("Auszeit notwendig -- Kampf kann zurzeit nicht stattfinden.", 'danger')

    return redirect(request.values['origin_url'])


@mod_list_view.route('/group/<id>/match/<match_id>/unschedule')
@check_and_apply_event
@check_is_registered
def unschedule_match(id, match_id):
    if not (g.device.event_role.may_use_global_list or
            g.device.event_role.may_use_assigned_lists):
        flash('Sie haben keine Berechtigung, hierauf zuzugreifen.', 'danger')
        return redirect(url_for('devices.index', event=g.event.slug))
    
    group = g.event.groups.filter_by(id=id).one_or_404()
    group_list = helpers.load_list(group)

    match = group.matches.filter_by(id=match_id).one_or_404()
    if match.scheduled:
        match.scheduled = False
        match.scheduled_at = None
        match.match_schedule_key = None

        db.session.commit()
        g.event.log(g.device.title, 'DEBUG', f'Der Kampf {group.title} - {match.white.full_name}/{match.blue.full_name} wurde abgesetzt.')

        flash("Kampf erfolgreich abgesetzt.", 'success')

    return redirect(request.values['origin_url'])

@mod_list_view.route('/group/<id>/match/<match_id>/write-result', methods=['POSt'])
@check_and_apply_event
@check_is_registered
def write_match_result(id, match_id):
    if not (g.device.event_role.may_use_global_list or
            g.device.event_role.may_use_assigned_lists):
        flash('Sie haben keine Berechtigung, hierauf zuzugreifen.', 'danger')
        return redirect(url_for('devices.index', event=g.event.slug))
    
    group = g.event.groups.filter_by(id=id).one_or_404()

    match = group.matches.filter_by(id=match_id).one_or_404()
    if not match.completed:
        match.completed = True
        match.completed_at = datetime.now()
        
    is_new, match_result = match.get_result()

    if request.form['winner'] == 'white':
        match_result.is_white_winner = True
        match_result.is_blue_winner = False

        match_result.white_points = 1
        match_result.blue_points = 0

        match_result.white_score = int(request.form['score'])
        match_result.blue_score = 0

        match_result.is_white_disqualified = False
        match_result.is_blue_disqualified = 'loser_disqualified' in request.form

        match_result.is_white_removed = False
        match_result.is_blue_removed = 'loser_removed' in request.form
    elif request.form['winner'] == 'blue':
        match_result.is_white_winner = False
        match_result.is_blue_winner = True

        match_result.white_points = 0
        match_result.blue_points = 1

        match_result.white_score = 0
        match_result.blue_score = int(request.form['score'])

        match_result.is_white_disqualified = 'loser_disqualified' in request.form
        match_result.is_blue_disqualified = False

        match_result.is_white_removed = 'loser_removed' in request.form
        match_result.is_blue_removed = False
    else:
        flash("Es wurde kein Ergebnis eingetragen, da nicht genügend Informationen übermittelt wurden.", 'danger')
        return redirect(request.form['origin_url'])
    
    has_sb_data = False
    sb_data = {
        "white": {
            "ippon": None,
            "wazaari": None,
            "shido": None,
            "hansokumake": None
        },
        "blue": {
            "ippon": None,
            "wazaari": None,
            "shido": None,
            "hansokumake": None
        }
    }

    for side in ['white', 'blue']:
        for field, limit in [('ippon', 1), ('wazaari', 2), ('shido', 3), ('hansokumake', 1)]:
            key = f"sb-{side}-{field}"

            if key in request.form:
                has_sb_data = True

                value = int(request.form[key])
                if 0 <= value <= limit:
                    sb_data[side][field] = value
                elif value < 0:
                    sb_data[side][field] = 0
                elif value > limit:
                    sb_data[side][field] = limit

    if has_sb_data:
        match_result.scoreboard_data = json.dumps(sb_data)

    if 'ft-minutes' in request.form and 'ft-seconds' in request.form:
        match_result.full_time = 60 * int(request.form['ft-minutes']) + int(request.form['ft-seconds'])

    if is_new:
        db.session.add(match_result)

    match.white.last_fight_at = datetime.now()
    match.blue.last_fight_at = datetime.now()

    db.session.commit()
    g.event.log(g.device.title, 'DEBUG', f'Für den Kampf {group.title} - {match.white.full_name}/{match.blue.full_name} wurde ein Ergebnis eingetragen.')

    if 'is_api' in request.form:
        return jsonify({
            'status': 'success'
        })

    elif not 'do_not_add_flash_message' in request.form:
        flash("Ergebnis wurde erfolgreich eingetragen.", 'success')

    return redirect(request.form['origin_url'])


@mod_list_view.route('/group/<id>/match/<match_id>/clear-result')
@check_and_apply_event
@check_is_registered
def clear_match_result(id, match_id):
    if not (g.device.event_role.may_use_global_list or
            g.device.event_role.may_use_assigned_lists):
        flash('Sie haben keine Berechtigung, hierauf zuzugreifen.', 'danger')
        return redirect(url_for('devices.index', event=g.event.slug))
    
    group = g.event.groups.filter_by(id=id).one_or_404()

    match = group.matches.filter_by(id=match_id).one_or_404()
    if match.completed:
        match.completed = False
        match.completed_at = None

        # Match is considered not scheduled up
        match.called_up = False
        match.called_up_at = None
        match.running = False
        match.running_since = None
        match.scheduled = False
        match.scheduled_at = None
        is_new, match_result = match.get_result()

        if not is_new:
            db.session.delete(match_result)
        
    db.session.commit()

    flash("Ergebnis wurde erfolgreich ausgetragen.", 'success')
    g.event.log(g.device.title, 'DEBUG', f'Für den Kampf {group.title} - {match.white.full_name}/{match.blue.full_name} wurde das Ergebnis gelöscht.')

    return redirect(request.values['origin_url'])



@mod_list_view.route('/api/schedule/<match_id>')
@check_and_apply_event
@check_is_registered
def api_schedule_match(match_id):
    if not (g.device.event_role.may_use_global_list or g.device.event_role.may_use_assigned_lists):
        return jsonify({
            'status': 'error',
            'message': 'Sie haben keine Berechtigung, hierauf zuzugreifen.'
        }), 401
    
    match = g.event.matches.filter_by(id=match_id).one_or_404()

    if not match.scheduled:
        if match.schedulable():
            match.scheduled = True
            match.scheduled_at = datetime.now()
            max_schedule_key = match.group.event_class.matches.filter_by(scheduled=True) \
                .order_by(Match.match_schedule_key.desc()).first()
            match.match_schedule_key = (max_schedule_key.match_schedule_key \
                                        if max_schedule_key is not None else 0) + 1
            match.white.last_fight_at = datetime.now()
            match.blue.last_fight_at = datetime.now()

            db.session.commit()
            g.event.log(g.device.title, 'DEBUG', f'Der Kampf {match.group.title} - {match.white.full_name}/{match.blue.full_name} wurde auf Nr. {match.match_schedule_key} angesetzt.')

            return jsonify({
                'status': 'success'
            })
        else:
            return jsonify({
                'status': 'error',
                'message': 'Auszeit notwendig -- Kampf kann zurzeit nicht stattfinden.'
            }), 400
    
    else:
        return jsonify({
            'status': 'error',
            'message': 'Der Kampf wurde bereits angesetzt.'
        }), 400