from flask import Blueprint, render_template, abort, redirect,\
    url_for, request, flash, jsonify
from flask_security import login_required, current_user

from ..models import db, User, Role, Event, EventClass, ListSystem, \
    ListSystemRule, HelpRequest, SystemMessage, ScoreboardRuleset

from ..helpers import _get_or_create

from datetime import datetime
import json

admin_view = Blueprint('admin', __name__)

@admin_view.context_processor
def inject_support_tickets():
    if current_user.has_privilege('admin'):
        return {
            "open_support_tickets": HelpRequest.query.filter_by(resolved=False).count()
        }
    else:
        return {
            "open_support_tickets": HelpRequest.query.filter_by(resolved=False, escalated=False).count()
        }


@admin_view.route('/')
@login_required
def index():
    events = current_user.get_all_supervised_events(in_the_future=True)
    system_messages = SystemMessage.that_are_not_removed()
    return render_template("admin/index.html", events=events, system_messages=system_messages)


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
            if role.is_support and not current_user.has_privilege(
                    'support'):
                continue
            if role.may_manage_users and not current_user.has_privilege(
                    'manage_users'):
                continue
            if role.may_create_tournaments and not current_user.has_privilege(
                    'create_tournaments'):
                continue
            if role.may_alter_presets and not current_user.has_privilege(
                    'alter_presets'):
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
    role.is_support = False
    role.may_manage_users = False
    role.may_create_tournaments = False
    role.may_alter_presets = False

    if current_user.has_privilege('admin'):
        role.is_admin = 'is_admin' in request.form

    if current_user.has_privilege('manage_users'):
        role.may_manage_users = 'may_manage_users' in request.form

    if current_user.has_privilege('support'):
        role.is_support = 'is_support' in request.form

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

    if current_user.has_privilege('support'):
        role.is_support = 'is_support' in request.form

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

    if current_user.has_privilege('admin'):
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
    scoreboard_rulesets = ScoreboardRuleset.query.order_by(ScoreboardRuleset.is_default.desc(), ScoreboardRuleset.title).all()

    return render_template(
        "admin/presets.html",
        event_classes=event_classes,
        scoreboard_rulesets=scoreboard_rulesets)


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
        "proximity_uses_percentage_instead_of_absolute": event_class.proximity_uses_percentage_instead_of_absolute,
        "default_maximal_size": event_class.default_maximal_size,
        "weight_generator": event_class.weight_generator.split("\n") if event_class.weight_generator else [],
    })


@admin_view.route("/templates/scoreboard/<id>", methods=['GET', 'POST'])
@login_required
def scoreboard_preset(id):
    if not current_user.has_privilege('alter_presets'):
        abort(404)

    scoreboard_ruleset = ScoreboardRuleset.query.filter_by(id=id).one_or_404()

    if request.method == 'POST':
        scoreboard_ruleset.title = request.form['title']
        scoreboard_ruleset.enabled = 'enabled' in request.form
        scoreboard_ruleset.is_default = 'is_default' in request.form

        try:
            scoreboard_ruleset.rules = json.dumps(json.loads(request.form['rules']), indent=4)
        except:
            scoreboard_ruleset.rules = request.form['rules']
            flash("Regelwerk wurde nicht gespeichert. Grund: JSON nicht wohlgeformt.", 'danger')
        else:
            db.session.commit()
            flash("Regelwerk wurde erfolgreich gespeichert.", 'success')

    return render_template(
        "admin/scoreboard_rulesets/edit.html",
        scoreboard_ruleset=scoreboard_ruleset, action='edit')


@admin_view.route("/templates/scoreboard/new", methods=['GET', 'POST'])
@login_required
def new_scoreboard_preset():
    if not current_user.has_privilege('alter_presets'):
        abort(404)

    scoreboard_ruleset = ScoreboardRuleset()

    if request.method == 'POST':
        scoreboard_ruleset.title = request.form['title']
        scoreboard_ruleset.enabled = 'enabled' in request.form
        scoreboard_ruleset.is_default = 'is_default' in request.form

        try:
            scoreboard_ruleset.rules = json.dumps(json.loads(request.form['rules']), indent=4)
        except:
            scoreboard_ruleset.rules = request.form['rules']
            flash("Regelwerk wurde nicht gespeichert. Grund: JSON nicht wohlgeformt.", 'danger')
        else:
            db.session.add(scoreboard_ruleset)
            db.session.commit()
            flash("Regelwerk wurde erfolgreich gespeichert.", 'success')

            return redirect(url_for('admin.scoreboard_preset', id=scoreboard_ruleset.id))

    return render_template(
        "admin/scoreboard_rulesets/edit.html",
        scoreboard_ruleset=scoreboard_ruleset, action='new')


