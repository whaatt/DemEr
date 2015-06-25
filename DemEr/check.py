from DemEr import app
from flask import session
import functools

def loggedIn(error):
    def decorator(fn):
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            if 'user' not in session:
                return error #None or false
            else: return fn(*args, **kwargs)
        return wrapper
    return decorator

#loggedIn decorator should
#always come before this
def ownership(error):
    def decorator(fn):
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            if not session['user']['owner']:
                return error #None or false
            else: return fn(*args, **kwargs)
        return wrapper
    return decorator
