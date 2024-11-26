from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user,current_user, login_required
from src.models import User,Report,Organisation
from src.extensions import bcrypt
from src.db import db


main = Blueprint('main', __name__)


@main.route('/', methods=['GET', 'POST'])
def mainpage():
    reports = Report.all_reports()
    return render_template('mainpage.html', reports=reports, current_user=current_user)



@main.route('/join/<token>', methods=['GET'])
@login_required
def join_organization(token):
    organisation = Organisation.query.filter_by(token=token).first()
    if not organisation:
        flash("Invalid or expired invitation link.", "danger")
        return redirect(url_for('main.mainpage'))
    if current_user.organisation_id:
        flash("You are already part of an organization.", "danger")
        return redirect(url_for('main.mainpage'))
    current_user.organisation_id = organisation.id
    db.session.commit()

    flash(f"You have successfully joined the organization '{organisation.name}'.", "success")
    return redirect(url_for('main.mainpage'))