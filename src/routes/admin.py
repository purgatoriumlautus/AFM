from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from src.models import User, Manager, Agent
from src.db import db

admin = Blueprint('admin', __name__)

@admin.route('/admin', methods=['GET', 'POST'])
@login_required
def admin_dashboard():
    # Only allow access to super user (owner)
    if not current_user.is_owner:  # Check if user is not owner or manager
        flash("You are not authorized to view this page.", "danger")
        return redirect(url_for('main.mainpage'))  # Redirect to the main page if not authorized

    # Get all users
    users = User.query.all()

    if request.method == 'POST':
        user_id = request.form.get('user_id')
        role = request.form.get('role')

        # Assign the selected role to the user
        user = User.query.get(user_id)
        if user:
            if role == 'agent':
                # Assign Agent role
                agent = Agent(user_id=user.uid)
                db.session.add(agent)
                user.agent = agent
                user.manager = None
                user.is_owner = False
                db.session.commit()
                flash(f'Assigned Agent role to {user.username}', 'success')
            elif role == 'manager':
                # Assign Manager role
                manager = Manager(user_id=user.uid)
                db.session.add(manager)
                user.manager = manager
                user.agent = None
                user.is_owner = False
                db.session.commit()
                flash(f'Assigned Manager role to {user.username}', 'success')
            else:
                flash(f'Role assignment failed for {user.username}', 'danger')

        return redirect(url_for('admin.admin_dashboard'))

    return render_template('admin_dashboard.html', users=users)
