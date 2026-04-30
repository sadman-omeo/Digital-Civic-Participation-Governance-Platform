from flask import Blueprint, request, render_template, session, redirect, url_for, jsonify
from models.vote_tokens import VoteToken
from models.voters import Voter
from database_init import db
from datetime import datetime, timedelta, timezone
import uuid
#import requests
from election_status_helper import is_election_locked #jesia auto lock
from models.election_creation import ElectionCreation #jeisa auto lock

token_bp= Blueprint("token", __name__, url_prefix="/token")
@token_bp.route("/generate_token", methods=["GET", "POST"])
def generate_token():

    voter_id = session.get("user_id")
    if not voter_id:
        return redirect("/auth/login")
    
    ############## jesia auto lock #######
    selected_election_id = session.get("selected_election_id")
    if not selected_election_id:
        return redirect(url_for("vote_flow.election_select"))

    election = ElectionCreation.query.get(selected_election_id)
    if not election:
        return "Election not found", 404

    if is_election_locked(election):
        return redirect(url_for("vote_flow.election_closed_page"))

    ######### jesia auto lock #############

    voter = Voter.query.get(voter_id)
    if not voter:
        return jsonify({"error": "Voter not found"}), 404

    if voter.has_voted:
        return render_template("you_voted.html")

    existing_token = VoteToken.query.filter_by(voter_id=voter_id, used=False).order_by(VoteToken.id.desc()).first()
    active_token = None
    if existing_token:
        # print('hi')
        
        # if existing_token.expires_at
        expires_at_aware = existing_token.expires_at.replace(tzinfo=timezone.utc)
        if expires_at_aware > datetime.now(timezone.utc):
            active_token = existing_token
        else:
            db.session.delete(existing_token)
            db.session.commit()

   
    if request.method == "POST":
        
        if active_token:
            return f"Existing token still active. Expires at {active_token.expires_at}", 429
        
        
        new_token_str = str(uuid.uuid4())
        expire = datetime.now(timezone.utc) + timedelta(minutes=10)
        
        token_obj = VoteToken(
            voter_id=voter_id,
            token=new_token_str,
            created_at=datetime.now(timezone.utc),
            expires_at=expire,
            used=False
        )
        existing_token=token_obj
        db.session.add(token_obj)
        db.session.commit()
        return redirect(url_for("token.generate_token"))
    
    if existing_token:
      return render_template("token_gate.html", active_token=active_token, expired=existing_token.expires_at.replace(tzinfo=timezone.utc) + timedelta(hours=6))
    
    return render_template("token_gate.html")