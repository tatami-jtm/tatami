from flask import Blueprint, render_template, abort, flash, g, request, redirect, url_for
from flask_security import login_required, current_user

from ..models import db, Event, EventClass, DeviceRegistration, DevicePosition, EventRole

from datetime import datetime
import time

eventmgr_view = Blueprint('event_manager', __name__)


def check_and_apply_event(func):
    def inner_func(event, *args, **kwargs):
        event = Event.from_slug(event)

        g.event = event

        return func(*args, **kwargs)
    
    inner_func.__name__ = func.__name__
    return inner_func

def check_is_event_supervisor(func):
    def inner_func(*args, **kwargs):
        if not g.event.is_supervisor(current_user) and not current_user.has_privilege('create_tournaments'):
            abort(404)

        return func(*args, **kwargs)
    
    inner_func.__name__ = func.__name__
    return inner_func


@eventmgr_view.route('/')
@login_required
@check_and_apply_event
@check_is_event_supervisor
def index():
    return render_template("event-manager/index.html", stat={
        "mats": DevicePosition.query.filter_by(event=g.event, is_mat=True).count(),
        "classes": EventClass.query.filter_by(event=g.event).count()
    })


@eventmgr_view.route('/classes')
@login_required
@check_and_apply_event
@check_is_event_supervisor
def classes():
    return render_template("event-manager/classes/index.html")


@eventmgr_view.route('/devices')
@login_required
@check_and_apply_event
@check_is_event_supervisor
def devices():
    mat_pos = DevicePosition.query.filter_by(event=g.event, is_mat=True).order_by('position').all()
    admin_pos = DevicePosition.query.filter_by(event=g.event, is_mat=False).order_by('position').all()
    requests = DeviceRegistration.query.filter_by(event=g.event, confirmed=False).all()
    roles = EventRole.query.all()
    return render_template("event-manager/devices.html", mat_pos=mat_pos, roles=roles, admin_pos=admin_pos, requests=requests)


@eventmgr_view.route('/devices/<id>/update', methods=["POST"])
@login_required
@check_and_apply_event
@check_is_event_supervisor
def device_update(id):
    device = DeviceRegistration.query.filter_by(event=g.event, id=id).one_or_404()
    pos = DevicePosition.query.filter_by(event=g.event, id=request.form['position']).one_or_404()
    name = request.form['name']
    role = EventRole.query.filter_by(id=request.form['role']).one_or_404()

    device.position_id = pos.id
    device.title = name
    device.event_role_id = role.id

    if not device.confirmed:
        device.confirmed = True
        device.confirmed_at = datetime.now()
        device.registered_by_id = current_user.id

    db.session.commit()

    return redirect(url_for('event_manager.devices', event=g.event.slug))
    


@eventmgr_view.route('/devices/<id>/delete', methods=["GET", "POST"])
@login_required
@check_and_apply_event
@check_is_event_supervisor
def device_delete(id):
    device = DeviceRegistration.query.filter_by(event=g.event, id=id).one_or_404()
    db.session.delete(device)
    db.session.commit()

    return redirect(url_for('event_manager.devices', event=g.event.slug))


@eventmgr_view.route('/devices/allow-registration', methods=["POST"])
@login_required
@check_and_apply_event
@check_is_event_supervisor
def devices_allow_register():
    g.event.allow_device_registration = 'allow' in request.form
    db.session.commit()

    return redirect(url_for('event_manager.devices', event=g.event.slug))



@eventmgr_view.route('/devices/position/<id>/update', methods=["POST"])
@login_required
@check_and_apply_event
@check_is_event_supervisor
def device_position_update(id):
    device_position = DevicePosition.query.filter_by(event=g.event, id=id).one_or_404()
    name = request.form['name']
    is_mat = request.form['is_mat'] == '1'

    device_position.title = name
    device_position.is_mat = is_mat

    db.session.commit()

    return redirect(url_for('event_manager.devices', event=g.event.slug))
    


@eventmgr_view.route('/devices/position/<id>/delete', methods=["GET", "POST"])
@login_required
@check_and_apply_event
@check_is_event_supervisor
def device_position_delete(id):
    device_position = DevicePosition.query.filter_by(event=g.event, id=id).one_or_404()

    if device_position.devices.count():
        flash(f"Position {device_position.title} kann nicht gelöscht werden, da ihr noch Geräte zugewiesen sind.", 'danger')
        return redirect(url_for('event_manager.devices', event=g.event.slug))

    db.session.delete(device_position)
    db.session.commit()

    return redirect(url_for('event_manager.devices', event=g.event.slug))



@eventmgr_view.route('/devices/position/create', methods=["GET", "POST"])
@login_required
@check_and_apply_event
@check_is_event_supervisor
def device_position_create():
    device_position = DevicePosition(event=g.event)
    device_position.title = "Neue Position"
    device_position.is_mat = request.values.get("mat", '0') == '1'
    device_position.position = int(time.time())

    if device_position.is_mat:
        mat_count = DevicePosition.query.filter_by(event=g.event, is_mat=True).count()
        device_position.title = f"Matte {mat_count}"

    db.session.add(device_position)
    db.session.commit()

    return redirect(url_for('event_manager.devices', event=g.event.slug))