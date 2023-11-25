from flask import Blueprint, render_template, flash, g, session, \
    request, redirect, url_for

from datetime import datetime as dt

from .event_manager import check_and_apply_event
from .devices import check_is_registered

from ..models import db, EventClass

mod_placement_view = Blueprint('mod_placement', __name__)

@mod_placement_view.route('/')
@check_and_apply_event
@check_is_registered
def index():
    if not g.device.event_role.may_use_placement_tool:
        flash('Sie haben keine Berechtigung, hierauf zuzugreifen.', 'danger')
        return redirect(url_for('devices.index', event=g.event.slug))

    classes_query = g.event.classes.order_by(EventClass.begin_fighting, EventClass.begin_placement.desc(), EventClass.title)

    return render_template("mod_placement/index.html", classes_query=classes_query)