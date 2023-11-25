from flask import Blueprint, render_template, flash, g, session, \
    request, redirect, url_for

from datetime import datetime as dt

from .event_manager import check_and_apply_event
from .devices import check_is_registered

from ..models import db, EventClass

mod_placement_view = Blueprint('mod_placement', __name__)

@mod_placement_view.context_processor
def provide_classes_query():
    return {
        "classes_query": g.event.classes.order_by(EventClass.begin_fighting,
                                                  EventClass.begin_placement.desc(),
                                                  EventClass.title)
    }

@mod_placement_view.route('/')
@check_and_apply_event
@check_is_registered
def index():
    if not g.device.event_role.may_use_placement_tool:
        flash('Sie haben keine Berechtigung, hierauf zuzugreifen.', 'danger')
        return redirect(url_for('devices.index', event=g.event.slug))

    return render_template("mod_placement/index.html")


@mod_placement_view.route('/class/<id>')
@check_and_apply_event
@check_is_registered
def for_class(id):
    if not g.device.event_role.may_use_placement_tool:
        flash('Sie haben keine Berechtigung, hierauf zuzugreifen.', 'danger')
        return redirect(url_for('devices.index', event=g.event.slug))

    event_class = g.event.classes.filter_by(id=id).one_or_404()

    if event_class.use_proximity_weight_mode:
        return render_template("mod_placement/for_class-proximity.html", event_class=event_class)
    else:
        return render_template("mod_placement/for_class-fixed.html", event_class=event_class)