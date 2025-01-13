from uuid import uuid4
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from src.models import User, Manager, Agent, Organisation
from src.db import db
import os

admin = Blueprint('admin', __name__)

def is_super_admin():
    super_admin_mail = os.getenv("ADMIN_EMAIL")
    return super_admin_mail == current_user.email


@admin.route('/admin', methods=['GET', 'POST'])
@login_required
def admin_dashboard():
    # Only allow access to super user (owner)
    is_admin = is_super_admin()
    if current_user.is_owner or is_admin:  # Check if user is not the owner
            # Redirect to the main page if not authorized

        # Get all users in the same organization as the current owner
        organisation = Organisation.query.filter_by(id=current_user.organisation_id).first()
        if not organisation:
            flash("You are not associated with any organization.", "danger")
            return redirect(url_for('main.mainpage'))

        # Filter users by organization ID
        users = User.query.filter_by(organisation_id=organisation.id).filter(User.is_owner == False).all()

        if request.method == 'POST':
            user_id = request.form.get('user_id')
            role = request.form.get('role')

            # Assign the selected role to the user
            user = User.query.get(user_id)
            if user and user.organisation_id == organisation.id:  # Ensure the user is in the same organization
                if role == 'agent' and not user.agent:
                    if user.manager:
                        db.session.delete(user.manager)
                        user.manager = None
                    # Assign Agent role
                    agent = Agent(user_id=user.uid)
                    db.session.add(agent)
                    user.agent = agent
                    user.manager = None
                    user.is_owner = False
                    db.session.commit()
                    flash(f'Assigned Agent role to {user.username}', 'success')

                elif role == 'manager' and not user.manager:
                    if user.agent:
                        db.session.delete(user.agent)
                        user.agent = None
                    # Assign Manager role
                    manager = Manager(user_id=user.uid)
                    db.session.add(manager)
                    user.manager = manager
                    user.agent = None
                    user.is_owner = False
                    db.session.commit()
                    flash(f'Assigned Manager role to {user.username}', 'success')
                else:
                    flash(f'Role is already assigned {user.username}', 'danger')
            else:
                flash("User is not part of your organization.", "danger")

            return redirect(url_for('admin.admin_dashboard'))
    else:
        flash("You don't have priviledges to create an organisation.", "danger")
        return redirect(url_for('main.mainpage'))
    # Generate invitation link
    invitation_link = url_for('main.join_organization', token=organisation.token, _external=True)
    return render_template('admin_dashboard.html', users=users, invitation_link=invitation_link,is_super_admin=is_super_admin(), organisation = organisation)


@admin.route('/create_organisation', methods=['GET', 'POST'])
@login_required
def create_organisation():
    is_admin = is_super_admin()
    if request.method == 'POST':
        if current_user.is_owner or is_admin: 
            
            organisation_name = request.form.get('organisation_name')
            if not organisation_name:
                flash("Organization name is required.", "danger")
                return redirect(url_for('admin.create_organisation'))  # Redirect back to create page
            if current_user.organisation_id:
                flash("You have already created an organization.", "danger")
                return redirect(url_for('admin.admin_dashboard'))
            
            owner = User.query.filter_by(email=current_user.email).first()

            organisation = Organisation(name=organisation_name, token=str(uuid4()), owner_id=owner.uid)
            db.session.add(organisation)
            db.session.commit()

            owner.organisation_id = organisation.id
            owner.is_owner = True
            db.session.commit()

            flash(f"Organization '{organisation_name}' created and {owner.username} is now the owner.", "success")

            return redirect(url_for('admin.admin_dashboard'))
        else:
            flash("You are not authorised to create an organisation.", "danger")
            return redirect(url_for('main.mainpage'))

    else:
        return render_template('add_organisation.html',is_super_admin=is_super_admin())
