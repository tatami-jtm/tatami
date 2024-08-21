from .list_helper import *
from .schedule_helper import *
from .group_helper import *
from . import streaming_helper as streaming


def _get_or_create(cls, **options):
    gotten = cls.query.filter_by(**options).one_or_none()

    if gotten is None:
        gotten = cls(**options)
        db.session.add(gotten)
        db.session.commit()
    
    return gotten