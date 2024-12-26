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
    manager = Manager.query.filter_by(user_id=current_user.uid).first()
    if manager:
        if request.method == 'POST':
            task.name = request.form.get('name', task.name)
            task.description = request.form.get('description', task.description)
            task.status = request.form.get('status', task.status)
            selected_agents_ids = set(map(int, request.form.getlist("agents[]")))
            current_agents_ids = {agent.id for agent in task.agents}

            agents_to_remove = current_agents_ids - selected_agents_ids
            for agent_id in agents_to_remove:
                agent = Agent.query.get(agent_id)
                if agent:
                    task.agents.remove(agent)

            agents_to_add = selected_agents_ids - current_agents_ids
            for agent_id in agents_to_add:
                agent = Agent.query.get(agent_id)
                if agent:
                    task.agents.append(agent)

            db.session.commit()
            flash('Task updated successfully!', 'success')
            return redirect(url_for('task.view_tasks'))

        return render_template('task/edit_task.html', task=task)


@task.route('/task/end/<int:task_id>', methods=['POST'])
@login_required
def end_task(task_id):
    manager = Manager.query.filter_by(user_id=current_user.uid).first()
    if manager:
        task = Task.query.get_or_404(task_id)
        task.status = 'Done'
        db.session.commit()
        flash('Task ended successfully!', 'success')
        return redirect(url_for('task.view_tasks'))


# Delete Task
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
        agents = [agent.user.username for agent in task.agents]

        tasks_with_related.append({
            'task': task,
            'agents': agents,
            'related_tasks': related_tasks
        })

    return render_template('agent_view_tasks.html', tasks_with_related=tasks_with_related,
                           status=status_filter, sort=sort_filter)


@task.route('/tasks/change_status/<int:task_id>', methods=['POST'])
@login_required
def change_status(task_id):
    task = Task.query.get(task_id)
    if not task:
        flash('Task not found', 'danger')
        return redirect(url_for('task.agent_view_tasks'))
    agent = Agent.query.filter_by(user_id=current_user.uid).first()
    if agent:
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
        task.status = 'In Process'
        db.session.commit()
        return render_template('agent_view_tasks.html', tasks_with_related=tasks_with_related,
                               status=status_filter, sort=sort_filter)


@task.route('/tasks/related_tasks/<int:task_id>', methods=['POST', 'GET'])
@login_required
def related_tasks(task_id):
    agent = Agent.query.filter_by(user_id=current_user.uid).first()
    if not agent:
        flash('You are not authorized to view this page.', 'danger')
        return redirect(url_for('main.index'))
    task = Task.query.get(task_id)
    status_filter = request.args.get('status')
    sort_filter = request.args.get('sort')

    related_tasks = Task.query.join(Task.reports).filter(
        Report.id.in_([report.id for report in task.reports]),
        Task.id != task.id  # Ensure we're not selecting the same task
    ).all()

    related_agents = {}
    for related_task in related_tasks:
        related_agents[related_task.id] = [agent.user.username for agent in related_task.agents]

    if sort_filter == "newest":
        related_tasks = sorted(related_tasks, key=lambda t: t.created_at, reverse=True)
    elif sort_filter == "oldest":
        related_tasks = sorted(related_tasks, key=lambda t: t.created_at, reverse=False)
    elif sort_filter == "status":
        related_tasks = sorted(related_tasks, key=lambda t: t.status)

    return render_template('related_tasks.html', related_tasks=related_tasks, related_agents = related_agents,
                           status=status_filter, sort=sort_filter, task = task)