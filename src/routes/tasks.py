from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from src.db import db
from src.models import Manager, Task, Report, Agent, TaskRequest, agent_task, User, Organisation
from sqlalchemy.orm import joinedload
from geopy.geocoders import Nominatim
import os

task = Blueprint('task', __name__)


def is_super_admin():
    super_admin_mail = os.getenv("ADMIN_EMAIL")
    return super_admin_mail == current_user.email

#to be done
@task.route('/create_task/<int:report_id>', methods=['GET', 'POST'])
@login_required
def create_task(report_id):
    report = Report.query.get_or_404(report_id)
    manager = Manager.query.filter_by(user_id=current_user.uid).first()
    current_organisation_id = current_user.organisation_id
    agents = Agent.query.all()
    if manager:
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



            if not task_name or not task_description:
                flash("Please fill in all fields.", "danger")
                return redirect(request.url)

            new_task = Task(
                name=task_name,
                description=task_description,
                creator_id=manager.id,
                status= "OPEN"
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
                               current_organisation_id=current_organisation_id, location=address,is_super_admin=is_super_admin())
    flash("You are not authorized to view this page.", "danger")
    return redirect(url_for('main.mainpage'))



@task.route('/view_tasks')
@login_required
def view_tasks():
    status = request.args.get('status', '')
    sort = request.args.get('sort', 'newest')
    current_organisation_id = current_user.organisation_id
    agents = Agent.query.all()
    manager = Manager.query.filter_by(user_id=current_user.uid).first()

    if manager:
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

        tasks_query = tasks_query.filter_by(creator_id=manager.id)

        if sort == 'newest':
            tasks_query = tasks_query.order_by(Task.created_at.desc())
        else:
            tasks_query = tasks_query.order_by(Task.created_at.asc())

        tasks = tasks_query.all()
        task_data = []
        for task in tasks:
            task_agents = []
            assigned_agents = {agent.id: agent for agent in task.agents}
            task_requests = TaskRequest.query.filter_by(task_id=task.id).all()
            requested_agents = {request.agent.id: request.agent for request in task_requests}
            for agent in in_org:
                if agent.id in assigned_agents:
                    task_agents.append({"agent": assigned_agents[agent.id], "status": "current"})
                elif agent.id in requested_agents:
                    task_agents.append({"agent": requested_agents[agent.id], "status": "requested"})

            for agent in not_org:
                if agent.id in assigned_agents:
                    task_agents.append({"agent": assigned_agents[agent.id], "status": "current"})
                elif agent.id in requested_agents:
                    task_agents.append({"agent": requested_agents[agent.id], "status": "requested"})

            task_data.append({"task": task, "agents": task_agents})

        return render_template(
            'view_tasks.html',
            tasks=task_data,
            my_agents=in_org,
            other_agents=not_org,
            status=status,
            sort=sort,is_super_admin=is_super_admin()
        )
    else:
        flash("You are not authorized to view this page.", "danger")
        return redirect(url_for('index'))


@task.route('/task/edit/<int:task_id>', methods=['POST'])
@login_required
def update_task(task_id):
    task = Task.query.get_or_404(task_id)
    manager = Manager.query.filter_by(user_id=current_user.uid).first()

    if manager:
        manager_organization = manager.user.organisation_id

        if request.method == 'POST':
            task.name = request.form.get('name', task.name)
            task.description = request.form.get('description', task.description)
            task.status = request.form.get('status', task.status)
            current_agents_in_task = {agent.id for agent in task.agents}
            current_agents_in_request = {task_request.agent_id for task_request in TaskRequest.query.filter_by(task_id=task.id).all()}
            selected_agents_ids = set(map(int, request.form.getlist("agents[]")))
            agents_to_remove_from_task = current_agents_in_task - selected_agents_ids
            for agent_id in agents_to_remove_from_task:
                agent = Agent.query.get(agent_id)
                if agent:
                    task.agents.remove(agent)
            agents_to_remove_from_request = current_agents_in_request - selected_agents_ids
            for agent_id in agents_to_remove_from_request:
                task_request = TaskRequest.query.filter_by(task_id=task.id, agent_id=agent_id).first()
                if task_request:
                    db.session.delete(task_request)

            agents_to_add = selected_agents_ids - current_agents_in_task - current_agents_in_request
            for agent_id in agents_to_add:
                agent = Agent.query.get(agent_id)
                if agent:
                    if agent.user.organisation_id != manager_organization:
                        new_request = TaskRequest(task_id=task.id, agent_id=agent.id)
                        existing_request = TaskRequest.query.filter_by(task_id=task.id, agent_id=agent.id).first()
                        if not existing_request:
                            db.session.add(new_request)
                    else:
                        if agent.id not in current_agents_in_task:
                            task.agents.append(agent)

            db.session.commit()
            flash('Task updated successfully!', 'success')
            return redirect(url_for('task.view_tasks'))

    flash("You are not authorized to view this page.", "danger")
    return redirect(url_for('main.mainpage'))


