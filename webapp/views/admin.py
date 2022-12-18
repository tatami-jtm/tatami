from flask import Blueprint, render_template
from flask_security import login_required

admin_view = Blueprint('admin', __name__)

@admin_view.route('/')
@login_required
def index():
    return render_template("admin/index.html")