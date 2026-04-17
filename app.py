#Install the required Python packages
# pip install flask
# pip install flask_sqlalchemy
# pip install sqlalchemy

from flask import Flask, request, redirect, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
from database_init import db
import os

app = Flask(__name__)

# Database Configuration
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///voting_system.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.secret_key = "digital_civic_secret"
app.config["UPLOAD_FOLDER"] = "static/uploads"

db.init_app(app)
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
#db = SQLAlchemy(app)




#call routes here:

#homepage route
@app.route("/")
def home():
    return render_template("home.html")

#service request routes
from routes.service_request_routes import s_bp
app.register_blueprint(s_bp)

#election creation routes
from routes.election_creation_routes import e_bp
app.register_blueprint(e_bp)

#signup routes
from routes.auth import auth_bp
app.register_blueprint(auth_bp)

#admin can see voter details
from routes.admin import admin_bp
app.register_blueprint(admin_bp)

#token generation routes
from routes.token import token_bp
app.register_blueprint(token_bp)

#candidate management routes
from routes.candidate_routes import c_bp
app.register_blueprint(c_bp)

#complaint management routes
from routes.complaint_routes import complaint_bp
app.register_blueprint(complaint_bp)

#voting flow routes
from routes.vote_flow import vote_flow_bp
app.register_blueprint(vote_flow_bp)

#chatbot route
from routes.chatbot import chat_bp
app.register_blueprint(chat_bp)



# Create Database Tables
with app.app_context():
    db.create_all()





# Run the App
if __name__ == "__main__":
    app.run(debug=True, port = 1234)