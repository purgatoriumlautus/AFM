from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from src.db import db
from src.models import Manager, Task, Report, Agent, TaskRequest, agent_task
from sqlalchemy.orm import joinedload
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
            status= "Not Started"
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
@task.route('/view_tasks')
@login_required
def view_tasks():
    status = request.args.get('status', '')
    sort = request.args.get('sort', 'newest')
    current_organisation_id = current_user.organisation_id
    agents = Agent.query.all()

    in_org = []
    not_org = []
    for agent in agents:
        if agent.user.organisation_id == current_organisation_id:
            in_org.append(agent)
        else:
            not_org.append(agent)

    tasks_query = Task.query.options(joinedload(Task.agents))

    if status:
        tasks_query = tasks_query.filter_by(status=status)
    if sort == 'newest':
        tasks_query = tasks_query.order_by(Task.created_at.desc())
    else:
        tasks_query = tasks_query.order_by(Task.created_at.asc())

    tasks = tasks_query.all()

    return render_template('view_tasks.html',
                           tasks=tasks,
                           status=status,
                           sort=sort,
                           current_organisation_id=current_organisation_id,
                           my_agents=in_org,
                           other_agents=not_org)


@task.route('/task/edit/<int:task_id>', methods=['GET', 'POST'])
@login_required
def update_task(task_id):
    task = Task.query.get_or_404(task_id)

    if request.method == 'POST':
        # Update basic task fields
        task.name = request.form.get('task_name', task.name)
        task.description = request.form.get('task_description', task.description)
        task.status = request.form.get('task_status', task.status)

        # Current organization ID
        current_organisation_id = current_user.organisation_id

        # Process agent assignments
        selected_agents_ids = request.form.getlist('agents')  # Agents to assign
        assigned_agents = []

        for agent_id in selected_agents_ids:
            agent = Agent.query.get(agent_id)
            if not agent:
                flash(f"Agent with ID {agent_id} not found.", "warning")
                continue

            # Check if agent is already assigned
            existing_assignment = db.session.query(agent_task).filter_by(
                agent_id=agent.id, task_id=task.id
            ).first()

            if existing_assignment:
                flash(f"Agent {agent.user.username} is already assigned to this task.", "warning")
                continue

            if agent.user.organisation_id == current_organisation_id:
                assigned_agents.append(agent)
            else:
                # Create a TaskRequest for agents from other organizations
                task_request = TaskRequest(task_id=task.id, agent_id=agent.id)
                db.session.add(task_request)
                flash(f"Task request sent to {agent.user.username}.", "info")

        # Assign agents to task
        task.agents = assigned_agents

        # Commit changes to the database
        db.session.commit()
        flash('Task updated successfully!', 'success')

    return redirect(url_for('task.view_tasks'))
# End Task
@task.route('/task/end/<int:task_id>', methods=['POST'])
@login_required
def end_task(task_id):
    task = Task.query.get_or_404(task_id)
    task.status = 'Done'
    db.session.commit()
    flash('Task ended successfully!', 'success')
    return redirect(url_for('task.view_tasks'))


# Delete Task
@task.route('/task/delete/<int:task_id>', methods=['POST'])
@login_required
def delete_task(task_id):
    task = Task.query.get_or_404(task_id)
    db.session.delete(task)
    db.session.commit()
    flash('Task deleted successfully!', 'success')
    return redirect(url_for('task.view_tasks'))
