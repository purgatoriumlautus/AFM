from flask import Blueprint, render_template, request, redirect, url_for,current_app,flash
from flask_login import login_user, logout_user,current_user,login_required
from werkzeug.security import check_password_hash
from src.models import User,Report
from src.db import db
from src.extensions import bcrypt
from werkzeug.utils import secure_filename
import os



report = Blueprint("report",__name__)


@report.route('/create-report', methods = ['GET','POST'] )
@login_required
def create_report():
    
    if request.method == "GET":
        return(render_template('report.html'))
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
    return redirect(url_for('main.mainpage'))
    

@report.route('/view-reports', methods=['GET', 'POST'])
@login_required
def view_reports():
    if request.method == 'POST':
        report_id = request.form.get('report_id')  

        #
        report_to_delete = Report.query.get(report_id)

        if not report_to_delete:
            flash('Report not found.', 'error')
            return redirect(url_for('report.view_reports'))

       
        if report_to_delete.creator_id != current_user.uid:
            flash('You are not authorized to delete this report.', 'error')
            return redirect(url_for('report.view_reports'))

        # 
        db.session.delete(report_to_delete)
        db.session.commit()

        flash('Report deleted successfully.', 'success')
        return redirect(url_for('report.view_reports'))
    
    else:
        #
        reports = Report.query.all()
        return render_template('reports.html', reports=reports)