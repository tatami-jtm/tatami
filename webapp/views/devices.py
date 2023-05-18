from flask import Blueprint, render_template, abort, flash, g, session, request, redirect, url_for

from ..models import db, DeviceRegistration
from .event_manager import check_and_apply_event

import uuid
from datetime import datetime

devices_view = Blueprint('devices', __name__)


def check_is_registered(func):
    def inner_func(*args, **kwargs):
        if "device_token" in session:
            matching_registration = DeviceRegistration.query.filter_by(event=g.event,
                                                                       token=session["device_token"]).all()

            if len(matching_registration) == 1:    
                if (registration := matching_registration[0]).confirmed:
                    g.device = registration
                    return func(*args, **kwargs)
        
        return redirect(url_for('devices.register', event=g.event.slug))
    
    inner_func.__name__ = func.__name__
    return inner_func


@devices_view.route('/register')
@check_and_apply_event
def register():
    if "device_token" in session:
        matching_registration = DeviceRegistration.query.filter_by(event=g.event, token=session["device_token"]).all()

        if len(matching_registration) == 1:    
            if (registration := matching_registration[0]).confirmed:
                flash('Willkommen! Dieses Gerät wurde freigegeben.', 'success')
                return redirect(url_for('devices.index', event=g.event.slug))

            return render_template("devices/register.html", registration=registration)
        else:
            del session["device_token"]

    registration = DeviceRegistration(event=g.event)
    registration.token = str(uuid.uuid4())
    registration.registered_at = datetime.now()
    registration.confirmed = False
    registration.title = "Gerät " + registration.get_human_readable_code() + " - " + request.remote_addr

    db.session.add(registration)
    db.session.commit()
    
    session["device_token"] = registration.token

    return render_template("devices/register.html", registration=registration)

@devices_view.route('/')
@check_and_apply_event
@check_is_registered
def index():
    return render_template("devices/index.html")


@devices_view.route('/exit')
@check_and_apply_event
@check_is_registered
def exit():
    db.session.delete(g.device)
    db.session.commit()

    return redirect(url_for('splash'))