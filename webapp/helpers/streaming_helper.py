from ..config_base import SETTINGS
import redis

REDIS_CONNECTION = None


def is_streaming_enabled():
    return SETTINGS['STREAMING_REDIS'] is not None


def make_connection():
    global REDIS_CONNECTION

    if REDIS_CONNECTION is not None:
        return REDIS_CONNECTION
    
    if not is_streaming_enabled():
        return None
    
    redis_conf = SETTINGS['STREAMING_REDIS']
    
    REDIS_CONNECTION = redis.Redis(
        host=redis_conf['host'],
        port=redis_conf['port'],
        db=redis_conf['db'],
        decode_responses=True
    )

    return REDIS_CONNECTION

def get_value(key):
    conn = make_connection()
    if conn:
        return make_connection().get(key)


def set_value(key, value):
    conn = make_connection()
    if conn:
        return make_connection().set(key, value)


def clear_value(key):
    conn = make_connection()
    if conn:
        return make_connection().delete(key)


def make_key(mat_id, question, element):
    return f'T<{mat_id}>:{question}:{element}'


def update_redis_for_current_match(mat, match):
    if match is not None:
        set_value(make_key(mat.id, 'current_match', 'exists'), 'true')
        set_value(make_key(mat.id, 'current_match', 'group_title'), match.group.title)
        set_value(make_key(mat.id, 'current_match', 'white.name'), match.white.full_name)
        set_value(make_key(mat.id, 'current_match', 'white.association'), match.white.association_name)
        set_value(make_key(mat.id, 'current_match', 'blue.name'), match.blue.full_name)
        set_value(make_key(mat.id, 'current_match', 'blue.association'), match.blue.association_name)
    else:
        clear_value(make_key(mat.id, 'current_match', 'exists'))

def update_redis_for_waiting_match(mat, match):
    if match is not None:
        set_value(make_key(mat.id, 'waiting_match', 'exists'), 'true')
        set_value(make_key(mat.id, 'waiting_match', 'group_title'), match.group.title)
        set_value(make_key(mat.id, 'waiting_match', 'white.name'), match.white.full_name)
        set_value(make_key(mat.id, 'waiting_match', 'white.association'), match.white.association_name)
        set_value(make_key(mat.id, 'waiting_match', 'blue.name'), match.blue.full_name)
        set_value(make_key(mat.id, 'waiting_match', 'blue.association'), match.blue.association_name)
    else:
        clear_value(make_key(mat.id, 'current_match', 'exists'))