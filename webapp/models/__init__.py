from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# autopep8: off
from .user import *
from .events import *
from .participants import *
from .matches import *
# autopep8: on
