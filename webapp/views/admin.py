from flask import Blueprint, render_template, abort, redirect, url_for, request, flash
from flask_security import login_required, current_user

from ..models import db, User, Role

admin_view = Blueprint('admin', __name__)


@admin_view.route('/')
@login_required
def index():
    return render_template("admin/index.html")


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
    if not (current_user.has_privilege('manage_users') or current_user.id == id):
        abort(404)

    user = User.query.get_or_404(id)
    roles = Role.query.order_by(Role.is_admin.desc(), Role.name).all()

    return render_template("admin/user/edit.html", user=user, roles=roles)


@admin_view.route('/user/<int:id>', methods=['POST'])
@login_required
def update_user(id):
    if not (current_user.has_privilege('manage_users') or current_user.id == id):
        abort(404)

    user = User.query.get_or_404(id)
    roles = Role.query.order_by(Role.is_admin.desc(), Role.name).all()

    user.display_name = request.form['display_name']
    user.email = request.form['email']

    if request.form['password']:
        user.password = request.form['password']

    if current_user.has_privilege('manage_users'):
        selected_role_ids = list(map(Role.query.get, request.form.getlist('roles')))
        for role in roles:
            if role.is_admin and not current_user.has_privilege('admin'):
                continue
            if role.may_manage_users and not current_user.has_privilege('manage_users'):
                continue
            if role.may_create_tournaments and not current_user.has_privilege('create_tournaments'):
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


@admin_view.route('/user/roles/<int:id>')
@login_required
def edit_role(id):
    if not current_user.has_privilege('manage_users'):
        abort(404)

    role = Role.query.get_or_404(id)

    return render_template("admin/user/edit_role.html", role=role)


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


    db.session.commit()
    flash('Änderungen erfolgreich gespeichert.', 'success')

    return redirect(url_for('admin.edit_role', id=role.id))