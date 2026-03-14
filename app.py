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

from routes.candidate_routes import c_bp
app.register_blueprint(c_bp)

from routes.complaint_routes import complaint_bp
app.register_blueprint(complaint_bp)






# Create Database Tables
with app.app_context():
    db.create_all()





# Run the App
if __name__ == "__main__":
    app.run(debug=True, port = 1234)