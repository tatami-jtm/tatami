from flask import Blueprint, render_template, flash, g, session, \
    request, redirect, url_for

from datetime import datetime as dt

from .event_manager import check_and_apply_event, check_event_is_in_team_mode
from .devices import check_is_registered
from .mod_placement import provide_classes_query

from ..models import db, TeamRegistration

mod_team_building_view = Blueprint('mod_team_building', __name__)

mod_team_building_view.context_processor(provide_classes_query)

@mod_team_building_view.route('/')
@check_and_apply_event
@check_is_registered
@check_event_is_in_team_mode
def index():
    if not g.device.event_role.may_use_placement_tool:
        flash('Sie haben keine Berechtigung, hierauf zuzugreifen.', 'danger')
        return redirect(url_for('devices.index', event=g.event.slug))

    return render_template("mod_team_building/index.html")