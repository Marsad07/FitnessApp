from werkzeug.security import generate_password_hash, check_password_hash
from app import db
from flask import Blueprint, request, render_template, session, flash, url_for, redirect

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

# This route is for the register form, GET=page for register form, POST="posted" for now
@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template("authentication/online_register/register_form.html")
    elif request.method == 'POST':
        return "posted"

