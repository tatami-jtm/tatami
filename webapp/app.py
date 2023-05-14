from flask import Flask, render_template
from flask_migrate import Migrate
from flask_security import Security, SQLAlchemyUserDatastore

from .config_base import SETTINGS

from .models import db, User, Role, Event
from .views import admin_view, eventmgr_view, devices_view

app = Flask(__name__, instance_path=SETTINGS['INSTANCE_PATH'])
app.config['SQLALCHEMY_DATABASE_URI'] = SETTINGS['SQL_URL']

# SQLAlchemy and Migrate
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)
migrate = Migrate(app, db)

app.db = db

# Security
app.config['SECRET_KEY'] = SETTINGS['SECRET_KEY']
app.config['SECURITY_PASSWORD_SALT'] = SETTINGS['SECRET_KEY']
app.config['SECURITY_URL_PREFIX'] = '/admin/auth'
app.config['SECURITY_CONFIRMABLE'] = False
app.config['SECURITY_REGISTERABLE'] = True
app.config['SECURITY_RECOVERABLE'] = True
app.config['SECURITY_POST_LOGIN_VIEW'] = 'admin.index'
app.config['SECURITY_SEND_REGISTER_EMAIL'] = False

app.config['SECURITY_EMAIL_VALIDATOR_ARGS'] = {
    'check_deliverability': (app.env == 'production' and not app.debug and
                             not SETTINGS['NEVER_VALIDATE_EMAIL_DNS'])
}

app.config['SECURITY_MSG_UNAUTHORIZED'] = (
    "Du hast nicht die Berechtigung, diese Funktion auszuführen.", 0)


user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security(app, user_datastore)


@app.route("/")
def splash():
    avail_events = Event.that_allows_registration()
    return render_template("index.html", avail_events=avail_events)


app.register_blueprint(admin_view, url_prefix='/admin')
app.register_blueprint(eventmgr_view, url_prefix='/event-manager/<event>')
app.register_blueprint(devices_view, url_prefix='/devices/<event>')