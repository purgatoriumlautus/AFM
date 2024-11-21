from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from src.db import db

task = Blueprint('task', __name__)


#to be done
@task.route('/create-task', methods=['GET', 'POST'])
@login_required
def create_task():
    return render_template('create_task.html')



#to be done
@task.route('/view-tasks')
@login_required
def view_tasks():
    return render_template('view_tasks.html')

