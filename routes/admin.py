import os
import subprocess

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
@admin_bp.route("/dashboard")
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


@admin_bp.route('/wifi_form')
def wifi_form():
    return render_template('wifi_form.html')


@admin_bp.route('/set-wifi', methods=['POST'])
def set_wifi():
    ssid = request.form['ssid']
    password = request.form['password']

    if not ssid or not password:
        return jsonify({'status': 'error', 'message': 'SSID and Password are required'}), 400

    wpa_config = f"""
    ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
    update_config=1
    country=US

    network={{
        ssid="{ssid}"
        psk="{password}"
    }}
    """
    try:
        with open('/etc/wpa_supplicant/wpa_supplicant.conf', 'w') as file:
            file.write(wpa_config)

        # Restart Wi-Fi
        result = subprocess.run(['sudo', 'wpa_cli', '-i', 'wlan0', 'reconfigure'], check=True)
        if result.returncode == 0:
            return jsonify({'status': 'success', 'message': 'Wi-Fi updated and restarted'}), 200
        else:
            return jsonify({'status': 'error', 'message': 'Failed to restart Wi-Fi'}), 500

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500
