from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from src.db import db
from src.models import Manager, Task, Report, Agent, TaskRequest, agent_task
from geopy.geocoders import Nominatim
task = Blueprint('task', __name__)



#to be done
@task.route('/create_task/<int:report_id>', methods=['GET', 'POST'])
@login_required
def create_task(report_id):
    report = Report.query.get_or_404(report_id)
    manager = Manager.query.filter_by(user_id=current_user.uid).first()
    current_organisation_id = current_user.organisation_id
    agents = Agent.query.all()

    in_org = []
    not_org = []
    for agent in agents:
        if agent.user.organisation_id == current_organisation_id:
            in_org.append(agent)
        else:
            not_org.append(agent)

    lat, lon = map(str.strip, report.location.split(','))
    geolocator = Nominatim(user_agent="AFM")

    try:
        loc = geolocator.reverse(f"{lat}, {lon}")
        address = loc.address if loc else f"Coordinates: {lat}, {lon}"
    except Exception as e:
        address = f"Coordinates: {lat}, {lon}"

    if request.method == 'POST':
        task_name = request.form.get('name')
        task_description = request.form.get('description')
        selected_agents_ids = request.form.getlist('agents')

        if not selected_agents_ids:
            flash("No agents selected.", "danger")
            return redirect(request.url)

        if not task_name or not task_description:
            flash("Please fill in all fields.", "danger")
            return redirect(request.url)

        new_task = Task(
            name=task_name,
            description=task_description,
            creator_id=manager.id,
        )

        db.session.add(new_task)
        db.session.commit()

        report.tasks.append(new_task)
        db.session.commit()

        for agent_id in selected_agents_ids:
            agent = Agent.query.get(agent_id)
            if agent:

                existing_assignment = db.session.query(agent_task).filter_by(agent_id=agent.id,
                                                                            task_id=new_task.id).first()

                if existing_assignment:

                    flash(f"Agent {agent.user.username} is already assigned to this task.", "warning")
                    continue
                if agent.user.organisation_id == current_organisation_id:

                    new_task.agents.append(agent)
                else:

                    task_request = TaskRequest(task_id=new_task.id, agent_id=agent.id)
                    db.session.add(task_request)

        db.session.commit()

        flash("Task created successfully!", "success")

    return render_template('create_task.html', report=report, my_agents=in_org, other_agents=not_org,
                           current_organisation_id=current_organisation_id, location=address)


#to be done
@task.route('/view-tasks')
@login_required
def view_tasks():
    return render_template('view_tasks.html')

