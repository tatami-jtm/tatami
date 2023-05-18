from flask import Blueprint, render_template, abort, flash, g, session

from ..models import db, DeviceRegistration
from .event_manager import check_and_apply_event

import uuid
from datetime import datetime

devices_view = Blueprint('devices', __name__)


@devices_view.route('/register')
@check_and_apply_event
def register():
    if "device_token" in session:
        matching_registration = DeviceRegistration.query.filter_by(event=g.event, token=session["device_token"]).all()

        if len(matching_registration) == 1:    
            if (registration := matching_registration[0]).confirmed:
                abort(418)  # TODO: redirect to proper page

            return render_template("devices/register.html", registration=registration)
        else:
            del session["device_token"]

    registration = DeviceRegistration(event=g.event)
    registration.token = str(uuid.uuid4())
    registration.registered_at = datetime.now()
    registration.confirmed = False
    registration.title = "Gerät " + registration.get_human_readable_code()

    db.session.add(registration)
    db.session.commit()
    
    session["device_token"] = registration.token

    return render_template("devices/register.html", registration=registration)