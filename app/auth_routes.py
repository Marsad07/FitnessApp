from werkzeug.security import generate_password_hash, check_password_hash
from app import db
from .models.user_accounts_model import User
from flask import Blueprint, request, render_template, session, flash, url_for, redirect

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

# This route is for the register form, GET = shows the register form,
# POST = checks what was entered, then saves the new user if everything is fine
@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template("authentication/online_register/register_form.html")

    # Reads the values from the form using request.form.get
    # (or "") turns a missing field (such as None) into an empty string so .strip() can't crash,
    # .strip() removes spaces from the start/end so "   " counts as empty
    username = (request.form.get('username') or "").strip()
    email = (request.form.get('email') or "").strip()
    password = request.form.get('password') or ""
    confirm_password = request.form.get('confirm_password') or ""

    # Checks each box isn't empty, with its own message
    if username == "":
        flash('Please enter a username', 'error')
        return redirect(url_for('auth.register'))

    if email == "":
        flash('Please enter an email', 'error')
        return redirect(url_for('auth.register'))

    if password == "" or confirm_password == "":
        flash('Please enter and confirm your password', 'error')
        return redirect(url_for('auth.register'))

    # Format checks
    if "@" not in email:
        flash('Please enter a valid email address', 'error')
        return redirect(url_for('auth.register'))

    if len(password) < 8:
        flash('Please enter a password that is at least 8 characters', 'error')
        return redirect(url_for('auth.register'))

    if confirm_password != password:
        flash('The passwords you entered do not match', 'error')
        return redirect(url_for('auth.register'))

    # Database checks - looks for a user who already has this username/email
    existing_username = User.query.filter(User.username == username).first()
    if existing_username is not None:
        flash('Username already exists, enter a new username', 'error')
        return redirect(url_for('auth.register'))

    existing_email = User.query.filter(User.email == email).first()
    if existing_email is not None:
        flash('Email already exists, enter a new email address', 'error')
        return redirect(url_for('auth.register'))

    # Hashes the password for security + builds the new user
    password_hash = generate_password_hash(password)
    new_user = User(
        username=username,
        email=email,
        password_hash=password_hash,
    )

    # Adds user, saves it, sends user back to homepage with success message
    db.session.add(new_user)
    db.session.commit()
    flash('Registration Successful', 'success')
    return redirect(url_for('homepage'))


# This route is for the login form, GET = shows the login form,
# POST = checks the email + password, then logs the user in if they match
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template("authentication/online_login/login_form.html")

    # Reads the values from the form using request.form.get, same checks that were used in register
    email = (request.form.get('email') or "").strip()
    password = request.form.get('password') or ""

    if email == "":
        flash('Please enter a valid email address', 'error')
        return redirect(url_for('auth.login'))

    if password == "":
        flash('Please enter a valid password', 'error')
        return redirect(url_for('auth.login'))

    # Looks for an account with this email through .first()
    # If there's no account, shows the same message as a wrong password
    user = User.query.filter(User.email == email).first()
    if user is None:
        flash('email or password is incorrect', 'error')
        return redirect(url_for('auth.login'))

    # Checks the typed password against the hash saved for this user
    # check_password_hash() re-hashes what was typed using the same salt as the stored hash,
    # then compares them - gives back True if they match, False if not
    verify_ps = check_password_hash(user.password_hash, password)
    if not verify_ps:
        flash('email or password is incorrect', 'error')
        return redirect(url_for('auth.login'))

    # If everything matched -> saves the user's id in the session so they stay logged in on every page
    session['user_id'] = user.id
    flash('Login Successful', 'success')
    return redirect(url_for('homepage'))


# This route logs the user out
@auth_bp.route('/logout', methods=['GET'])
def logout():
    # This removes user_id from the session through .pop()
    # (None means it won't crash if they were already logged out)
    session.pop('user_id', None)
    flash('Logged Out', 'info')
    return redirect(url_for('homepage'))
