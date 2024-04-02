from webapp.app import db

db.create_all()
print("Database has been created. Start server and go to /setup to continue installation.")