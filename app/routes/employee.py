from flask import Blueprint, render_template, session, request, current_app
from app.models import get_tasks_by_user, update_task_status, log_action, update_task_file
from werkzeug.utils import secure_filename
import os

employee_bp = Blueprint('employee', __name__)

@employee_bp.route('/employee', methods=['GET', 'POST'])
def employee_dashboard():
    if session.get('role') != 'employee':
        return "Unauthorized"

    user_id = session['user_id']

    # ================= SUBMIT TASK =================
    if request.method == 'POST':
        task_id = request.form.get('task_id')
        file = request.files.get('proof')

        if file and file.filename != "":
            filename = secure_filename(file.filename)

            upload_folder = current_app.config.get('UPLOAD_FOLDER', 'static/uploads')
            os.makedirs(upload_folder, exist_ok=True)

            path = os.path.join(upload_folder, filename)
            file.save(path)

            # Save file + update status
            update_task_file(task_id, filename)
            update_task_status(task_id, "pending_manager")

            log_action(
                user_id,
                f"Submitted task ID: {task_id}",
                "local",
                "browser",
                "unknown"
            )

    # ================= FETCH TASKS =================
    tasks = get_tasks_by_user(user_id)

    # 🟢 Ensure dict format (important)
    tasks = [dict(t) for t in tasks]

    # ================= FILTER TASKS =================
    pending_tasks = [t for t in tasks if 'pending' in t['status']]
    completed_tasks = [t for t in tasks if t['status'] == 'approved']
    rejected_tasks = [t for t in tasks if t['status'] == 'rejected']

    # ================= COUNTS =================
    total = len(tasks)
    completed = len(completed_tasks)
    pending = len(pending_tasks)
    rejected = len(rejected_tasks)

    # ================= RENDER =================
    return render_template(
        "employee.html",
        tasks=tasks,
        pending_tasks=pending_tasks,
        completed_tasks=completed_tasks,
        rejected_tasks=rejected_tasks,
        total=total,
        completed=completed,
        pending=pending,
        rejected=rejected
    )