from webapp.app import app, db
from flask_migrate import stamp

with app.app_context():
    db.create_all()
    stamp('migrations')

print("Database has been created. Start server and go to /setup to continue installation.")