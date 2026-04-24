#Install the required Python packages
# pip install flask
# pip install flask_sqlalchemy
# pip install sqlalchemy
from dotenv import load_dotenv  # added
load_dotenv()  # added

from flask import Flask, request, redirect, jsonify, render_template, session  #added session
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
    generate_notifications()  # added for notification badge
    return render_template("landing.html")


@app.route("/dashboard")
def dashboard():  # added
    voter_id = session.get("user_id")
    if not voter_id:
        return redirect("/auth/login")

    from models.voters import Voter  # added
    current_user = Voter.query.get(voter_id)  # added

    if not current_user:  # added
        session.pop("user_id", None)  # added
        return redirect("/")  # added

    generate_notifications()  # added
    return render_template("home.html", current_user=current_user)  # changed



#############  FOR NOTIFICATION BADGE #############
@app.context_processor
def inject_notification_count():  
    unread_notification_count = 0  
    current_user = None  # added

    voter_id = session.get("user_id")  
    if voter_id:  # added
        from models.voters import Voter  # added
        from models.notification import Notification  
        current_user = Voter.query.get(voter_id)  # added

        unread_notification_count = Notification.query.filter_by(
            voter_id=voter_id,
            is_read=False
        ).count()  

    return dict(unread_notification_count=unread_notification_count, current_user=current_user)  

########################################################

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

#notificaTIon routes
from routes.notification import notification_bp, generate_notifications 
app.register_blueprint(notification_bp)  

#result visualization routes
from routes.results import result_bp  
app.register_blueprint(result_bp)  

#audit log routes
from routes.audit_log import audit_bp
app.register_blueprint(audit_bp)



# Create Database Tables
with app.app_context():
    db.create_all()





# Run the App
if __name__ == "__main__":
    import os
    debug_mode = os.getenv("FLASK_ENV") == "development"
    port = int(os.getenv("PORT", 1234))
    app.run(debug=debug_mode, port=port, host="0.0.0.0")