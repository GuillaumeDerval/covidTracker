import os
from datetime import timedelta


class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'omhgzo!u"àçtuà'
    PERMANENT_SESSION_LIFETIME = timedelta(days=365)
