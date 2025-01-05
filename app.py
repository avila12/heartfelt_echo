from flask import Flask
from config import FLASK_HOST, FLASK_PORT
from routes import routes
from scheduler import setup_jobs

# Initialize the Flask app
app = Flask(__name__)

# Register routes blueprint
app.register_blueprint(routes)

# Setup scheduler jobs
setup_jobs()

if __name__ == "__main__":
    app.run(host=FLASK_HOST, port=FLASK_PORT)
