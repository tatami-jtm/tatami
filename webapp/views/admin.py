from flask import Blueprint
from flask_security import login_required

admin_view = Blueprint('admin', __name__)

@admin_view.route('/')
@login_required
def index():
    return "HELLO, ADMINS!"