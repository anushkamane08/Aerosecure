from flask import Flask, send_from_directory
from flask_bcrypt import Bcrypt
import os
from flask import send_from_directory

bcrypt = Bcrypt()

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'secret123'

    UPLOAD_FOLDER = os.path.join(app.root_path, 'static', 'uploads')
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    bcrypt.init_app(app)



    # Import routes
    from app.routes.auth import auth_bp
    from app.routes.admin import admin_bp
    from app.routes.manager import manager_bp
    from app.routes.employee import employee_bp

    # Register routes
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(manager_bp)
    app.register_blueprint(employee_bp)

    return app