import os

# Base directory of your project
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = 'your_secret_key_here'

    # Upload folder (VERY IMPORTANT)
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'uploads')

    # Max file size (optional but good)
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB