from DemEr import app
from Flask import session
import functools

def loggedIn(error):
    def decorator(fn):
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            if not session['user']:
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
            if not session['owner']:
                return error #None or false
            else: return fn(*args, **kwargs)
        return wrapper
    return decorator
