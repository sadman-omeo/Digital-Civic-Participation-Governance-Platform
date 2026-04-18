from flask import Blueprint, render_template, request, redirect, url_for, flash
from database_init import db
from models.election_creation import ElectionCreation, VotingOption
from models.candidate import Candidate

e_bp = Blueprint("e_bp", __name__, url_prefix="/election_creation")


@e_bp.route("/")
def election_creation_page():
    elections = ElectionCreation.query.all()
    candidates = Candidate.query.all()
    return render_template("election_creation.html", elections=elections, candidates=candidates)


@e_bp.route("/add_election", methods=["POST"])
def add_election():
    title = request.form.get("title")
    description = request.form.get("description")
    start_time = request.form.get("start_time")  # added
    deadline = request.form.get("deadline")

    option1 = request.form.get("option1")
    option2 = request.form.get("option2")
    option3 = request.form.get("option3")
    option4 = request.form.get("option4")

    if not title or not description or not start_time or not deadline:  # changed
        return "Title, description, start time, and deadline are required", 400  # changed

    if not option1 or not option2:
        return "At least two candidate options are required", 400

    candidate_ids = [option1, option2, option3, option4]
    selected_candidate_ids = []
    for cid in candidate_ids:
        if cid and cid.strip():
            selected_id = int(cid)
            if selected_id in selected_candidate_ids:
                return "Each voting option must choose a different candidate.", 400
            selected_candidate_ids.append(selected_id)

    if len(selected_candidate_ids) < 2:
        return "At least two candidate options are required", 400

    # Ensure all selected candidates exist
    candidates = Candidate.query.filter(Candidate.id.in_(selected_candidate_ids)).all()
    if len(candidates) != len(selected_candidate_ids):
        return "One or more selected candidates are invalid", 400

    new_election = ElectionCreation(
        title=title,
        description=description,
        start_time=start_time,  # added
        deadline=deadline
    )

    db.session.add(new_election)
    db.session.commit()

    for candidate_id in selected_candidate_ids:
        candidate = next((c for c in candidates if c.id == candidate_id), None)
        if candidate:
            option_text = f"[{candidate.description}] {candidate.name}" if candidate.description else candidate.name
            new_option = VotingOption(
                option_text=option_text,
                election_id=new_election.id
            )
            db.session.add(new_option)

    db.session.commit()

    flash("Election created successfully!")
    return redirect(url_for("e_bp.election_creation_page"))