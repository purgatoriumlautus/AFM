from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from src.models import User, Organisation, Agent, Manager
from src.db import db
import os

superadmin = Blueprint('superadmin', __name__)

def is_super_admin():
    return current_user.email == os.getenv("ADMIN_EMAIL")



@superadmin.route('/', methods=['GET', 'POST'])
@login_required
def superadmin_dashboard():
    if not is_super_admin():
        flash("You are not authorized to view this page.", "danger")
        return redirect(url_for('main.mainpage'))

    # Handle POST requests for search or updates
    if request.method == 'POST':
        # Search query from the form (if applicable)
        search_query = request.form.get('search', '').strip()

        # Redirect to the same page with search query as a GET parameter
        return redirect(url_for('superadmin.superadmin_dashboard', search=search_query))

    # Handle GET requests for sorting and filtering
    search_query = request.args.get('search', '').strip()
    sort_by = request.args.get('sort_by', 'username')  # Default sort by username
    sort_order = request.args.get('sort_order', 'asc')  # Default sort order is ascending

    # Base query for users
    query = User.query.filter(User.email != os.getenv("ADMIN_EMAIL"))

    # Apply search filter
    if search_query:
        query = query.filter(User.username.ilike(f"%{search_query}%"))

    # Sorting logic
    if sort_by == 'role':
        query = query.outerjoin(Agent).outerjoin(Manager).order_by(
            (Manager.id != None).desc(),  # Managers first
            (Agent.id != None).desc(),   # Agents second
            User.username if sort_order == 'asc' else User.username.desc()
        )
    elif sort_by == 'organisation':
        query = query.outerjoin(Organisation).order_by(
            Organisation.name if sort_order == 'asc' else Organisation.name.desc()
        )
    elif sort_by == 'status':
        query = query.order_by(
            User.is_banned if sort_order == 'asc' else User.is_banned.desc()
        )
    else:  # Default sorting
        query = query.order_by(User.username if sort_order == 'asc' else User.username.desc())

    # Fetch data
    users = query.all()
    organisations = Organisation.query.all()

    return render_template(
        'superadmin_dashboard.html',
        organisations=organisations,
        users=users,
        is_super_admin=is_super_admin(),
        sort_by=sort_by,
        sort_order=sort_order,
        search_query=search_query
    )



@superadmin.route('/update_user', methods=['POST'])
@login_required
def update_user():
    if not is_super_admin():
        return jsonify({"success": False, "message": "Unauthorized"}), 403

    user_id = request.form.get('user_id')
    organisation_id = request.form.get('organisation_id')
    role = request.form.get('role')
    is_owner = request.form.get('is_owner') == 'true'

    user = User.query.get_or_404(user_id)

    # Update organisation
    if organisation_id is not None:
        organisation = Organisation.query.get(organisation_id) if organisation_id else None
        user.organisation_id = organisation.id if organisation else None

    # Update roles
    if role is not None:
        if user.agent:
            db.session.delete(user.agent)
        if user.manager:
            db.session.delete(user.manager)

        if role == 'agent':
            db.session.add(Agent(user_id=user.uid))
        elif role == 'manager':
            db.session.add(Manager(user_id=user.uid))

    # Update ownership privilege
    if is_owner:
        # Ensure no other user in this organization is set as owner
        if user.organisation_id:
            User.query.filter_by(organisation_id=user.organisation_id, is_owner=True).update({'is_owner': False})
        user.is_owner = True
    else:
        user.is_owner = False

    db.session.commit()

    return jsonify({"success": True, "message": "User updated successfully"})





@superadmin.route('/ban_user', methods=['POST'])
@login_required
def ban_user():
    if not is_super_admin():
        return jsonify({"success": False, "message": "Unauthorized"}), 403
    
    print("Request data:", request.form)
    user_id = request.form.get('user_id')
    action = request.form.get('action')

    user = User.query.get_or_404(user_id)

    if action == "ban":
        user.is_banned = True
        message = f"User {user.username} has been banned."
    elif action == "unban":
        user.is_banned = False
        message = f"User {user.username} has been unbanned."
    else:
        return jsonify({"success": False, "message": "Invalid action"}), 400

    db.session.commit()
    return jsonify({"success": True, "message": message})



@superadmin.route('/organisations', methods=['GET'])
@login_required
def organisations_dashboard():
    if not is_super_admin():
        flash("You are not authorized to view this page.", "danger")
        return redirect(url_for('main.mainpage'))

    organisations = Organisation.query.all()

    # Prepare organization details
    org_data = []
    for org in organisations:
        members_count = org.users.count()
        owner = User.query.filter_by(uid=org.owner_id).first()
        org_data.append({
            'id': org.id,
            'name': org.name,
            'members_count': members_count,
            'owner': owner.username if owner else "No Owner"
        })

    return render_template('organisations_dashboard.html', organisations=org_data,is_super_admin=is_super_admin())



@superadmin.route('/delete_organisation/<int:org_id>', methods=['POST'])
@login_required
def delete_organisation(org_id):
    if not is_super_admin():
        return jsonify({"success": False, "message": "Unauthorized"}), 403

    organisation = Organisation.query.get_or_404(org_id)

    # Handle members
    members = User.query.filter_by(organisation_id=organisation.id).all()
    for member in members:
        member.organisation_id = None
        member.is_owner = False

        # Remove roles
        if member.agent:
            db.session.delete(member.agent)
        if member.manager:
            db.session.delete(member.manager)

    # Delete the organisation
    db.session.delete(organisation)
    db.session.commit()

    return jsonify({"success": True, "message": f"Organisation '{organisation.name}' deleted successfully"})
