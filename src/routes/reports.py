from flask import Blueprint, render_template, request, redirect, url_for,current_app,flash
from flask_login import login_user, logout_user,current_user,login_required
from werkzeug.security import check_password_hash
from src.models import User,Report, Manager
from src.db import db
from src.extensions import bcrypt
from werkzeug.utils import secure_filename
import os


def is_super_admin():
    super_admin_mail = os.getenv("ADMIN_EMAIL")
    return super_admin_mail == current_user.email



report = Blueprint("report",__name__)


@report.route('/create-report', methods = ['GET','POST'] )
@login_required
def create_report():
    if request.method == "GET":
        return(render_template('report.html',is_super_admin=is_super_admin()))
    location = request.form.get('location')
    description = request.form.get('description')
    photo = request.files.get('photo')
    user_id = current_user.uid
    print(user_id)
    if photo:
        filename = secure_filename(photo.filename)
        photo_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        photo.save(photo_path)
    else:
        filename = None

    report = Report(location=location, description=description,photo_file=filename,creator_id=user_id)
    db.session.add(report)
    db.session.commit()
    flash("Report successfully created",'success')
    return redirect(url_for('main.mainpage'))



@report.route('/view_reports', methods=['GET'])
@login_required
def view_reports():
    super_admin = is_super_admin()
    manager = Manager.query.filter_by(user_id=current_user.uid).first()
    if manager or super_admin:
        reports = Report.query.all()  # Optionally filter based on approval status
        return render_template('reports.html', reports=reports,is_super_admin=super_admin)
    else:
        flash(f'Access denied. Only managers can manage reports is', 'error')
        return redirect(url_for('main.mainpage'))



@report.route('/view_reports/<int:report_id>', methods=['GET', 'POST'])
@login_required
def manage_report(report_id):
    report = Report.query.get_or_404(report_id)
    super_admin = is_super_admin()
    # Check if the user is a manager
    manager = Manager.query.filter_by(user_id=current_user.uid).first()
    if request.method == 'POST':
        if manager or super_admin:
            flash('Access denied. Only managers can manage reports.', 'error')
            return redirect(url_for('main.mainpage'))
        
        action = request.form.get('action')
        
        if action == 'approve':
            report.is_approved = True
            report.approver_id = manager.id
            db.session.commit()
            flash('Report approved successfully.', 'success')
        
        elif action == 'delete':
            db.session.delete(report)
            db.session.commit()
            flash('Report deleted successfully.', 'success')
        return redirect(url_for('report.view_reports'))

    return render_template('report_details.html', report=report, manager=manager,is_super_admin=is_super_admin())
