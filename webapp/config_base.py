import os

if os.path.isfile("./config.py"):
    from .config import SETTINGS as custom_settings
else:
    custom_settings = {}

SETTINGS = {
    "SQL_URL": "sqlite:///tatami.db",
    "SECRET_KEY": "OVERWRITE ME IN CONFIG_BASE.PY!"
}

SETTINGS.update(custom_settings)