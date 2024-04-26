from flask import Blueprint, render_template, flash, g, session, \
    request, redirect, url_for, send_file

from datetime import datetime as dt

from .event_manager import check_and_apply_event
from .devices import check_is_registered

from ..models import db, Registration
from .. import helpers

import io, csv

mod_results_view = Blueprint('mod_results', __name__)

@mod_results_view.route('/')
@check_and_apply_event
@check_is_registered
def index():
    if not g.device.event_role.may_use_results:
        flash('Sie haben keine Berechtigung, hierauf zuzugreifen.', 'danger')
        return redirect(url_for('devices.index', event=g.event.slug))
    
    for evcl in g.event.classes:
        for group in evcl.groups.filter_by(completed=True):
            helpers.force_create_list(group)
    
    return render_template("mod_results/index.html")


@mod_results_view.route('/print/<id>')
@check_and_apply_event
@check_is_registered
def print_class(id):
    if not g.device.event_role.may_use_results:
        flash('Sie haben keine Berechtigung, hierauf zuzugreifen.', 'danger')
        return redirect(url_for('devices.index', event=g.event.slug))
    
    evcl = g.event.classes.filter_by(id=id).one_or_404()
    
    return render_template("mod_results/print_class.html", evcl=evcl)


@mod_results_view.route('/class_<id>_results.csv')
@check_and_apply_event
@check_is_registered
def class_as_csv(id):
    if not g.device.event_role.may_use_results:
        flash('Sie haben keine Berechtigung, hierauf zuzugreifen.', 'danger')
        return redirect(url_for('devices.index', event=g.event.slug))
    
    evcl = g.event.classes.filter_by(id=id).one_or_404()

    data = [()]
    field_names = (
        'Klasse',
        'Gruppe',
        'Platzierung',
        'Teilnehmer/in',
        'Verband'
    )

    for group in evcl.groups.filter_by(completed=True):
        for participant in group.placements():
            data.append((
                evcl.short_title,
                group.cut_title(),
                f"{participant.final_placement}.",
                participant.full_name,
                participant.association_name
            ))
        data.append(())

    # Ignore last empty tuple
    data = data[:-1]
    
    
    csv_io = io.StringIO()
    csvwriter = csv.writer(csv_io, delimiter=',', quotechar='\"')
    csvwriter.writerow(field_names)
    csvwriter.writerows(data)

    # Flask is stupid and only accepts BytesIO,
    # however csv is stupid too and only works with StringIO
    # so we need to convert the csv_io to mem_io
    mem_io = io.BytesIO()
    mem_io.write(csv_io.getvalue().encode())
    mem_io.seek(0)

    return send_file(mem_io, mimetype='text/csv')