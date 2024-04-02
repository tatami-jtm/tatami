from flask import Blueprint, render_template, flash, g, session, \
    request, redirect, url_for

from datetime import datetime as dt

from .event_manager import check_and_apply_event
from .devices import check_is_registered

from ..models import db, Registration
from .. import helpers

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