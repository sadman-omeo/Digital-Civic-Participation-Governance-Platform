from datetime import datetime, timezone
from flask import Blueprint, render_template, request, redirect, session, url_for

from database_init import db
from models.election_creation import ElectionCreation, VotingOption
from models.vote_tokens import VoteToken
from models.voters import Voter

vote_flow_bp = Blueprint("vote_flow", __name__, url_prefix="/vote")


def parse_deadline(deadline_str):
    formats = [
        "%Y-%m-%dT%H:%M",
        "%Y-%m-%d %H:%M",
        "%Y-%m-%d"
    ]

    for fmt in formats:
        try:
            return datetime.strptime(deadline_str, fmt)
        except ValueError:
            continue
    return None


@vote_flow_bp.route("/select", methods=["GET", "POST"])
def election_select():
    voter_id = session.get("user_id")
    if not voter_id:
        return redirect("/auth/login")

    if request.method == "POST":
        election_id = request.form.get("election_id", type=int)
        election = ElectionCreation.query.get(election_id)

        if not election:
            return "Election not found", 404

        session["selected_election_id"] = election.id
        return redirect("/token/generate_token")

    all_elections = ElectionCreation.query.all()
    active_elections = []

    now = datetime.now()
    for election in all_elections:
        deadline = parse_deadline(election.deadline)
        if deadline and deadline > now:
            active_elections.append(election)

    return render_template("election_select.html", elections=active_elections)


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

    return render_template(
        "vote_cast.html",
        election=election,
        options=election.options
    )


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

    deadline = parse_deadline(election.deadline)
    if not deadline or deadline <= datetime.now():
        return "This election is no longer active.", 400

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

    return render_template(
        "vote_cast.html",
        election=election,
        options=election.options,
        success_message=f"Vote submitted successfully for {selected_option.option_text}."
    )