from functools import wraps

from flask import abort, g, session


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if "user_id" not in session:
            abort(401)
        g.user_id = session["user_id"]
        g.tenant_id = session["tenant_id"]
        return view(*args, **kwargs)

    return wrapped
