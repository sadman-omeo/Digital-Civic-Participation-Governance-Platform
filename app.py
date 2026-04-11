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

db.init_app(app)
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


# Create Database Tables
with app.app_context():
    db.create_all()





# Run the App
if __name__ == "__main__":
    app.run(debug=True, port = 1234)