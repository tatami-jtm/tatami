from flask import Blueprint, render_template, abort, redirect,\
    url_for, request, flash, jsonify
from flask_security import login_required, current_user

from ..models import db, User, Role, Event, EventClass, ListSystem, ListSystemRule

from ..helpers import _get_or_create

from datetime import datetime

admin_view = Blueprint('admin', __name__)


@admin_view.route('/')
@login_required
def index():
    events = current_user.get_all_supervised_events(in_the_future=True)
    return render_template("admin/index.html", events=events)


@admin_view.route('/toggle-display-mode-preference')
@login_required
def toggle_display_mode_preference():
    current_user.prefers_dark_mode = not current_user.prefers_dark_mode
    db.session.commit()

    flash('Anzeigemodus erfolgreich aktualisiert.', 'success')

    return redirect(url_for('admin.index'))


@admin_view.route('/user')
@login_required
def user():
    if not current_user.has_privilege('manage_users'):
        abort(404)

    all_user = User.query.all()

    return render_template("admin/user/users.html", all_user=all_user)


@admin_view.route('/user/me')
@login_required
def edit_user_me():
    return redirect(url_for('admin.edit_user', id=current_user.id))


@admin_view.route('/user/<int:id>')
@login_required
def edit_user(id):
    if not (current_user.has_privilege(
            'manage_users') or current_user.id == id):
        abort(404)

    user = User.query.get_or_404(id)
    roles = Role.query.order_by(Role.is_admin.desc(), Role.name).all()

    return render_template("admin/user/edit.html", user=user, roles=roles)


@admin_view.route('/user/<int:id>', methods=['POST'])
@login_required
def update_user(id):
    if not (current_user.has_privilege(
            'manage_users') or current_user.id == id):
        abort(404)

    user = User.query.get_or_404(id)
    roles = Role.query.order_by(Role.is_admin.desc(), Role.name).all()

    user.display_name = request.form['display_name']
    user.email = request.form['email']

    if request.form['password']:
        user.password = request.form['password']

    if current_user.has_privilege('manage_users'):
        selected_role_ids = list(
            map(Role.query.get, request.form.getlist('roles')))
        for role in roles:
            if role.is_admin and not current_user.has_privilege('admin'):
                continue
            if role.may_manage_users and not current_user.has_privilege(
                    'manage_users'):
                continue
            if role.may_create_tournaments and not current_user.has_privilege(
                    'create_tournaments'):
                continue
            if role.may_alter_presets and not current_user.has_privilege(
                    'may_alter_presets'):
                continue

            if (role in selected_role_ids) and (role not in user.roles):
                user.roles.append(role)
            elif (role not in selected_role_ids) and (role in user.roles):
                user.roles.remove(role)

    db.session.commit()
    flash('Änderungen erfolgreich gespeichert.', 'success')

    return redirect(url_for('admin.edit_user', id=user.id))


@admin_view.route('/user/toggle-active/<int:id>', methods=['POST'])
@login_required
def user_toggle_active(id):
    if not current_user.has_privilege('manage_users'):
        abort(404)

    if id == current_user.id:
        flash('Fehler: eigenes Konto kann nicht deaktiviert werden', 'danger')
        return redirect(url_for('admin.user'))

    user = User.query.get_or_404(id)
    user.active = not user.active
    db.session.commit()

    if user.active:
        flash('Konto erfolgreich aktiviert.', 'success')
    else:
        flash('Konto erfolgreich deaktiviert.', 'success')

    return redirect(url_for('admin.user'))


@admin_view.route('/user/roles')
@login_required
def roles():
    if not current_user.has_privilege('manage_users'):
        abort(404)

    all_roles = Role.query.order_by(Role.is_admin.desc(), Role.name).all()

    return render_template("admin/user/roles.html", all_roles=all_roles)


@admin_view.route('/user/roles/new')
@login_required
def new_role():
    if not current_user.has_privilege('manage_users'):
        abort(404)

    role = Role()
    role.name = 'new_role'

    return render_template(
        "admin/user/edit_role.html",
        role=role,
        action='new')


@admin_view.route('/user/roles/new', methods=['POST'])
@login_required
def create_role():
    if not current_user.has_privilege('manage_users'):
        abort(404)

    role = Role()

    role.name = request.form['name']
    role.description = request.form['description']
    role.is_admin = False
    role.may_manage_users = False
    role.may_create_tournaments = False
    role.may_alter_presets = False

    if current_user.has_privilege('admin'):
        role.is_admin = 'is_admin' in request.form

    if current_user.has_privilege('manage_users'):
        role.may_manage_users = 'may_manage_users' in request.form

    if current_user.has_privilege('create_tournaments'):
        role.may_create_tournaments = 'may_create_tournaments' in request.form

    if current_user.has_privilege('alter_presets'):
        role.may_alter_presets = 'may_alter_presets' in request.form

    db.session.add(role)
    db.session.commit()
    flash('Rolle erfolgreich erzeugt.', 'success')

    return redirect(url_for('admin.edit_role', id=role.id))


