import os
from flask import (
    Blueprint,
    jsonify,
    render_template,
    request,
    redirect,
    url_for,
    current_app,
)

admin_bp = Blueprint("admin", __name__)

# Configure upload folder and allowed extensions
UPLOAD_FOLDER = "photos"
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}

# Ensure the upload directory exists
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)


# Function to check allowed file types
def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS



# Routes
@admin_bp.route("/")
def dashboard():
    return jsonify({"message": "Welcome to the admin dashboard!"})


@admin_bp.route("/dashboard/photo")
def index():
    return render_template("admin_photo.html")


@admin_bp.route("/upload", methods=["POST"])
def upload_file():
    if "photo" not in request.files:
        return "No file part"
    file = request.files["photo"]
    if file.filename == "":
        return "No selected file"
    if file and allowed_file(file.filename):
        filename = file.filename
        filepath = os.path.join(current_app.config["UPLOAD_FOLDER"], filename)
        file.save(filepath)
        return redirect(url_for("admin.uploaded_file", filename=filename))
    return "File type not allowed"


@admin_bp.route("/uploads/<filename>")
def uploaded_file(filename):
    return render_template("uploaded.html", filename=filename)
