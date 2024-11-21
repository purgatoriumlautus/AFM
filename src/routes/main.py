from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import login_user, logout_user,current_user
from src.models import User,Report
from src.extensions import bcrypt


main = Blueprint('main', __name__)



@main.route('/', methods=['GET', 'POST'])
def mainpage():
    reports = Report.all_reports()
    return render_template('mainpage.html', reports=reports, current_user=current_user)
