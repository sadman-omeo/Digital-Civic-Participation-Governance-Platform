# ============================================================
#  Lab 04 | Voter Support System - Flask
#  Student ID : 23301111
#  Features   : 1) AI Chatbot for Voter Support  2) "I Voted" Virtual Sticker
#  Port       : 1111
# ============================================================

from flask import Flask
from routes import ui_bp, chat_bp, vote_bp

# Create Flask application
app = Flask(__name__)
app.secret_key = "secret_23301111"

# Register blueprints
app.register_blueprint(ui_bp)
app.register_blueprint(chat_bp)
app.register_blueprint(vote_bp)


# ════════════════════════════════════════════════════════════
#  MAIN
# ════════════════════════════════════════════════════════════

if __name__ == "__main__":
    app.run(debug=True, port=1111)


