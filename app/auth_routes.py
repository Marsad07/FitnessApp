from werkzeug.security import generate_password_hash, check_password_hash
from app import db
from .models.user_accounts_model import User
from flask import Blueprint, request, render_template, session, flash, url_for, redirect

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

# This route is for the register form, GET=page for register form,
# POST = checks what was entered, then saves the new user if everything is fine
@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template("authentication/online_register/register_form.html")
    elif request.method == 'POST':
        # Read the values from form using request.form.get, .strip removes spaces from start/end,
        # so "" counts as empty
        username = request.form.get('username').strip()
        email = request.form.get('email').strip()
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        if not username or not email or not password or not confirm_password:
            flash('Please fill in every box')
            return redirect(url_for('auth.register'))

        if "@" not in email:
            flash('Please enter a valid email address')
            return redirect(url_for('auth.register'))

        if len(password) < 8:
            flash('Please enter a password that is at least 8 characters')
            return redirect(url_for('auth.register'))

        if confirm_password != password:
            flash('The passwords you entered do not match')
            return redirect(url_for('auth.register'))

        # DB looks for a user who already has this username/email
        existing_username = User.query.filter(User.username == username).first()
        if existing_username is not None:
            flash('Username already exists, enter a new username')
            return redirect(url_for('auth.register'))

        existing_email = User.query.filter(User.email == email).first()
        if existing_email is not None:
            flash('Email already exists, enter a new email address')
            return redirect(url_for('auth.register'))

        # Hash the password for security
        # And build new user
        password_hash = generate_password_hash(password)
        new_user = User(
            username=username,
            email=email,
            password_hash=password_hash,

        )

        # Adds user, saves it, sends user back to homepage with success message
        db.session.add(new_user)
        db.session.commit()
        flash('Registration Successful')
        return redirect(url_for('homepage'))

