from flask import Blueprint, render_template, flash, g, session, \
    request, redirect, url_for, abort, jsonify
from flask_security import current_user

from ..models import db, DeviceRegistration, EventRole, DevicePosition
from .event_manager import check_and_apply_event

import uuid
from datetime import datetime

devices_view = Blueprint('devices', __name__)


def _check_if_registration_is_not_required():
    return current_user.is_authenticated and \
        (g.event.is_supervisor(current_user) or \
         current_user.has_privilege('admin'))

def check_is_registered(func):
    def inner_func(*args, **kwargs):
        if "device_token" in session:
            matching_registration = DeviceRegistration.query.filter_by(
                event=g.event, token=session["device_token"]).all()

            if len(matching_registration) == 1:
                if (registration := matching_registration[0]).confirmed:
                    g.device = registration
                    g.deviceless = False
                    return func(*args, **kwargs)

        if _check_if_registration_is_not_required():
            g.device = DeviceRegistration()
            g.device.title = current_user.qualified_name()
            g.device.is_admin = True
            g.device.event_role = EventRole.administrative()
            g.device.position = DevicePosition.administrative()
            g.deviceless = False
            return func(*args, **kwargs)

        return redirect(url_for('devices.register', event=g.event.slug))

    inner_func.__name__ = func.__name__
    return inner_func


@devices_view.route('/register')
@check_and_apply_event
def register():
    if _check_if_registration_is_not_required():
        return redirect(url_for('devices.index', event=g.event.slug))

    if "device_token" in session:
        matching_registration = DeviceRegistration.query.filter_by(
            event=g.event, token=session["device_token"]).all()

        if len(matching_registration) == 1:
            if (registration := matching_registration[0]).confirmed:
                flash('Willkommen! Dieses Gerät wurde freigegeben.', 'success')
                return redirect(url_for('devices.index', event=g.event.slug))

            return render_template(
                "devices/register.html",
                registration=registration)
        else:
            del session["device_token"]

    if not g.event.allow_device_registration:
        abort(404)

    registration = _create_new_registration()

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


@devices_view.route('/api/register', methods=['GET', 'POST'])
@check_and_apply_event
def api_register():
    if "device_token" in session:
        matching_registration = DeviceRegistration.query.filter_by(
            event=g.event, token=session["device_token"]).all()

        if len(matching_registration) == 1:
            if (registration := matching_registration[0]).confirmed:
                return jsonify({
                    "result": "success"
                })

            return jsonify({
                "result": "pending",
                "auth_code": registration.get_human_readable_code()
            })
        else:
            del session["device_token"]

    if not g.event.allow_device_registration:
        abort(404)

    registration = _create_new_registration()

    return jsonify({
        "result": "pending",
        "auth_code": registration.get_human_readable_code()
    })

def _create_new_registration():
    registration = DeviceRegistration(event=g.event)
    registration.token = str(uuid.uuid4())
    registration.registered_at = datetime.now()
    registration.confirmed = False
    registration.title = "Gerät " + registration.get_human_readable_code() + \
        " - " + (request.access_route[-1] if len(request.access_route) else request.remote_addr)

    db.session.add(registration)
    db.session.commit()

    session["device_token"] = registration.token

    g.event.log(registration.title, 'DEBUG', f'Neues Gerät {registration.title} registriert, wartet auf Freigabe.')

    return registration