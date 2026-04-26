from flask import Blueprint, render_template, request, redirect, jsonify, flash, url_for, session
from database_init import db
from models.complaint import Complaint
from models.voters import Voter  # added

complaint_bp = Blueprint("complaint_bp", __name__, url_prefix="/complaints")

def is_admin():  # added
    voter_id = session.get("user_id")  # added
    if not voter_id:  # added
        return False  # added

    user = Voter.query.get(voter_id)  # added
    return user and user.role == "admin"  # added


@complaint_bp.route("/")
def complaints_page():
    complaints = Complaint.query.all()
    return render_template("complaints.html", complaints=complaints)


# POST - voter submits complaint
@complaint_bp.route("/add", methods=["POST"])
def add_complaint():
    voter_name = request.form.get("voter_name")
    voter_email = request.form.get("voter_email")
    subject = request.form.get("subject")
    message = request.form.get("message")

    if not voter_name or not voter_email or not subject or not message:
        return "All fields are required", 400

    new_complaint = Complaint(
        voter_name=voter_name,
        voter_email=voter_email,
        subject=subject,
        message=message,
        status="Pending"
    )

    db.session.add(new_complaint)
    db.session.commit()

    flash("Complaint submitted successfully.", "success")
    return redirect(url_for("complaint_bp.complaints_page"))


# GET - all complaints API
@complaint_bp.route("/get_all", methods=["GET"])
def get_all_complaints():
    complaints = Complaint.query.all()

    return jsonify([
        {
            "id": c.id,
            "voter_name": c.voter_name,
            "voter_email": c.voter_email,
            "subject": c.subject,
            "message": c.message,
            "status": c.status,
            "admin_reply": c.admin_reply
        }
        for c in complaints
    ])


# GET - one complaint API
@complaint_bp.route("/get/<int:complaint_id>", methods=["GET"])
def get_complaint(complaint_id):
    complaint = Complaint.query.get(complaint_id)

    if not complaint:
        return jsonify({"message": "Complaint Not Found"}), 404

    return jsonify({
        "id": complaint.id,
        "voter_name": complaint.voter_name,
        "voter_email": complaint.voter_email,
        "subject": complaint.subject,
        "message": complaint.message,
        "status": complaint.status,
        "admin_reply": complaint.admin_reply
    })


# GET - admin edit page
# @complaint_bp.route("/edit/<int:complaint_id>", methods=["GET"])
# def edit_complaint_page(complaint_id):
#     complaint = Complaint.query.get(complaint_id)

#     if not complaint:
#         return "Complaint Not Found", 404

#     return render_template("edit_complaint.html", complaint=complaint)

# GET - admin edit page
@complaint_bp.route("/edit/<int:complaint_id>", methods=["GET"])
def edit_complaint_page(complaint_id):
    if not is_admin():  # added
        flash("Only admin can manage complaints.", "danger")  # added
        return redirect(url_for("complaint_bp.complaints_page"))  # added

    complaint = Complaint.query.get(complaint_id)

    if not complaint:
        return "Complaint Not Found", 404

    return render_template("edit_complaint.html", complaint=complaint)


# PUT/POST - admin updates status and reply
# @complaint_bp.route("/update/<int:complaint_id>", methods=["POST", "PUT"])
# def update_complaint(complaint_id):
#     complaint = Complaint.query.get(complaint_id)

#     if not complaint:
#         return "Complaint Not Found", 404

#     status = request.form.get("status")
#     admin_reply = request.form.get("admin_reply")

#     if status is not None and status.strip():
#         complaint.status = status

#     if admin_reply is not None:
#         complaint.admin_reply = admin_reply

#     db.session.commit()

#     flash("Complaint updated successfully.", "success")
#     return redirect(url_for("complaint_bp.complaints_page"))

# PUT/POST - admin updates status and reply
@complaint_bp.route("/update/<int:complaint_id>", methods=["POST", "PUT"])
def update_complaint(complaint_id):
    if not is_admin():  # added
        flash("Only admin can update complaints.", "danger")  # added
        return redirect(url_for("complaint_bp.complaints_page"))  # added

    complaint = Complaint.query.get(complaint_id)

    if not complaint:
        return "Complaint Not Found", 404

    status = request.form.get("status")
    admin_reply = request.form.get("admin_reply")

    if status is not None and status.strip():
        complaint.status = status

    if admin_reply is not None:
        complaint.admin_reply = admin_reply

    db.session.commit()

    flash("Complaint updated successfully.", "success")
    return redirect(url_for("complaint_bp.complaints_page"))


# DELETE/POST - admin deletes complaint
@complaint_bp.route("/delete/<int:complaint_id>", methods=["POST", "DELETE"])
def delete_complaint(complaint_id):
    if not is_admin():  # added
        flash("Only admin can delete complaints.", "danger")  # added
        return redirect(url_for("complaint_bp.complaints_page"))  # added

    complaint = Complaint.query.get(complaint_id)

    if not complaint:
        return jsonify({"message": "Complaint Not Found"}), 404

    db.session.delete(complaint)
    db.session.commit()

    flash("Complaint deleted successfully.", "success")
    return redirect(url_for("complaint_bp.complaints_page"))