from flask import Blueprint, render_template, flash, g, session, \
    request, redirect, url_for, send_file, Response, jsonify, abort

import io, zipfile, random, time, json
from datetime import datetime

from pypdf import PdfWriter, PdfReader

from .event_manager import check_and_apply_event
from .devices import check_is_registered

from ..models import db, Match

from .. import helpers

from ..listslib import ListRenderer

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


@mod_list_view.route('/display')
@check_and_apply_event
@check_is_registered
def display():
    if not g.device.event_role.may_use_assigned_lists:
        flash('Sie haben keine Berechtigung, hierauf zuzugreifen.', 'danger')
        return redirect(url_for('devices.index', event=g.event.slug))

    g.mat = g.device.position
    assigned_lists = g.mat.assigned_groups.filter_by(marked_ready=True, completed=False).all()

    # Make sure all assigned lists are created (if not already)
    for assigned_list in assigned_lists:
        helpers.force_create_list(assigned_list)

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

    return render_template("mod_list/display.html", assigned_lists=assigned_lists, shown_list=shown_list)

@mod_list_view.route('/display/<id>/list.png')
@mod_list_view.route('/display/<id>/list-page<int:page>.png')
@check_and_apply_event
@check_is_registered
def display_image(id, page=1):
    if not (g.device.event_role.may_use_global_list or
            g.device.event_role.may_use_assigned_lists or
            g.device.event_role.may_use_placement_tool):
        flash('Sie haben keine Berechtigung, hierauf zuzugreifen.', 'danger')
        return redirect(url_for('devices.index', event=g.event.slug))
    
    group = g.event.groups.filter_by(id=id).one_or_404()
    group_list = helpers.load_list(group)

    if 'cumult' in request.values:
        time.sleep(random.random())

    if not group.list_page_count() > page - 1 >= 0:
        abort(404)

    lr = ListRenderer(group_list, g.event, group, served=False)
    image_io = io.BytesIO()
    image_data = lr.render_image(page=page)
    image_data[0].save(image_io, 'PNG', quality=70)

    if image_data[1] != group.list_page_count():
        group.display_page_count = image_data[1]
        db.session.commit()

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

    lr = ListRenderer(group_list, g.event, group, served=False)

    pdf_io = io.BytesIO()
    pdf_io.write((pdf_data := lr.render_pdf())[0])
    pdf_io.seek(0)

    if pdf_data[1] != group.list_page_count():
        group.display_page_count = pdf_data[1]
        db.session.commit()

    return send_file(pdf_io, mimetype='application/pdf')


@mod_list_view.route('/display/all_lists.pdf')
@check_and_apply_event
@check_is_registered
def display_all_pdf():
    if not g.device.event_role.may_use_global_list:
        flash('Sie haben keine Berechtigung, hierauf zuzugreifen.', 'danger')
        return redirect(url_for('devices.index', event=g.event.slug))
    
    collected_groups = []
    for event_class in g.event.classes.filter_by(begin_fighting=True, ended_fighting=False).all():
        for group in event_class.groups.all():
            if not group.participants.count() == 0 and group.list_system() != None:
                collected_groups.append([
                    group,
                    helpers.load_list(group)
                ])

    pdfw = PdfWriter()

    for group, group_list in collected_groups:
        lr = ListRenderer(group_list, g.event, group, served=False)
        pdf = PdfReader(io.BytesIO(lr.render_pdf()[0]))

        for page in pdf.pages:
            pdfw.add_page(page)

    pdf_io = io.BytesIO()
    pdfw.write(pdf_io)
    pdf_io.seek(0)

    return send_file(pdf_io, mimetype='application/pdf')


@mod_list_view.route('/display/all_lists.zip')
@check_and_apply_event
@check_is_registered
def display_all_zip():
    if not g.device.event_role.may_use_global_list:
        flash('Sie haben keine Berechtigung, hierauf zuzugreifen.', 'danger')
        return redirect(url_for('devices.index', event=g.event.slug))
    
    collected_groups = []
    for event_class in g.event.classes.filter_by(begin_fighting=True, ended_fighting=False).all():
        for group in event_class.groups.all():
            if not group.participants.count() == 0 and group.list_system() != None:
                collected_groups.append([
                    group,
                    helpers.load_list(group)
                ])

    zip_io = io.BytesIO()
    zip_file = zipfile.ZipFile(zip_io, mode='w')

    for group, group_list in collected_groups:
        lr = ListRenderer(group_list, g.event, group, served=False)

        pdf_io = io.BytesIO()
        pdf_io.write(lr.render_pdf()[0])
        pdf_io.seek(0)

        title = group.title
        title = title.replace(":", "_").replace(".", "").replace(",", "").replace(" ", "_")
        title = title.replace("+", "_plus_")

        zip_file.writestr(f"{title}.pdf", pdf_io.getbuffer())
    
    zip_file.close()

    now = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    return Response(zip_io.getvalue(), mimetype='application/zip', headers={
        'Content-Disposition': f'attachment;filename=all_lists_{now}.zip'
    })


