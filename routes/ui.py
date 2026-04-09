# ============================================================
#  UI Routes - Template Rendering
# ============================================================

from flask import Blueprint, render_template

# Initialize UI blueprint
ui_bp = Blueprint('ui', __name__)


@ui_bp.route("/")
def index():
    """Render home page."""
    return render_template("index.html")


@ui_bp.route("/chatbot")
def chatbot_page():
    """Render chatbot page with AI voter support assistant."""
    return render_template("chatbot.html")


@ui_bp.route("/vote")
def vote_page():
    """Render voting page with candidate selection and virtual sticker."""
    return render_template("vote.html")
