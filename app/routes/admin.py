from asyncio import tasks

from flask import Blueprint, render_template, session, request
from app.models import (
    create_user, delete_user, get_all_users,
    create_task, get_all_tasks,
    get_logs, log_action, get_user_by_id, update_task_status
)
from app import bcrypt
from app.utils.email import send_email

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/admin', methods=['GET', 'POST'])
def admin_dashboard():
    if session.get('role') != 'admin':
        return "Unauthorized"

    # ================= CREATE MANAGER =================
    if request.method == 'POST' and 'username' in request.form:
        username = request.form.get('username')
        password = bcrypt.generate_password_hash(
            request.form.get('password')
        ).decode('utf-8')

        role = request.form.get('role')   # ✅ FIXED
        email = request.form.get('email')

        if role != "manager":
            return "Admin can only create managers"

        create_user(username, password, role, email)

        log_action(session.get('user_id'), f"Created manager: {username}", "local", "browser", "unknown")

    # ================= DELETE USER =================
    elif request.method == 'POST' and 'delete_user_id' in request.form:
        user_id = request.form.get('delete_user_id')

        user = get_user_by_id(user_id)

        if user and user['role'] == 'admin':
            return "Admin cannot be deleted"

        delete_user(user_id)

    # ================= ASSIGN TASK =================
    elif request.method == 'POST' and 'title' in request.form:
        title = request.form.get('title')
        user_id = request.form.get('user_id')
        deadline = request.form.get('deadline')

        create_task(title, user_id, deadline)

        user = get_user_by_id(user_id)
        email = user['email'] if user else None

        if email:
            send_email(
    email,
    "✈️ AeroSecure Alert: New Task Assigned",
    f"""
========================================
        ✈ AEROSECURE TASK ALERT
========================================

Hello {user['username']},

A new task has been assigned to you by the system.

----------------------------------------
📌 TASK DETAILS
----------------------------------------
Task Name   : {title}
Deadline    : {deadline}
Assigned By : Admin

----------------------------------------
⚠️ ACTION REQUIRED
----------------------------------------
Please complete the task before the deadline
and upload the required proof in the system.

----------------------------------------
🔒 SECURITY NOTE
----------------------------------------
This is an automated notification from
AeroSecure Airport Security System.

If you were not expecting this task,
please report immediately.

----------------------------------------
AeroSecure Control Panel
"""
)

        log_action(session.get('user_id'), f"Assigned task: {title}", "local", "browser", "unknown")

    # ================= APPROVE / REJECT =================
    elif request.method == 'POST' and 'action' in request.form:
        task_id = request.form.get('task_id')
        action = request.form.get('action')

        if action == "approve":
            update_task_status(task_id, "approved")
        elif action == "reject":
            update_task_status(task_id, "rejected")

    # ================= FETCH DATA =================
    users = get_all_users()
    managers = [u for u in users if u['role'] == 'manager']

    tasks = get_all_tasks()
    manager_submissions = [t for t in tasks if t['status'] == 'pending_admin']
    logs = get_logs()

    # ✅ SPLIT TASKS FOR DIFFERENT TABLES
    completed_tasks = [t for t in tasks if t['status'] == 'approved']
    pending_tasks = [t for t in tasks if 'pending' in t['status']]
    rejected_tasks = [t for t in tasks if t['status'] == 'rejected']


    completed = len([t for t in tasks if t['status'] == 'approved'])
    pending = len([t for t in tasks if 'pending' in t['status']])
    rejected = len([t for t in tasks if t['status'] == 'rejected'])
    total = len(tasks)

    return render_template(
        "admin.html",
        users=users,
        managers=managers,
        tasks=tasks,
        manager_submissions=manager_submissions,
        logs=logs,
        completed=completed,
        pending=pending,
        rejected=rejected,
        completed_tasks=completed_tasks,
        pending_tasks=pending_tasks,
        rejected_tasks=rejected_tasks,
        total=total
    )