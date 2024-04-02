from webapp.app import app, db

with app.app_context():
    db.create_all()

print("Database has been created. Start server and go to /setup to continue installation.")