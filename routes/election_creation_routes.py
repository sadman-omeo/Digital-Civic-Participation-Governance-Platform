# routes/election_creation_routes.py
from flask import Blueprint, render_template, request, redirect, url_for, flash
from database_init import db
from models.election_creation import ElectionCreation, VotingOption

e_bp = Blueprint("e_bp", __name__, url_prefix="/election_creation")


@e_bp.route("/")
def election_creation_page():
    elections = ElectionCreation.query.all()
    return render_template("election_creation.html", elections=elections)


@e_bp.route("/add_election", methods=["POST"])
def add_election():
    title = request.form.get("title")
    description = request.form.get("description")
    deadline = request.form.get("deadline")

    option1 = request.form.get("option1")
    option2 = request.form.get("option2")
    option3 = request.form.get("option3")
    option4 = request.form.get("option4")

    if not title or not description or not deadline:
        return "Title, description, and deadline are required", 400

    if not option1 or not option2:
        return "At least two options are required", 400

    new_election = ElectionCreation(
        title=title,
        description=description,
        deadline=deadline
    )

    db.session.add(new_election)
    db.session.commit()

    options = [option1, option2, option3, option4]

    for opt in options:
        if opt and opt.strip():
            new_option = VotingOption(
                option_text=opt.strip(),
                election_id=new_election.id
            )
            db.session.add(new_option)

    db.session.commit()

    flash("Election created successfully!")
    return redirect(url_for("e_bp.election_creation_page"))