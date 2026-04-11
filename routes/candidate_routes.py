import os
from werkzeug.utils import secure_filename
from flask import Blueprint, render_template, request, redirect, jsonify, current_app, flash, url_for
from database_init import db
from models.candidate import Candidate

c_bp = Blueprint("c_bp", __name__, url_prefix="/candidates")


@c_bp.route("")
def candidates_page():
    candidates = Candidate.query.all()
    return render_template("candidates.html", candidates=candidates)


@c_bp.route("/add", methods=["POST"])
def add_candidate():
    name = request.form.get("name")
    category = request.form.get("category")
    description = request.form.get("description")
    image_file = request.files.get("image")

    if not name or not category:
        return "name and category are required", 400

    filename = None
    if image_file and image_file.filename:
        filename = secure_filename(image_file.filename)
        image_path = os.path.join(current_app.config["UPLOAD_FOLDER"], filename)
        image_file.save(image_path)

    new_candidate = Candidate(
        name=name,
        category=category,
        description=description,
        image=filename
    )

    db.session.add(new_candidate)
    db.session.commit()
    flash("Candidate added successfully.", "success")
    return redirect(url_for("c_bp.candidates_page"))


@c_bp.route("/get_all", methods=["GET"])
def get_candidates():
    candidates = Candidate.query.all()

    return jsonify([
        {
            "id": c.id,
            "name": c.name,
            "category": c.category,
            "description": c.description,
            "image": c.image
        }
        for c in candidates
    ])


@c_bp.route("/get/<int:candidate_id>", methods=["GET"])
def get_candidate(candidate_id):
    candidate = Candidate.query.get(candidate_id)

    if not candidate:
        return jsonify({"message": "Candidate Not Found"}), 404

    return jsonify({
        "id": candidate.id,
        "name": candidate.name,
        "category": candidate.category,
        "description": candidate.description,
        "image": candidate.image
    })


@c_bp.route("/edit/<int:candidate_id>", methods=["GET"])
def edit_candidate_page(candidate_id):
    candidate = Candidate.query.get(candidate_id)

    if not candidate:
        return "Candidate Not Found", 404

    return render_template("edit_candidate.html", candidate=candidate)


@c_bp.route("/update/<int:candidate_id>", methods=["POST", "PUT"])
def update_candidate(candidate_id):
    candidate = Candidate.query.get(candidate_id)

    if not candidate:
        return "Candidate Not Found", 404

    name = request.form.get("name")
    category = request.form.get("category")
    description = request.form.get("description")
    image_file = request.files.get("image")

    if name is not None and name.strip():
        candidate.name = name
    if category is not None and category.strip():
        candidate.category = category
    if description is not None:
        candidate.description = description

    if image_file and image_file.filename:
        filename = secure_filename(image_file.filename)
        image_path = os.path.join(current_app.config["UPLOAD_FOLDER"], filename)
        image_file.save(image_path)
        candidate.image = filename

    db.session.commit()
    flash("Candidate updated successfully.", "success")
    return redirect(url_for("c_bp.candidates_page"))


@c_bp.route("/delete/<int:candidate_id>", methods=["POST", "DELETE"])
def delete_candidate(candidate_id):
    candidate = Candidate.query.get(candidate_id)

    if not candidate:
        return jsonify({"message": "Candidate Not Found"}), 404

    db.session.delete(candidate)
    db.session.commit()

    flash("Candidate deleted successfully.", "success")
    return redirect(url_for("c_bp.candidates_page"))