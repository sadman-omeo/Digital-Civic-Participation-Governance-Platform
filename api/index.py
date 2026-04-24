# Vercel entry point for Digital Civic Participation & Governance Platform
import sys
import os
import logging

# Configure logging for debugging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add the root directory to Python path so imports work correctly
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, root_dir)

logger.info(f"Root directory: {root_dir}")

from dotenv import load_dotenv
load_dotenv()

from flask import Flask, request, redirect, jsonify, render_template, session
from sqlalchemy import text
from database_init import db
import os

app = Flask(__name__, template_folder=os.path.join(root_dir, 'templates'), static_folder=os.path.join(root_dir, 'static'))

# Database Configuration
db_url = os.getenv("DATABASE_URL")
if db_url:
    # Fix PostgreSQL URL scheme if needed
    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)
    app.config["SQLALCHEMY_DATABASE_URI"] = db_url
    logger.info("Using PostgreSQL database from DATABASE_URL")
else:
    # Local development with SQLite
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(root_dir, "voting_system.db")
    logger.warning("Using SQLite database (not recommended for production)")

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.secret_key = os.getenv("SECRET_KEY", "dev_key_change_in_production")
app.config["UPLOAD_FOLDER"] = os.path.join(root_dir, "static", "uploads")
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024

db.init_app(app)

try:
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
    logger.info(f"Upload folder ready: {app.config['UPLOAD_FOLDER']}")
except Exception as e:
    logger.error(f"Failed to create upload folder: {e}")


# ========== IMPORT BLUEPRINTS EARLY ==========
try:
    from routes.notification import notification_bp, generate_notifications
    logger.info("✅ Notification routes imported")
except Exception as e:
    logger.error(f"❌ Failed to import notification routes: {e}")
    # Provide a fallback function if import fails
    def generate_notifications():
        logger.warning("generate_notifications called but not available")
        pass

try:
    from routes.service_request_routes import s_bp
    logger.info("✅ Service request routes imported")
except Exception as e:
    logger.error(f"❌ Failed to import service request routes: {e}")

try:
    from routes.election_creation_routes import e_bp
    logger.info("✅ Election creation routes imported")
except Exception as e:
    logger.error(f"❌ Failed to import election creation routes: {e}")

try:
    from routes.auth import auth_bp
    logger.info("✅ Auth routes imported")
except Exception as e:
    logger.error(f"❌ Failed to import auth routes: {e}")

try:
    from routes.admin import admin_bp
    logger.info("✅ Admin routes imported")
except Exception as e:
    logger.error(f"❌ Failed to import admin routes: {e}")

try:
    from routes.token import token_bp
    logger.info("✅ Token routes imported")
except Exception as e:
    logger.error(f"❌ Failed to import token routes: {e}")

try:
    from routes.candidate_routes import c_bp
    logger.info("✅ Candidate routes imported")
except Exception as e:
    logger.error(f"❌ Failed to import candidate routes: {e}")

try:
    from routes.complaint_routes import complaint_bp
    logger.info("✅ Complaint routes imported")
except Exception as e:
    logger.error(f"❌ Failed to import complaint routes: {e}")

try:
    from routes.vote_flow import vote_flow_bp
    logger.info("✅ Vote flow routes imported")
except Exception as e:
    logger.error(f"❌ Failed to import vote flow routes: {e}")

try:
    from routes.chatbot import chat_bp
    logger.info("✅ Chatbot routes imported")
except Exception as e:
    logger.error(f"❌ Failed to import chatbot routes: {e}")

try:
    from routes.results import result_bp
    logger.info("✅ Results routes imported")
except Exception as e:
    logger.error(f"❌ Failed to import results routes: {e}")

try:
    from routes.audit_log import audit_bp
    logger.info("✅ Audit log routes imported")
except Exception as e:
    logger.error(f"❌ Failed to import audit log routes: {e}")


# ========== DEFINE ROUTES ==========

@app.route("/")
def home():
    try:
        generate_notifications()
    except Exception as e:
        logger.error(f"Error generating notifications: {e}")
    return render_template("landing.html")


@app.route("/dashboard")
def dashboard():
    voter_id = session.get("user_id")
    if not voter_id:
        return redirect("/auth/login")

    try:
        from models.voters import Voter
        current_user = Voter.query.get(voter_id)

        if not current_user:
            session.pop("user_id", None)
            return redirect("/")

        generate_notifications()
        return render_template("home.html", current_user=current_user)
    except Exception as e:
        logger.error(f"Error in dashboard: {e}")
        return redirect("/auth/login")


@app.context_processor
def inject_notification_count():
    unread_notification_count = 0
    current_user = None

    try:
        voter_id = session.get("user_id")
        if voter_id:
            from models.voters import Voter
            from models.notification import Notification
            current_user = Voter.query.get(voter_id)

            unread_notification_count = Notification.query.filter_by(
                voter_id=voter_id,
                is_read=False
            ).count()
    except Exception as e:
        logger.error(f"Error in context processor: {e}")

    return dict(unread_notification_count=unread_notification_count, current_user=current_user)


# ========== REGISTER ALL BLUEPRINTS ==========
try:
    app.register_blueprint(s_bp)
    app.register_blueprint(e_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(token_bp)
    app.register_blueprint(c_bp)
    app.register_blueprint(complaint_bp)
    app.register_blueprint(vote_flow_bp)
    app.register_blueprint(chat_bp)
    app.register_blueprint(notification_bp)
    app.register_blueprint(result_bp)
    app.register_blueprint(audit_bp)
    logger.info("✅ All blueprints registered successfully")
except Exception as e:
    logger.error(f"❌ Error registering blueprints: {e}")


# ========== INITIALIZE DATABASE ==========
try:
    with app.app_context():
        db.create_all()
        logger.info("✅ Database tables created/verified")
except Exception as e:
    logger.error(f"❌ Error creating database tables: {e}")
    logger.warning("Database initialization failed - this may cause runtime errors")


# ========== ERROR HANDLERS ==========
@app.errorhandler(404)
def not_found(error):
    return render_template("404.html") if os.path.exists(os.path.join(root_dir, "templates", "404.html")) else "Page not found", 404

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Internal server error: {error}")
    return "Internal server error", 500


# ========== HEALTH CHECK ENDPOINT ==========
@app.route("/health")
def health_check():
    """Health check endpoint for Vercel"""
    try:
        # Test database connection
        with app.app_context():
            db.session.execute(text("SELECT 1"))
        return jsonify({"status": "healthy", "database": "connected"}), 200
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return jsonify({"status": "unhealthy", "error": str(e)}), 500


if __name__ == "__main__":
    debug_mode = os.getenv("FLASK_ENV") == "development"
    port = int(os.getenv("PORT", 5000))
    app.run(debug=debug_mode, port=port, host="0.0.0.0")