@mod_list_view.route('/display/<id>/list.html')
@check_and_apply_event
@check_is_registered
def display_html(id):
    if not (g.device.event_role.may_use_global_list or
            g.device.event_role.may_use_assigned_lists or
            g.device.event_role.may_use_placement_tool):
        flash('Sie haben keine Berechtigung, hierauf zuzugreifen.', 'danger')
        return redirect(url_for('devices.index', event=g.event.slug))
    
    group = g.event.groups.filter_by(id=id).one_or_404()
    group_list = helpers.load_list(group)

    lr = ListRenderer(group_list, g.event, group, served=True)
    return lr.render_html_template()


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
        if match.obsolete:
            flash("Match beruht auf veralteten Daten und kann daher nicht angesetzt werden.", 'danger')
        elif match.schedulable(consider_preptime=True):
            match.scheduled = True
            match.scheduled_at = datetime.now()
            max_schedule_key = group.event_class.matches.filter_by(scheduled=True).order_by(Match.match_schedule_key.desc()).first()
            match.match_schedule_key = (max_schedule_key.match_schedule_key if max_schedule_key is not None else 0) + 1
            match.white.last_fight_at = datetime.now() + \
                    group.estimated_average_fight_duration_delta()
            match.blue.last_fight_at = datetime.now() + \
                    group.estimated_average_fight_duration_delta()

            if not group.opened:
                group.opened = True
                group.opened_at = datetime.now()

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

    if match.obsolete:
        flash("Match beruht auf veralteten Daten und kann daher kein Ergebnis erhalten.", 'danger')
        return redirect(request.form['origin_url'])

    if not match.completed:
        match.completed = True
        match.completed_at = datetime.now()
        
    is_new, match_result = match.get_result()

    if 'winner' not in request.form or request.form['winner'] not in ('white', 'blue'):
        flash("Es wurde kein Ergebnis eingetragen, da nicht genügend Informationen übermittelt wurden.", 'danger')
        return redirect(request.form['origin_url'])
    elif request.form['winner'] == 'white':
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

        if 'loser_disqualified' in request.form:
            match.blue.disqualified = True
        else:
            match.blue.disqualified = False

        if 'loser_removed' in request.form:
            match.blue.removed = True
        else:
            match.blue.removed = False

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

        if 'loser_disqualified' in request.form:
            match.white.disqualified = True
        else:
            match.white.disqualified = False

        if 'loser_removed' in request.form:
            match.white.removed = True
        else:
            match.white.removed = False
    
    has_sb_data = False
    sb_data = {
        "white": {
        },
        "blue": {
        }
    }

    SBRULES = g.event.sb_rules()

    for side in ['white', 'blue']:
        for field, data in SBRULES['scores'].items():
            key = f"sb-{side}-{field}"

            if key in request.form:
                has_sb_data = True
                value = int(request.form[key])

                if 'max_count' in data:
                    limit = data['max_count']
                else:
                    limit = value

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

    if match.obsolete:
        flash("Match beruht auf veralteten Daten, daher kann das Ergebnis nicht entfernt werden.", 'danger')
        return redirect(request.form['origin_url'])

    if match.completed:
        match.completed = False
        match.completed_at = None

        # Match is considered not scheduled up
        match.called_up = False
        match.called_up_at = None
        match.running = False
        match.running_since = None
        match.scheduled = False
        match.match_schedule_key = None
        match.scheduled_at = None
        is_new, match_result = match.get_result()

        if not is_new:
            db.session.delete(match_result)

        if group.completed:
            group.completed = False
        
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
        if match.obsolete:
            return jsonify({
                'status': 'error',
                'message': 'Match beruht auf veralteten Daten und kann daher nicht angesetzt werden.'
            }), 400
        elif match.schedulable(consider_preptime=True):
            match.scheduled = True
            match.scheduled_at = datetime.now()
            max_schedule_key = match.group.event_class.matches.filter_by(scheduled=True) \
                .order_by(Match.match_schedule_key.desc()).first()
            match.match_schedule_key = (max_schedule_key.match_schedule_key \
                                        if max_schedule_key is not None else 0) + 1
            match.white.last_fight_at = datetime.now() + \
                    match.group.estimated_average_fight_duration_delta()
            match.blue.last_fight_at = datetime.now() + \
                    match.group.estimated_average_fight_duration_delta()

            if not match.group.opened:
                match.group.opened = True
                match.group.opened_at = datetime.now()

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
