from flask import Blueprint, render_template, request, redirect, url_for,current_app,flash, jsonify
from flask_login import login_user, logout_user,current_user,login_required
from werkzeug.security import check_password_hash
from src.models import User,Report, Manager
from src.db import db
from src.extensions import bcrypt
from werkzeug.utils import secure_filename
import os
from geopy.geocoders import Nominatim


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

        query = Report.query
        urgency = request.args.get('urgency')
        status = request.args.get('status')
        sort = request.args.get('sort')

        if status:
            if status == "approved":
                query = query.filter_by(is_approved=True)
            elif status == "pending":
                query = query.filter_by(is_approved=False)

        if urgency:
            if urgency == "low":
                query = query.filter(Report.average_score <= 30)
            elif urgency == "medium":
                query = query.filter(Report.average_score > 30, Report.average_score <= 60)
            elif urgency == "high":
                query = query.filter(Report.average_score > 60)

        if sort:
            if sort == "newest":
                query = query.order_by(Report.created_at.desc())
            elif sort == "oldest":
                query = query.order_by(Report.created_at.asc())

        reports = query.all()

        return render_template(
            'reports.html',
            reports=reports,
            is_super_admin=super_admin,
            urgency=urgency,
            status=status,
            sort=sort
        )
    else:
        flash('Access denied. Only managers or super admins can manage reports.', 'error')
        return redirect(url_for('main.mainpage'))


@report.route('/view_reports/<int:report_id>', methods=['GET', 'POST'])
@login_required
def manage_report(report_id):

    report = Report.query.get_or_404(report_id)
    super_admin = is_super_admin()
    manager = Manager.query.filter_by(user_id=current_user.uid).first()
    urgency = report.get_urgency()
    creator = User.query.filter_by(uid=report.creator_id).first()
    if request.method == 'POST':
        if manager or super_admin:

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
        else:
            flash('Access denied. Only managers can manage reports.', 'error')
            return redirect(url_for('main.mainpage'))
    lat, lon = map(str.strip, report.location.split(','))
    geolocator = Nominatim(user_agent="AFM")
    loc = geolocator.reverse(f"{lat}, {lon}")
    address = loc.address if loc else ""
    return render_template('report_details.html', current_user = current_user,report=report, manager=manager,is_super_admin=is_super_admin(), location = address,  urgency = urgency, creator_name = creator.username)


@report.route("/score_report/<int:report_id>", methods=['GET', 'POST'])
@login_required
def score_report(report_id):
    try:
        report = Report.query.get_or_404(report_id)  # Fetch the report
        manager = Manager.query.filter_by(user_id=current_user.uid).first()
        urgency = report.get_urgency()
        lat, lon = map(str.strip, report.location.split(','))
        geolocator = Nominatim(user_agent="AFM")

        try:
            loc = geolocator.reverse(f"{lat}, {lon}")
            address = loc.address if loc else f"Coordinates: {lat}, {lon}"

        except Exception as e:
            address = f"Coordinates: {lat}, {lon}"  # In case of any other error, show coordinates

        if request.method == 'POST':
            data = request.get_json()  # Get the JSON data from the frontend
            score_value = data['score']
            if not report.is_approved:
                report.add_score(current_user.uid, int(score_value))  # Add the score
                return jsonify({
                    'message': 'Score updated successfully',
                    'urgency': urgency  # Send back the updated score
                }), 200

        else:
            return render_template('report_details.html',
                                   report=report,
                                   manager=manager,
                                   is_super_admin=is_super_admin(),
                                   location=address,
                                   urgency = urgency, current_user = current_user)

    except Exception as e:
        return jsonify({"error": str(e)}), 500



