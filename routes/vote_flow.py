from datetime import datetime, timezone
from election_status_helper import is_election_locked #new added
from flask import Blueprint, render_template, request, redirect, session, url_for, jsonify, flash #added flash for auto lock
from urllib.parse import quote
#Jesia recaptcha imports
import os
from recaptcha_helper import verify_recaptcha

from database_init import db
from models.election_creation import ElectionCreation, VotingOption
from models.vote_tokens import VoteToken
from models.voters import Voter

vote_flow_bp = Blueprint("vote_flow", __name__, url_prefix="/vote")

################### To Delete part ######################
#Delete this part. Not needed for the new feature. 
#def parse_deadline(deadline_str):
#    formats = [
#        "%Y-%m-%dT%H:%M",
 #       "%Y-%m-%d %H:%M",
  #      "%Y-%m-%d"
   # ]

    #for fmt in formats:
     #   try:
      #      return datetime.strptime(deadline_str, fmt)
       # except ValueError:
        #    continue
    #return None

 #################### to Delete part ####################   

def build_sticker_data(candidate_name, election_title, voter_id):
    sticker_svg = f"""
    <svg xmlns='http://www.w3.org/2000/svg' width='320' height='320' viewBox='0 0 320 320'>
      <defs>
        <linearGradient id='bg' x1='0%' y1='0%' x2='100%' y2='100%'>
          <stop offset='0%' stop-color='#1a237e'/>
          <stop offset='100%' stop-color='#283593'/>
        </linearGradient>
      </defs>

      <circle cx='160' cy='160' r='150' fill='url(#bg)' stroke='#ffd600' stroke-width='10'/>
      <circle cx='160' cy='160' r='132' fill='none' stroke='#ffd600' stroke-width='3'/>

      <text x='160' y='92' text-anchor='middle'
            font-family='Arial Black, Arial, sans-serif'
            font-size='28' font-weight='900' fill='#ffd600'>
        I VOTED
      </text>

      <text x='160' y='165' text-anchor='middle'
            font-family='Arial, sans-serif'
            font-size='70'>
        🗳️
      </text>

      <text x='160' y='214' text-anchor='middle'
            font-family='Arial, sans-serif'
            font-size='15' fill='#ffffff'>
        Election: {election_title[:26]}
      </text>

      <text x='160' y='238' text-anchor='middle'
            font-family='Arial, sans-serif'
            font-size='13' fill='#e8eaf6'>
        Choice: {candidate_name[:28]}
      </text>

      <text x='160' y='266' text-anchor='middle'
            font-family='Arial, sans-serif'
            font-size='11' fill='#cccccc'>
        Voter ID: {voter_id}
      </text>

      <text x='160' y='290' text-anchor='middle'
            font-family='Arial, sans-serif'
            font-size='11' fill='#aaaaaa'>
        #YouthVotes #Democracy
      </text>
    </svg>
    """.strip()

    share_caption = (
        f"🗳️ I just voted in '{election_title}' and made my voice heard. "
        f"#IVoted #YouthVotes #Democracy"
    )

    encoded_text = quote(share_caption)

    return {
        "sticker_title": "I Voted! 🗳️",
        "sticker_svg": sticker_svg,
        "share_caption": share_caption,
        "candidate_name": candidate_name,
        "election_title": election_title,
        "social_links": {
            "twitter": f"https://twitter.com/intent/tweet?text={encoded_text}",
            "facebook": f"https://www.facebook.com/sharer/sharer.php?u=&quote={encoded_text}"
        }
    }

@vote_flow_bp.route("/select", methods=["GET", "POST"])
def election_select():
    voter_id = session.get("user_id")
    if not voter_id:
        return redirect("/auth/login")

    # if request.method == "POST":
    #     election_id = request.form.get("election_id", type=int)
    #     election = ElectionCreation.query.get(election_id)

    #     if not election:
    #         return "Election not found", 404

    #     session["selected_election_id"] = election.id
    #     return redirect("/token/generate_token")
    ### new ###
    if request.method == "POST":
        election_id = request.form.get("election_id", type=int)
        election = ElectionCreation.query.get(election_id)

        if not election:
            return "Election not found", 404

        if is_election_locked(election):
            session["selected_election_id"] = election.id
            return redirect(url_for("vote_flow.election_closed_page"))

        session["selected_election_id"] = election.id
        return redirect("/token/generate_token")
    ### new ###

    # all_elections = ElectionCreation.query.all()
    # active_elections = []

    # now = datetime.now()
    # for election in all_elections:
    #     deadline = parse_deadline(election.deadline)
    #     if deadline and deadline > now:
    #         active_elections.append(election)

    # return render_template("election_select.html", elections=active_elections)

    #### new ####
    all_elections = ElectionCreation.query.all()
    locked_election_ids = []

    for election in all_elections:
        if is_election_locked(election):
            locked_election_ids.append(election.id)

    return render_template(
        "election_select.html",
        elections=all_elections,
        locked_election_ids = locked_election_ids
    )
    #### new ####


