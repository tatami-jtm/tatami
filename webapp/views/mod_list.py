from flask import Blueprint, render_template, flash, g, session, \
    request, redirect, url_for, send_file

import io
from datetime import datetime

from .event_manager import check_and_apply_event
from .devices import check_is_registered

from ..models import db, Match

from .. import helpers

mod_list_view = Blueprint('mod_list', __name__)

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


@mod_list_view.route('/group/<id>/match/<match_id>/schedule')
@check_and_apply_event
@check_is_registered
def schedule_match(id, match_id):
    if not (g.device.event_role.may_use_global_list or
            g.device.event_role.may_use_assigned_lists):
        flash('Sie haben keine Berechtigung, hierauf zuzugreifen.', 'danger')
        return redirect(url_for('devices.index', event=g.event.slug))
    
    group = g.event.groups.filter_by(id=id).one_or_404()
    group_list = helpers.load_list(group)

    match = group.matches.filter_by(id=match_id).one_or_404()
    if not match.scheduled:
        match.scheduled = True
        match.scheduled_at = datetime.now()
        max_schedule_key = group.event_class.matches.filter_by(scheduled=True).order_by(Match.match_schedule_key.desc()).first().match_schedule_key
        match.match_schedule_key = (max_schedule_key or 0) + 1

        db.session.commit()

        flash("Kampf erfolgreich angesetzt.", 'success')

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

        flash("Kampf erfolgreich abgesetzt.", 'success')

    return redirect(request.values['origin_url'])