from app import app  # Import your Flask app object

# Expose the Flask app as a WSGI callable
application = app

if __name__ == "__main__":
    application.run()  # Only for debugging, not used in production