# src/routes/superadmin.py

from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from src.models import User, Organisation
from src.db import db

superadmin = Blueprint('superadmin', __name__)

@superadmin.route('/superadmin', methods=['GET', 'POST'])
@login_required
def superadmin_dashboard():
    if not current_user.is_superadmin:  # Check if user is not a superadmin
        flash("You are not authorized to view this page.", "danger")
        return redirect(url_for('main.mainpage'))  # Redirect to the main page if not authorized

    organisations = Organisation.query.all()  # Superadmin can view all organizations
    users = User.query.all()  # Superadmin can view all users

    return render_template('superadmin_dashboard.html', organisations=organisations, users=users)