@task.route('/task/delete/<int:task_id>', methods=['POST'])
@login_required
def delete_task(task_id):
    manager = Manager.query.filter_by(user_id=current_user.uid).first()
    if manager:
        task = Task.query.get_or_404(task_id)
        db.session.delete(task)
        db.session.commit()
        flash('Task deleted successfully!', 'success')
        return redirect(url_for('task.view_tasks'))
    flash("You are not authorized to view this page.", "danger")
    return redirect(url_for('main.mainpage'))


@task.route('/agents/view_tasks', methods=['GET'])
@login_required
def agent_view_tasks():
    agent = Agent.query.filter_by(user_id=current_user.uid).first()
    if not agent:
        flash('You are not authorized to view this page.', 'danger')
        return redirect(url_for('main.index'))

    status_filter = request.args.get('status')
    sort_filter = request.args.get('sort')
    query = db.session.query(Task).join(agent_task).filter(agent_task.c.agent_id == agent.id)

    if status_filter:
        query = query.filter(Task.status == status_filter)

    if sort_filter == "newest":
        query = query.order_by(Task.created_at.desc())
    elif sort_filter == "oldest":
        query = query.order_by(Task.created_at.asc())

    assigned_tasks = query.all()

    tasks_with_related = []

    for task in assigned_tasks:

        related_tasks = Task.query.join(Task.reports).filter(
            Report.id.in_([report.id for report in task.reports]),
            Task.id != task.id
        ).all()

        tasks_with_related.append({
            'task': task,
            'related_tasks': related_tasks
        })

    return render_template('agent_view_tasks.html', tasks_with_related=tasks_with_related,
                           status=status_filter, sort=sort_filter,is_super_admin=is_super_admin())


@task.route('/tasks/change_status/<int:task_id>', methods=['POST'])
@login_required
def change_status(task_id):
    task = Task.query.get(task_id)
    if not task:
        flash('Task not found', 'danger')
        return redirect(url_for('task.agent_view_tasks'))

    agent = Agent.query.filter_by(user_id=current_user.uid).first()
    if agent:
        new_status = request.form.get('new_status')

        if new_status == 'IN_PROGRESS' and task.status in ['OPEN', 'REQUIRES_CLARIFICATION']:
            task.status = 'IN_PROGRESS'
        elif new_status == 'RESOLVED' and task.status == 'IN_PROGRESS':
            task.status = 'RESOLVED'
        elif new_status == 'REQUIRES_CLARIFICATION' and task.status in ['OPEN', 'IN_PROGRESS']:
            task.status = 'REQUIRES_CLARIFICATION'
        else:
            flash('Invalid status change', 'danger')
            return redirect(url_for('task.agent_view_tasks'))

        db.session.commit()

        status_filter = request.args.get('status')
        sort_filter = request.args.get('sort')
        query = db.session.query(Task).join(agent_task).filter(agent_task.c.agent_id == agent.id)

        if status_filter:
            query = query.filter(Task.status == status_filter)

        if sort_filter == "newest":
            query = query.order_by(Task.created_at.desc())
        elif sort_filter == "oldest":
            query = query.order_by(Task.created_at.asc())

        assigned_tasks = query.all()
        tasks_with_related = []
        for task in assigned_tasks:
            related_tasks = Task.query.join(Task.reports).filter(
                Report.id.in_([report.id for report in task.reports]),
                Task.id != task.id
            ).all()
            agents = [agent.user.username for agent in task.agents]

            tasks_with_related.append({
                'task': task,
                'agents': agents,
                'related_tasks': related_tasks
            })
        return render_template('agent_view_tasks.html', tasks_with_related=tasks_with_related,
                               status=status_filter, sort=sort_filter,is_super_admin=is_super_admin())

    flash("You are not authorized to view this page.", "danger")
    return redirect(url_for('main.mainpage'))

