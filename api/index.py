# Vercel entry point for Digital Civic Participation & Governance Platform
import sys
import os

# Add the root directory to Python path so imports work correctly
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, root_dir)

from dotenv import load_dotenv
load_dotenv()

from flask import Flask, request, redirect, jsonify, render_template, session
from sqlalchemy import text
from database_init import db
import os

app = Flask(__name__, template_folder=os.path.join(root_dir, 'templates'), static_folder=os.path.join(root_dir, 'static'))

# Database Configuration
# Support PostgreSQL on Vercel, SQLite for local development
db_url = os.getenv("DATABASE_URL")
if db_url:
    # Fix PostgreSQL URL scheme if needed (psycopg2 requires postgresql:// not postgres://)
    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)
    app.config["SQLALCHEMY_DATABASE_URI"] = db_url
else:
    # Local development with SQLite
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(root_dir, "voting_system.db")

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.secret_key = os.getenv("SECRET_KEY", "dev_key_change_in_production")
app.config["UPLOAD_FOLDER"] = os.path.join(root_dir, "static", "uploads")
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # 16MB max upload

db.init_app(app)
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)


# Homepage route
@app.route("/")
def home():
    generate_notifications()
    return render_template("landing.html")


@app.route("/dashboard")
def dashboard():
    voter_id = session.get("user_id")
    if not voter_id:
        return redirect("/auth/login")

    from models.voters import Voter
    current_user = Voter.query.get(voter_id)

    if not current_user:
        session.pop("user_id", None)
        return redirect("/")

    generate_notifications()
    return render_template("home.html", current_user=current_user)


# Context processor for notification badge
@app.context_processor
def inject_notification_count():
    unread_notification_count = 0
    current_user = None

    voter_id = session.get("user_id")
    if voter_id:
        from models.voters import Voter
        from models.notification import Notification
        current_user = Voter.query.get(voter_id)

        unread_notification_count = Notification.query.filter_by(
            voter_id=voter_id,
            is_read=False
        ).count()

    return dict(unread_notification_count=unread_notification_count, current_user=current_user)


# Register all blueprints
from routes.service_request_routes import s_bp
app.register_blueprint(s_bp)

from routes.election_creation_routes import e_bp
app.register_blueprint(e_bp)

from routes.auth import auth_bp
app.register_blueprint(auth_bp)

from routes.admin import admin_bp
app.register_blueprint(admin_bp)

from routes.token import token_bp
app.register_blueprint(token_bp)

from routes.candidate_routes import c_bp
app.register_blueprint(c_bp)

from routes.complaint_routes import complaint_bp
app.register_blueprint(complaint_bp)

from routes.vote_flow import vote_flow_bp
app.register_blueprint(vote_flow_bp)

from routes.chatbot import chat_bp
app.register_blueprint(chat_bp)

from routes.notification import notification_bp, generate_notifications
app.register_blueprint(notification_bp)

from routes.results import result_bp
app.register_blueprint(result_bp)

from routes.audit_log import audit_bp
app.register_blueprint(audit_bp)


# Create Database Tables
with app.app_context():
    db.create_all()


if __name__ == "__main__":
    debug_mode = os.getenv("FLASK_ENV") == "development"
    port = int(os.getenv("PORT", 5000))
    app.run(debug=debug_mode, port=port, host="0.0.0.0")
