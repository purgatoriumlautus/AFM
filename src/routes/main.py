from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user,current_user, login_required
from src.models import User,Report,Organisation, Manager, Agent
from src.extensions import bcrypt
from src.db import db
import os

main = Blueprint('main', __name__)

def is_super_admin():
    super_admin_mail = os.getenv("ADMIN_EMAIL")
    return super_admin_mail == current_user.email


@main.route('/', methods=['GET', 'POST'])
def mainpage():
    reports = Report.all_reports()
    if current_user.is_authenticated:
        if current_user.is_banned:
            return render_template('banned.html')
        return render_template('mainpage.html', reports=reports, current_user=current_user,
                               is_super_admin=is_super_admin())
    
    else:
        return render_template('mainpage.html', reports=reports, current_user=current_user)



@main.route('/join/<token>', methods=['GET'])
@login_required
def join_organization(token):
    organisation = Organisation.query.filter_by(token=token).first()
    if not organisation:
        flash("Invalid or expired invitation link.", "danger")
        return redirect(url_for('main.mainpage',is_super_admin=is_super_admin()))

    if current_user.organisation_id:
        flash("You are already part of an organization.", "danger")
        return redirect(url_for('main.mainpage',is_super_admin=is_super_admin()))

    if current_user.is_owner:
        flash("You are already the owner of an organization.", "danger")
        return redirect(url_for('main.mainpage',is_super_admin=is_super_admin()))

    # Ensure the user is not marked as an owner
    current_user.organisation_id = organisation.id
    current_user.is_owner = False  # Explicitly set is_owner to False
    db.session.commit()

    flash(f"You have successfully joined the organization '{organisation.name}'.", "success")
    return redirect(url_for('main.mainpage',is_super_admin=is_super_admin()))


@main.route('/dashboard', methods=['GET'])
@login_required
def see_dashboard():
    
    role = None
    task_data = []

    manager = Manager.query.filter_by(user_id=current_user.uid).first()
    if manager:
        role = "Manager"
        task_data = [{
            'title': task.name,
            'location': task.reports[0].location if task.reports else "0,0",
            'description': task.description,
            'status': task.status
        } for task in manager.tasks]

    agent = Agent.query.filter_by(user_id=current_user.uid).first()
    if agent:
        role = "Agent"
        task_data = [{
            'title': task.name,
            'location': task.reports[0].location if task.reports else "0,0",
            'description': task.description,
            'status': task.status
        } for task in agent.tasks]

    if role:
        return render_template("dashboard.html", tasks=task_data, user=current_user, role=role,is_super_admin=is_super_admin())

    flash("You are not authorized to view this page.", "danger")
    return redirect(url_for('main.mainpage'))