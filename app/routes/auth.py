from flask import Blueprint, render_template, request, redirect, session
from app.models import log_action, get_user_by_username
from app.utils.email import send_email
from app import bcrypt
from datetime import datetime
import time
import requests

auth_bp = Blueprint('auth', __name__)

FAILED_LIMIT = 5
LOCK_TIME = 60


@auth_bp.route('/', methods=['GET', 'POST'])
def login():
    error = None
    username = None

    # 🔒 LOCK CHECK
    lock_until = session.get('lock_until')

    if lock_until:
        if time.time() < lock_until:
            remaining = int(lock_until - time.time())
            return render_template(
                "login.html",
                error="Too many failed attempts",
                remaining=remaining,
                username=username
            )
        else:
            session.pop('lock_until')
            session['failed_attempts'] = 0

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = get_user_by_username(username)

        # ================= ✅ SUCCESS LOGIN =================
        if user and bcrypt.check_password_hash(user['password'], password):

            session['user_id'] = user['id']
            session['role'] = user['role']
            session['failed_attempts'] = 0

            log_action(
                user['id'],
                "Login Success",
                request.remote_addr,
                "browser",
                "unknown"
            )

            # 📧 SUCCESS EMAIL
            email = user['email']

            if email:
                ip = request.remote_addr
                ua = request.headers.get('User-Agent')

                if "Windows" in ua:
                    device = "Windows PC"
                elif "Mac" in ua:
                    device = "Mac"
                elif "Android" in ua:
                    device = "Android Device"
                elif "iPhone" in ua:
                    device = "iPhone"
                else:
                    device = "Unknown Device"
                now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                try:
                    response = requests.get(f"http://ip-api.com/json/{ip}")
                    data = response.json()
                    location = f"{data.get('city')}, {data.get('regionName')}, {data.get('country')}"
                except:
                    location = "Unknown"

                send_email(
    email,
    "AeroSecure: New Login Detected",
    f"""
========================================
        ✈ AEROSECURE SECURITY ALERT
========================================

A new login was detected on your account.

----------------------------------------
User        : {user['username']} ({user['role']})
IP Address  : {ip}
Location    : {location}
Device      : {device}
Date & Time : {now}
----------------------------------------

If this was you, no action is needed.

If this was NOT you:
⚠️ Immediately change your password
⚠️ Contact system administrator

----------------------------------------
AeroSecure Security Team
"""
)

            # 🔁 REDIRECT
            if user['role'] == 'admin':
                return redirect('/admin')
            elif user['role'] == 'manager':
                return redirect('/manager')
            else:
                return redirect('/employee')

        # ================= ❌ FAILED LOGIN =================
        else:
            session['failed_attempts'] = session.get('failed_attempts', 0) + 1
            attempts = session['failed_attempts']

            log_action(
                user['id'] if user else None,
                f"Failed Login ({attempts})",
                request.remote_addr,
                "browser",
                "unknown"
            )

            # 📧 ALERT AFTER 3 ATTEMPTS
            if attempts == 3 and user:
                email = user['email']

                if email:
                    ip = request.remote_addr
                    ua = request.headers.get('User-Agent')

                    if "Windows" in ua:
                        device = "Windows PC"
                    elif "Mac" in ua:
                        device = "Mac"
                    elif "Android" in ua:
                        device = "Android Device"
                    elif "iPhone" in ua:
                        device = "iPhone"
                    else:
                        device = "Unknown Device"
                    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                    try:
                        response = requests.get(f"http://ip-api.com/json/{ip}")
                        data = response.json()
                        location = f"{data.get('city')}, {data.get('regionName')}, {data.get('country')}"
                    except:
                        location = "Unknown"

                    send_email(
    email,
    "⚠️ AeroSecure Security Warning",
    f"""
========================================
        ⚠️ SECURITY WARNING
========================================

We detected multiple failed login attempts on your account.

----------------------------------------
User        : {user['username']} ({user['role']})
IP Address  : {ip}
Location    : {location}
Device      : {device}
Date & Time : {now}
----------------------------------------

⚠️ Your account may be at risk.

Recommended Actions:
- Change your password immediately
- Do not share your credentials
- Report suspicious activity

----------------------------------------
AeroSecure Threat Detection System
"""
)

            # 🔒 LOCK AFTER LIMIT
            if attempts >= FAILED_LIMIT:
                session['lock_until'] = time.time() + LOCK_TIME
                session['failed_attempts'] = 0
                error = "Too many failed attempts. Account locked for 60 seconds."
            else:
                error = "Invalid username or password"

        return render_template(
            "login.html",
            error=error,
            username=username
        )

    return render_template("login.html")