@vote_flow_bp.route("/cast", methods=["GET"])
def vote_cast_page():
    voter_id = session.get("user_id")
    if not voter_id:
        return redirect("/auth/login")

    election_id = session.get("selected_election_id")
    if not election_id:
        return redirect(url_for("vote_flow.election_select"))

    election = ElectionCreation.query.get(election_id)
    if not election:
        return "Election not found", 404
    
    #### new ####
    if is_election_locked(election):
        return redirect(url_for("vote_flow.election_closed_page"))

    # return render_template(
    #     "vote_cast.html",
    #     election=election,
    #     options=election.options
    # )
    #### new jesia recaptcha    ####
    return render_template(
        "vote_cast.html",
        election=election,
        options=election.options,
        recaptcha_site_key=os.getenv("RECAPTCHA_SITE_KEY")
    )
    ########## jesia recaptcha end ############

@vote_flow_bp.route("/submit", methods=["POST"])
def submit_vote():
    voter_id = session.get("user_id")
    if not voter_id:
        return redirect("/auth/login")

    voter = Voter.query.get(voter_id)
    if not voter:
        return "Voter not found", 404

    if voter.has_voted:
        return "You have already voted.", 400

    election_id = session.get("selected_election_id")
    if not election_id:
        return redirect(url_for("vote_flow.election_select"))

    election = ElectionCreation.query.get(election_id)
    if not election:
        return "Election not found", 404

    # deadline = parse_deadline(election.deadline)
    # if not deadline or deadline <= datetime.now():
    #     return "This election is no longer active.", 400
    ### new ###
    if is_election_locked(election):
        return redirect(url_for("vote_flow.election_closed_page"))
    ### new ###
    ######### jesia recaptcha ##########
    recaptcha_response = request.form.get("g-recaptcha-response")
    if not verify_recaptcha(recaptcha_response):
        return "reCAPTCHA verification failed. Please try again.", 400
    ####### Jesia rercaptcha #############


    option_id = request.form.get("candidate_id", type=int)
    token_value = request.form.get("token", "").strip()

    if not option_id:
        return "Please select a candidate.", 400

    if not token_value:
        return "Please enter your token.", 400

    selected_option = VotingOption.query.filter_by(
        id=option_id,
        election_id=election.id
    ).first()

    if not selected_option:
        return "Invalid candidate selection.", 400

    token_obj = VoteToken.query.filter_by(
        token=token_value,
        voter_id=voter_id,
        used=False
    ).first()

    if not token_obj:
        return "Invalid token.", 400

    if token_obj.expires_at:
        expires_at = token_obj.expires_at
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)

        if expires_at <= datetime.now(timezone.utc):
            return "Token expired.", 400

    selected_option.vote_count += 1
    voter.has_voted = True

    db.session.delete(token_obj)
    db.session.commit()

    session["last_vote_candidate"] = selected_option.option_text
    session["last_vote_election"] = election.title

    return redirect("/vote/i-voted")

@vote_flow_bp.route("/i-voted", endpoint="i_voted_page", methods=["GET"])
def i_voted_page():
    voter_id = session.get("user_id")
    if not voter_id:
        return redirect("/auth/login")

    candidate_name = session.get("last_vote_candidate")
    election_title = session.get("last_vote_election")

    if not candidate_name or not election_title:
        return redirect(url_for("vote_flow.election_select"))

    return render_template(
        "i_voted.html",
        candidate_name=candidate_name,
        election_title=election_title
    )

@vote_flow_bp.route("/sticker-data", methods=["GET"])
def sticker_data():
    voter_id = session.get("user_id")
    if not voter_id:
        return jsonify({"error": "Not logged in"}), 401

    candidate_name = session.get("last_vote_candidate")
    election_title = session.get("last_vote_election")

    if not candidate_name or not election_title:
        return jsonify({"error": "No recent vote found"}), 404

    return jsonify(build_sticker_data(candidate_name, election_title, voter_id)), 200

#### new ####
@vote_flow_bp.route("/election-closed", methods=["GET"])
def election_closed_page():
    election_id = session.get("selected_election_id")
    election = None

    if election_id:
        election = ElectionCreation.query.get(election_id)

    return render_template("election_closed.html", election=election)