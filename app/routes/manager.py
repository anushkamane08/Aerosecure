from flask import Blueprint, render_template, session, request
from app.models import (
    create_user, create_task, get_all_tasks,
    update_task_status, get_tasks_assigned_to_manager,
    get_all_users, update_manager_file
)
from app import bcrypt
from app.utils.email import send_email

manager_bp = Blueprint('manager', __name__)

@manager_bp.route('/manager', methods=['GET', 'POST'])
def manager_dashboard():

    if session.get('role') != 'manager':
        return "Unauthorized"

    manager_id = session['user_id']

    # ================= CREATE EMPLOYEE =================
    if request.method == 'POST' and 'username' in request.form:
        username = request.form['username']
        password = bcrypt.generate_password_hash(
            request.form['password']
        ).decode('utf-8')
        email = request.form['email']

        create_user(username, password, "employee", email)

    # ================= ASSIGN TASK =================
    elif request.method == 'POST' and 'title' in request.form:
        title = request.form['title']
        user_id = int(request.form['user_id'])
        deadline = request.form['deadline']

        create_task(title, user_id, deadline)

    # ================= APPROVE / REJECT / SUBMIT =================
    elif request.method == 'POST' and 'action' in request.form:
        task_id = request.form['task_id']
        action = request.form['action']

        if action == "approve":
            update_task_status(task_id, "approved")

        elif action == "reject":
            update_task_status(task_id, "rejected")

        elif action == "submit_admin":
            file = request.files.get('manager_file')

            if file and file.filename != "":
                from werkzeug.utils import secure_filename
                import os
                from flask import current_app

                filename = secure_filename(file.filename)
                path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
                file.save(path)

                update_manager_file(task_id, filename)

            update_task_status(task_id, "pending_admin")

    # ================= EOD REPORT =================
    elif request.method == 'POST' and 'send_report' in request.form:

        admin_tasks = get_tasks_assigned_to_manager(manager_id)

        completed = [t for t in admin_tasks if t['status'] == 'approved']
        pending = [t for t in admin_tasks if t['status'] != 'approved']

        completed_text = "\n".join([f"- {t['title']}" for t in completed]) or "None"
        pending_text = "\n".join([f"- {t['title']}" for t in pending]) or "None"

        message = f"""
End of Day Report

Manager ID: {manager_id}

Completed Tasks:
{completed_text}

Pending Tasks:
{pending_text}
"""

        users = get_all_users()
        admin = [u for u in users if u['role'] == 'admin'][0]

        send_email(admin['email'], "EOD Task Report", message)

    # ================= FETCH DATA =================
    employees = [u for u in get_all_users() if u['role'] == 'employee']
    admin_tasks = get_tasks_assigned_to_manager(manager_id)

    all_tasks = get_all_tasks()

    # ⚠️ filter properly (basic version)
    tasks = [t for t in all_tasks if t['assigned_to'] != manager_id]

    # ================= ALWAYS DEFINE (IMPORTANT) =================
    pending_tasks = [t for t in tasks if 'pending' in t['status']]
    completed_tasks = [t for t in tasks if t['status'] == 'approved']
    rejected_tasks = [t for t in tasks if t['status'] == 'rejected']

    # ================= RETURN =================
    return render_template(
        "manager.html",
        employees=employees,
        tasks=tasks,
        admin_tasks=admin_tasks,

        pending_tasks=pending_tasks,
        completed_tasks=completed_tasks,
        rejected_tasks=rejected_tasks,

        pending=len(pending_tasks),
        completed=len(completed_tasks),
        rejected=len(rejected_tasks)
    )