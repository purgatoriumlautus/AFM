from flask import Blueprint, render_template, request, redirect, url_for,current_app,flash, jsonify
from flask_login import login_user, logout_user,current_user,login_required
from werkzeug.security import check_password_hash
from src.models import User,Report, Manager, Organisation,TaskRequest
from src.db import db
from src.extensions import bcrypt
from werkzeug.utils import secure_filename
import os
from geopy.geocoders import Nominatim
from math import radians, cos, sin, sqrt, atan2

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
        urgency = request.args.get('urgency', default="all")
        status = request.args.get('status', default="all")
        sort = request.args.get('sort', default="newest")
        min_distance = request.args.get('min_distance', type=float, default=0)
        max_distance = request.args.get('max_distance', type=float, default=float('inf'))
        user_lat = request.args.get('latitude', type=float)
        user_lon = request.args.get('longitude', type=float)

        if status != "all":
            query = query.filter(Report.status == status)
        if urgency != "all":
            if urgency == "low":
                query = query.filter(Report.average_score <= 30)
            elif urgency == "medium":
                query = query.filter(Report.average_score > 30, Report.average_score <= 60)
            elif urgency == "high":
                query = query.filter(Report.average_score > 60)
        if sort == "newest":
            query = query.order_by(Report.created_at.desc())
        elif sort == "oldest":
            query = query.order_by(Report.created_at.asc())
        reports = query.all()

        if user_lat is not None and user_lon is not None:
            def calculate_distance(lat1, lon1, lat2, lon2):
                R = 6371
                dLat = radians(lat2 - lat1)
                dLon = radians(lon2 - lon1)
                a = sin(dLat / 2) * sin(dLat / 2) + cos(radians(lat1)) * cos(radians(lat2)) * sin(dLon / 2) * sin(
                    dLon / 2)
                c = 2 * atan2(sqrt(a), sqrt(1 - a))
                return R * c

            filtered_reports = []
            for report in reports:
                if report.location:
                    try:
                        report_lat, report_lon = map(float, report.location.split(','))
                        distance = calculate_distance(user_lat, user_lon, report_lat, report_lon)
                        if min_distance <= distance <= max_distance:
                            filtered_reports.append(report)
                    except ValueError:
                        continue
            reports = filtered_reports
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

            if action == 'resolve' and report.status == 'OPEN':
                unresolved_tasks = [task for task in report.tasks if task.status != 'RESOLVED']
                if unresolved_tasks:
                    flash('Cannot resolve the report because there are unresolved tasks.', 'danger')
                else:
                    report.status = 'RESOLVED'
                    db.session.commit()
                    flash('Report marked as resolved.', 'success')

            elif action == 'open' and report.status == 'RESOLVED' or report.status == '':
                report.status = 'OPEN'
                db.session.commit()
                flash('Report status changed to OPEN.', 'success')
            elif action == 'delete':
                for task in report.tasks:
                    db.session.delete(task)
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

    return render_template('report_details.html', current_user=current_user, report=report, manager=manager,
                           is_super_admin=is_super_admin(), location=address, urgency=urgency,
                           creator_name=creator.username)

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

@report.route("/report_tasks/<int:report_id>", methods=['GET', 'POST'])
@login_required
def report_tasks(report_id):
    super_admin = is_super_admin()
    manager = Manager.query.filter_by(user_id=current_user.uid).first()
    report = Report.query.get_or_404(report_id)

    # Check if the user is a manager or a super admin
    if manager or super_admin:
        # Get the selected organization and sort order from the request
        organisation_id = request.args.get('organisation')
        sort_order = request.args.get('sort', 'newest')  # Default to 'newest'

        # Get all tasks for the report
        tasks = report.tasks

        # Filter tasks by organization if provided
        tasks_with_organisation = []
        for task in tasks:
            creator = task.creator  # The manager who created the task
            organisation = creator.user.organisation if creator else None  # Get the creator's organisation

            # Filter by organization if an organisation is selected
            if organisation_id and organisation and organisation.id != int(organisation_id):
                continue  # Skip this task if it doesn't belong to the selected organization

            task_agents = task.agents  # Assigned agents

            # Get requested agents for the task
            task_requests = TaskRequest.query.filter_by(task_id=task.id).all()
            task_request_agents = [request.agent for request in task_requests]  # List of agents who requested the task

            tasks_with_organisation.append({
                'task': task,
                'organisation': organisation,
                'task_agents': task_agents,
                'task_request_agents': task_request_agents
            })

        # Sort tasks based on the selected sort order
        if sort_order == 'newest':
            tasks_with_organisation.sort(key=lambda x: x['task'].created_at, reverse=True)
        elif sort_order == 'oldest':
            tasks_with_organisation.sort(key=lambda x: x['task'].created_at)

        # Get all organizations for the filter dropdown
        organisations = Organisation.query.all()

        return render_template(
            'report_tasks.html',
            report=report,
            tasks_with_organisation=tasks_with_organisation,
            organisations=organisations,
            organisation_id=organisation_id,
            sort_order=sort_order
        )

    else:
        flash('Access denied. Only managers can manage reports.', 'error')
        return redirect(url_for('main.mainpage'))