@admin_view.route('/support/new', methods=['GET', 'POST'])
@login_required
def new_support():

    if request.method == 'POST':
        db.session.add(HelpRequest(
            user=current_user,
            resolution='',
            created_at=datetime.now(),
            resolved=False,
            escalated=False,
            resolved_at=None,
            description=request.form['description']
        ))

        db.session.commit()

        flash("Ihre Problemmeldung wurde angelegt. Wir melden uns bald bei Ihnen.", 'success')

        return redirect(url_for('admin.index'))
    
    return render_template("admin/support/new.html")


@admin_view.route('/support')
@login_required
def support_tickets():
    if not current_user.has_privilege('support'):
        abort(404)

    support_tickets = HelpRequest.query.filter_by(resolved=False)
    support_tickets = support_tickets.order_by(HelpRequest.escalated.desc(), HelpRequest.created_at.asc())

    if not current_user.has_privilege('admin'):
        support_tickets = support_tickets.filter_by(escalated=False)

    support_tickets = support_tickets.all()
    
    return render_template("admin/support/tickets.html", support_tickets=support_tickets)


@admin_view.route('/support/<id>/resolve', methods=['POST'])
@login_required
def resolve_ticket(id):
    if not current_user.has_privilege('support'):
        abort(404)

    support_ticket = HelpRequest.query.filter_by(resolved=False, id=id).one_or_404()

    support_ticket.resolved = True
    support_ticket.resolved_at = datetime.now()
    support_ticket.resolution = request.form['resolution']

    db.session.commit()

    return redirect(url_for('admin.support_tickets'))


@admin_view.route('/support/<id>/escalate', methods=['POST'])
@login_required
def escalate_ticket(id):
    if not current_user.has_privilege('support'):
        abort(404)

    support_ticket = HelpRequest.query.filter_by(resolved=False, id=id).one_or_404()
    support_ticket.escalated = True
    db.session.commit()

    return redirect(url_for('admin.support_tickets'))


@admin_view.route('/messages')
@login_required
def messages():
    if not current_user.has_privilege('admin'):
        abort(404)

    messages = SystemMessage.query.filter_by(removed=False)
    
    return render_template("admin/messages/index.html", messages=messages)


@admin_view.route('/messages/<id>', methods=['GET', 'POST'])
@login_required
def message(id):
    if not current_user.has_privilege('admin'):
        abort(404)

    message = SystemMessage.query.filter_by(id=id).one_or_404()

    if request.method == 'POST':
        message.description = request.form['description']

        if request.form['user_id'] == '':
            message.user_id = None
        else:
            message.user_id = User.query.get_or_404(request.form['user_id']).id

        db.session.commit()

        flash('Systemmeldung erfolgreich gespeichert.', 'success')

    users = User.query.all()
    
    return render_template("admin/messages/edit.html", message=message, action='edit', users=users)


@admin_view.route('/messages/new', methods=['GET', 'POST'])
@login_required
def new_message():
    if not current_user.has_privilege('admin'):
        abort(404)

    message = SystemMessage(
        created_at=datetime.now(),
        removed=False,
        removed_at=None,
        user=current_user
    )

    if request.method == 'POST':
        message.description = request.form['description']

        if request.form['user_id'] == '':
            message.user_id = None
        else:
            message.user_id = User.query.get_or_404(request.form['user_id']).id

        db.session.add(message)
        db.session.commit()

        flash('Systemmeldung erfolgreich angelegt.', 'success')

        return redirect(url_for('admin.message', id=message.id))

    users = User.query.all()
    
    return render_template("admin/messages/edit.html", message=message, action='new', users=users)


@admin_view.route('/messages/<id>/delete', methods=['POST'])
@login_required
def delete_message(id):
    if not current_user.has_privilege('admin'):
        abort(404)

    message = SystemMessage(
        created_at=datetime.now(),
        removed=False,
        removed_at=None,
        user=current_user
    )

    message = SystemMessage.query.filter_by(id=id).one_or_404()
    message.removed = True
    message.removed_at = datetime.now()

    db.session.commit()

    flash('Systemmeldung erfolgreich gelöscht.', 'success')

    return redirect(url_for('admin.messages'))