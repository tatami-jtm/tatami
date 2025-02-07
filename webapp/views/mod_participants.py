from flask import Blueprint, render_template, flash, g, session, \
    request, redirect, url_for

from .event_manager import check_and_apply_event
from .devices import check_is_registered

from ..models import db, Registration, EventClass

mod_participants_view = Blueprint('mod_participants', __name__)

@mod_participants_view.route('/')
@check_and_apply_event
@check_is_registered
def index():
    if not g.device.event_role.may_use_participants:
        flash('Sie haben keine Berechtigung, hierauf zuzugreifen.', 'danger')
        return redirect(url_for('devices.index', event=g.event.slug))
    
    class_filter = None
    filtered_class = None
    status_filter = request.values.get('status_filter', None)
    name_filter = request.values.get('name_filter', None)
    externalid_filter = request.values.get('externalid_filter', None)
    club_filter = request.values.get('club_filter', None)
    order_by = request.values.get('order_by', None)

    if request.values.get('class_filter', None):
        if request.values['class_filter'] not in ['pending', 'weighing_in', 'weighed_in', 'fighting', 'completed']:
            filtered_class = EventClass.query.filter_by(id=request.values['class_filter']).one_or_404()
            class_filter = 'single'
        else:
            class_filter = request.values['class_filter']

    filtered = filtered_class is not None or status_filter is not None or name_filter is not None or club_filter is not None or externalid_filter is not None
    query = Registration.filter(g.event, class_filter=class_filter, event_class=filtered_class,
                                status=status_filter, name=name_filter, club=club_filter, order_by=order_by,
                                external_id=externalid_filter)

    return render_template("mod_participants/index.html", filtered=filtered, class_filter=class_filter,
                           filtered_class=filtered_class, status_filter=status_filter, name_filter=name_filter,
                           club_filter=club_filter, externalid_filter=externalid_filter, order_by=order_by,
                           query=query)