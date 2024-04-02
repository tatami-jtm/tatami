from flask import Blueprint, render_template, flash, g, session, \
    request, redirect, url_for

from datetime import datetime as dt

from .event_manager import check_and_apply_event
from .devices import check_is_registered

from ..models import db, Registration

mod_beamer_view = Blueprint('mod_beamer', __name__)

@mod_beamer_view.route('/')
@check_and_apply_event
@check_is_registered
def index():
    if not g.device.event_role.may_use_beamer:
        flash('Sie haben keine Berechtigung, hierauf zuzugreifen.', 'danger')
        return redirect(url_for('devices.index', event=g.event.slug))
    
    if g.device.position.is_mat:
        assigned_mats = [g.device.position]
    else:
        assigned_mats = g.event.device_positions.filter_by(is_mat=True).all()
    
    return render_template("mod_beamer/index.html", assigned_mats=assigned_mats)