from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_security import Security, SQLAlchemyUserDatastore

from .config_base import SETTINGS

from .models import db, User, Role
from .views import admin_view

app = Flask(__name__)
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

app.config['SECURITY_MSG_UNAUTHORIZED'] = (
    "Du hast nicht die Berechtigung, diese Funktion auszuführen.", 0)


user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security(app, user_datastore)




@app.route("/")
def splash():
    return render_template("index.html")


app.register_blueprint(admin_view, url_prefix='/admin')