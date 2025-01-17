from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from src.models import User, Organisation, Agent, Manager
from src.db import db
import os

superadmin = Blueprint('superadmin', __name__)

def is_super_admin():
    return current_user.email == os.getenv("ADMIN_EMAIL")


def get_super_admin_id():
    super_admin = User.query.filter_by(email=os.getenv("ADMIN_EMAIL")).first()
    if super_admin:
        return super_admin.uid
    raise ValueError("Super admin user not found. Please check the configuration.")

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
        flash("You are not authorized to perform this action.", "danger")
        return redirect(url_for('superadmin.superadmin_dashboard'))

    user_id = request.form.get('user_id')
    organisation_id = request.form.get('organisation_id')
    role = request.form.get('role')
    is_owner = request.form.get('is_owner') == 'true'

    user = User.query.get_or_404(user_id)

    # Ensure only one owner per organisation
    if is_owner:
        if user.organisation_id:
            # Remove ownership from other users in the same organisation
            User.query.filter_by(organisation_id=user.organisation_id, is_owner=True).update({'is_owner': False})

        user.is_owner = True

    else:
        if user.is_owner and user.organisation_id:
            organisation = Organisation.query.get(user.organisation_id)
            members = User.query.filter_by(organisation_id=organisation.id).all()

            # Get the superadmin's organisation
            super_admin_id = get_super_admin_id()
            super_admin = User.query.get(super_admin_id)
            super_admin_organisation_id = super_admin.organisation_id

            for member in members:
                member.organisation_id = super_admin_organisation_id
                member.is_owner = False

                # Remove roles
                if member.agent:
                    db.session.delete(member.agent)
                if member.manager:
                    db.session.delete(member.manager)

            db.session.delete(organisation)
            user.is_owner = False
            user.organisation_id = None
        elif user.is_owner and not user.organisation_id:
            user.is_owner = False
    # Update organisation only if user is not an owner
    if organisation_id is not None and not user.is_owner:
        organisation = Organisation.query.get(organisation_id) if organisation_id else None
        user.organisation_id = organisation.id if organisation else None

    
    # Update roles
    
    if role is not None:
        # Remove existing roles
        if user.agent:
            db.session.delete(user.agent)
        if user.manager:
            db.session.delete(user.manager)

        # Commit to persist the deletions before adding new roles
        db.session.commit()
        try:
            # Add new role
            if role == 'agent' and not user.agent:
                db.session.add(Agent(user_id=user.uid))
            elif role == 'manager' and not user.manager:
                db.session.add(Manager(user_id=user.uid))
        except:
            pass

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

    users = User.query.all()
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

    return render_template('organisations_dashboard.html', organisations=organisations,
        users=users,
        super_admin_id = get_super_admin_id(),
        is_super_admin=is_super_admin())



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


@superadmin.route('/update_owner/<int:org_id>', methods=['POST'])
@login_required
def update_owner(org_id):
    if not is_super_admin():
        return jsonify({"success": False, "message": "Unauthorized"}), 403

    new_owner_id = request.form.get('owner_id')
    organisation = Organisation.query.get_or_404(org_id)

    if new_owner_id:
        # Remove current owner's privileges
        if organisation.owner_id:
            current_owner = User.query.get(organisation.owner_id)
            if current_owner:
                current_owner.is_owner = False
                current_owner.organisation_id = None

        # Set new owner
        new_owner = User.query.get_or_404(new_owner_id)
        new_owner.is_owner = True
        new_owner.organisation_id = organisation.id
        organisation.owner_id = new_owner_id
    else:
        # Remove the owner entirely if no owner is selected
        organisation.owner_id = None

    db.session.commit()
    return jsonify({"success": True, "message": "Owner updated successfully"})

