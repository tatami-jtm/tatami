from flask import Blueprint, render_template, flash, g, session, \
    request, redirect, url_for, send_file

import io

from .event_manager import check_and_apply_event
from .devices import check_is_registered

from ..models import db

from .. import helpers

mod_list_view = Blueprint('mod_list', __name__)

@mod_list_view.route('/display/<id>/list.png')
@check_and_apply_event
@check_is_registered
def display_image(id):
    if not g.device.event_role.may_use_global_list and not g.device.event_role.may_use_assigned_lists:
        flash('Sie haben keine Berechtigung, hierauf zuzugreifen.', 'danger')
        return redirect(url_for('devices.index', event=g.event.slug))
    
    group = g.event.groups.filter_by(id=id).one_or_404()
    group_list = helpers.load_list(group)

    image = group_list.make_image(title=g.event.title, event_class=group.event_class.short_title, group=group.cut_title())
    image_io = io.BytesIO()
    image.save(image_io, 'PNG', quality=70)
    image_io.seek(0)

    return send_file(image_io, mimetype='image/png')


@mod_list_view.route('/display/<id>/list.pdf')
@check_and_apply_event
@check_is_registered
def display_pdf(id):
    if not g.device.event_role.may_use_global_list and not g.device.event_role.may_use_assigned_lists:
        flash('Sie haben keine Berechtigung, hierauf zuzugreifen.', 'danger')
        return redirect(url_for('devices.index', event=g.event.slug))
    
    group = g.event.groups.filter_by(id=id).one_or_404()
    group_list = helpers.load_list(group)

    output = io.BytesIO()

    pdf = group_list.make_pdf(title=g.event.title, event_class=group.event_class.short_title, group=group.cut_title())
    pdf_io = io.BytesIO()
    pdf.write(pdf_io)
    pdf_io.seek(0)

    return send_file(pdf_io, mimetype='application/pdf')