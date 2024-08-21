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
    return make_connection().get(key)


def set_value(key, value):
    return make_connection().set(key, value)


def make_key(mat_id, question, element):
    return f'T<{mat_id}>:{question}:{element}'