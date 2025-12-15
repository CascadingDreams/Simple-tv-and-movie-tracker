from flask import Flask
from config import Config
from models import init_db

app = Flask(__name__)
app.config.from_object(Config)

init_db(app)


@app.route("/")
def home():
    return {"message": "API is running!"}


@app.route("/health")
def health():
    """Health check endpoint to verify database connection"""
    from models import db

    try:
        # Try to execute a simple query
        db.session.execute(db.text("SELECT 1"))
        return {"status": "healthy", "database": "connected"}, 200
    except Exception as e:
        return {"status": "unhealthy", "database": "disconnected", "error": str(e)}, 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
