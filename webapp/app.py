from flask import Flask, render_template, request, flash, redirect, url_for
from flask_migrate import Migrate
from flask_security import Security, SQLAlchemyUserDatastore

from .config_base import SETTINGS
from . import setup_data

from .models import db, User, Role, Event
from .views import admin_view, eventmgr_view, devices_view, mod_scoreboard_view, mod_registrations_view, mod_weighin_view, mod_placement_view, mod_global_list_view, mod_list_view, mod_beamer_view

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
    'check_deliverability': (not app.debug and not SETTINGS['NEVER_VALIDATE_EMAIL_DNS'])
}

app.config['SECURITY_MSG_UNAUTHORIZED'] = (
    "Du hast nicht die Berechtigung, diese Funktion auszuführen.", 0)


user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security(app, user_datastore)


@app.route("/")
def splash():
    avail_events = Event.that_allows_registration()
    return render_template("index.html", avail_events=avail_events)


@app.route("/scoreboard")
def scoreboard():
    return render_template("scoreboard.html")


if SETTINGS['ALLOW_SETUP']:
    @app.route('/setup', methods=['GET', 'POST'])
    def setup():
        if request.method == 'POST':
            # Setup admin role
            setup_data.setup_roles()
            admin_role = Role.query.filter_by(name="platform_admin", is_admin=True).one()

            # Activate and adminify selected admin accounts
            for acct_id in request.form.getlist('admin-accts'):
                acct = User.query.get(int(acct_id))
                acct.active = True

                if admin_role not in acct.roles:
                    acct.roles.append(admin_role)
            
            db.session.commit()

            # Install event roles
            setup_data.setup_event_roles()

            # Possibly install template classes
            if "install-class-templates" in request.form:
                setup_data.setup_class_templates()

            flash("Installation erfolgreich abgeschlossen.", 'success')
            flash("ACHTUNG: Über das Installationsskript können beliebige Dritte vollen Administrationszugriff erhalten! Daher muss das Installationsskript wenn es nicht mehr benötigt wird SOFORT in der config.py wieder deaktiviert werden.", 'danger')

        return render_template("setup.html", user=User.query.all())


app.register_blueprint(admin_view, url_prefix='/admin')
app.register_blueprint(eventmgr_view, url_prefix='/event-manager/<event>')
app.register_blueprint(devices_view, url_prefix='/go/<event>')

app.register_blueprint(mod_scoreboard_view, url_prefix="/go/<event>/mod_scoreboard")
app.register_blueprint(mod_registrations_view, url_prefix="/go/<event>/mod_registrations")
app.register_blueprint(mod_weighin_view, url_prefix="/go/<event>/mod_weighin")
app.register_blueprint(mod_placement_view, url_prefix="/go/<event>/mod_placement")
app.register_blueprint(mod_global_list_view, url_prefix="/go/<event>/mod_global_list")
app.register_blueprint(mod_list_view, url_prefix="/go/<event>/mod_list")
app.register_blueprint(mod_beamer_view, url_prefix='/go/<event>/mod_beamer')