@task.route('/tasks/related_tasks/<int:task_id>', methods=['POST', 'GET'])
@login_required
def related_tasks(task_id):
    agent = Agent.query.filter_by(user_id=current_user.uid).first()
    if agent:
        task = Task.query.get(task_id)
        status_filter = request.args.get('status')
        sort_filter = request.args.get('sort')

        related_tasks = Task.query.join(Task.reports).filter(
            Report.id.in_([report.id for report in task.reports]),
            Task.id != task.id
        ).all()

        related_agents = {
            related_task.id: [agent.user.username for agent in related_task.agents]
            for related_task in related_tasks
        }

        if status_filter:
            related_tasks = [task for task in related_tasks if task.status == status_filter]

        if sort_filter == "newest":
            related_tasks = sorted(related_tasks, key=lambda t: t.created_at, reverse=True)
        elif sort_filter == "oldest":
            related_tasks = sorted(related_tasks, key=lambda t: t.created_at)
        elif sort_filter == "status":
            related_tasks = sorted(related_tasks, key=lambda t: t.status)

        return render_template(
            'related_tasks.html',
            related_tasks=related_tasks,
            related_agents=related_agents,
            status=status_filter,
            sort=sort_filter,
            task=task,is_super_admin=is_super_admin()
        )

    flash("You are not authorized to view this page.", "danger")
    return redirect(url_for('main.mainpage'))

@task.route('/manage_requests', methods=['GET', 'POST'])
@login_required
def manage_requests():
    agent = Agent.query.filter_by(user_id=current_user.uid).first()

    if agent:
        organisation_id = request.args.get('organisation')
        sort_order = request.args.get('sort')
        query = (
            TaskRequest.query
            .join(Task)
            .join(Manager, Task.creator_id == Manager.id)
            .join(User, Manager.user_id == User.uid)
            .join(Organisation, User.organisation_id == Organisation.id)
        )
        query = query.filter(TaskRequest.agent_id == agent.id)
        if organisation_id:
            query = query.filter(Organisation.id == organisation_id)
        if sort_order == 'newest':
            query = query.order_by(TaskRequest.created_at.desc())  # Newest first
        elif sort_order == 'oldest':
            query = query.order_by(TaskRequest.created_at.asc())
        requests = query.all()
        organisations = Organisation.query.all()
        return render_template('manage_requests.html', requests=requests, organisations=organisations, organisation=organisation_id,is_super_admin=is_super_admin())
    flash("You are not authorized to view this page.", "danger")
    return redirect(url_for('main.mainpage'))

@task.route('/manage_request/<int:request_id>', methods=['POST'])
@login_required
def manage_request(request_id):
    agent = Agent.query.filter_by(user_id=current_user.uid).first()

    if agent:

        task_request = TaskRequest.query.get_or_404(request_id)

        if task_request.agent_id != agent.id:
            flash("You do not have permission to manage this request.", 'danger')
            return redirect(url_for('task.manage_requests'))

        action = request.form['action']

        if action == 'approve':
            task_request.approved = True
            task = task_request.task
            task.agents.append(agent)
            db.session.delete(task_request)
            db.session.commit()
            flash(f"Request approved! {agent.user.username} has been assigned to the task.", 'success')

        elif action == 'reject':
            db.session.delete(task_request)
            db.session.commit()
            flash("Request rejected and deleted.", 'danger')

        return redirect(url_for('task.manage_requests'))
    flash("You are not authorized to view this page.", "danger")
    return redirect(url_for('main.mainpage'))
