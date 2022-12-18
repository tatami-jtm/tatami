from flask import Blueprint, render_template, abort
from flask_security import login_required, current_user

from ..models import db, User, Role

admin_view = Blueprint('admin', __name__)


@admin_view.route('/')
@login_required
def index():
    return render_template("admin/index.html")


@admin_view.route('/user')
@login_required
def user():
    if not current_user.has_privilege('manage_users'):
        abort(404)

    all_user = User.query.all()

    return render_template("admin/user/index.html", all_user=all_user)