@admin_view.route('/user/roles/<int:id>')
@login_required
def edit_role(id):
    if not current_user.has_privilege('manage_users'):
        abort(404)

    role = Role.query.get_or_404(id)

    return render_template(
        "admin/user/edit_role.html",
        role=role,
        action='edit')


@admin_view.route('/user/roles/<int:id>', methods=['POST'])
@login_required
def update_role(id):
    if not current_user.has_privilege('manage_users'):
        abort(404)

    role = Role.query.get_or_404(id)

    role.name = request.form['name']
    role.description = request.form['description']

    if current_user.has_privilege('admin'):
        role.is_admin = 'is_admin' in request.form

    if current_user.has_privilege('manage_users'):
        role.may_manage_users = 'may_manage_users' in request.form

    if current_user.has_privilege('create_tournaments'):
        role.may_create_tournaments = 'may_create_tournaments' in request.form

    if current_user.has_privilege('alter_presets'):
        role.may_alter_presets = 'may_alter_presets' in request.form

    db.session.commit()
    flash('Änderungen erfolgreich gespeichert.', 'success')

    return redirect(url_for('admin.edit_role', id=role.id))


@admin_view.route('/events')
@login_required
def events():
    current_user_events = events = current_user.get_all_supervised_events()

    if current_user.has_privilege('create_tournaments'):
        events = Event.query.all()

    return render_template(
        "admin/event/index.html",
        events=events,
        current_user_events=current_user_events)


@admin_view.route('/event/new')
@login_required
def new_event():
    if not current_user.has_privilege('create_tournaments'):
        abort(404)

    event = Event()
    roles = Role.query.order_by(Role.is_admin.desc(), Role.name).all()
    users = User.query.all()

    return render_template(
        "admin/event/new.html",
        event=event,
        roles=roles,
        users=users)


@admin_view.route('/event/new', methods=['POST'])
@login_required
def create_event():
    if not current_user.has_privilege('create_tournaments'):
        abort(404)

    role = Role.query.get_or_404(request.form['supervising_role'])
    user = User.query.get_or_404(request.form['supervising_user'])
    first_day = request.form['event_day'] + "T06:00"
    last_day = request.form['event_day'] + "T23:00"

    event = Event()
    event.slug = role.name + ':' + request.form['slug_part']
    event.title = request.form['title']
    event.first_day = datetime.fromisoformat(first_day)
    event.last_day = datetime.fromisoformat(last_day)
    event.supervising_role = role
    event.supervising_user = user

    db.session.add(event)
    db.session.commit()

    for rng, system in [
        ((1, 1), 'single'),
        ((2, 2), 'bestof3'),
        ((3, 3), 'pool3'),
        ((4, 4), 'pool4'),
        ((5, 5), 'pool5'),
        ((6, 8), 'doublepool8'),
        ((9, 16), 'ko16'),
        ((17, 32), 'ko32'),
    ]:
        system = ListSystem.all_enabled().filter_by(list_file=system).one_or_none()

        _get_or_create(ListSystemRule, event=event, minimum=rng[0], maximum=rng[1], system=system)

    flash(f'Erfolg: Veranstaltung {event.slug} wurde erstellt!', 'success')
    event.log(current_user.qualified_name(), 'DEBUG', 'Veranstaltung angelegt.')

    return redirect(url_for('admin.index'))


@admin_view.route("/templates")
@login_required
def presets():
    if not current_user.has_privilege('alter_presets'):
        abort(404)

    event_classes = EventClass.query.filter_by(is_template=True).order_by(EventClass.template_name).all()

    return render_template(
        "admin/presets.html",
        event_classes=event_classes)


@admin_view.route("/template/event_class/<id>")
@login_required
def event_class_template(id):
    event_class = EventClass.query.filter_by(id=id, is_template=True).one_or_404()

    return jsonify({
        "title": event_class.template_name,
        "short_title": event_class.short_title,
        "fighting_time": event_class.fighting_time,
        "golden_score_time": event_class.golden_score_time,
        "between_fights_time": event_class.between_fights_time,
        "use_proximity_weight_mode": event_class.use_proximity_weight_mode,
        "default_maximal_proximity": event_class.default_maximal_proximity,
        "proximitiy_uses_percentage_instead_of_absolute": event_class.proximitiy_uses_percentage_instead_of_absolute,
        "default_maximal_size": event_class.default_maximal_size,
        "weight_generator": event_class.weight_generator.split("\n") if event_class.weight_generator else [],
    })