from flask import Flask
from config import FLASK_HOST, FLASK_PORT
from routes import main_bp, admin_bp
from scheduler import setup_jobs


# Initialize the Flask app
app = Flask(__name__)

# Set the maximum upload size to 16MB
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # 16MB

# Configure the upload folder for the main app
app.config["UPLOAD_FOLDER"] = "photos/default"

# Register routes blueprint
app.register_blueprint(main_bp)  # no prefix, so "/" routes remain the same
app.register_blueprint(admin_bp, url_prefix="/admin")

@app.errorhandler(413)
def too_large(e):
    return "File is too large. Maximum size allowed is 16MB.", 413

# Setup scheduler jobs
setup_jobs()

if __name__ == "__main__":
    app.run(host=FLASK_HOST, port=FLASK_PORT)
