from functools import wraps

from flask import session, redirect, url_for, flash


def login_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Checks the user is logged in before running the route
        user_id = session.get('user_id')
        if user_id is None:
            flash('Please log in to access this page')
            return redirect(url_for('auth.login'))

        # Runs original function
        return func(*args, **kwargs)
    return wrapper




