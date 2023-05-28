from flask import Blueprint, render_template, flash, g, session, \
    request, redirect, url_for

from .event_manager import check_and_apply_event
from .devices import check_is_registered

mod_scoreboard_view = Blueprint('mod_scoreboard', __name__)

@mod_scoreboard_view.route('/standalone')
@check_and_apply_event
@check_is_registered
def standalone():
    if not g.device.event_role.may_use_scoreboard:
        flash('Sie haben keine Berechtigung, hierauf zuzugreifen.', 'danger')
        return redirect(url_for('devices.index', event=g.event.slug))

    return render_template("mod_scoreboard/standalone.html")