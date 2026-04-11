from flask import Blueprint, request, render_template, session, redirect, url_for, jsonify
from models.voters import Voter
from database_init import db

admin_bp= Blueprint("admin", __name__, url_prefix="/admin")

@admin_bp.route("/getVoters")
def getVoters():
    voters = Voter.query.all()

    return render_template("allvoters.html", voters=voters)

@admin_bp.route("/voter/<nid>/edit", methods=["GET", "POST"])
def edit_voter(nid):
    if request.method=="GET":
        voter= Voter.query.filter_by(NID=nid).first()
        return render_template("update_voters.html", voter=voter)

    voter = Voter.query.get_or_404(nid)
    name = request.form.get("name")
    phone = request.form.get("phone")
    email = request.form.get("email")
    role=request.form.get("role")
    voter.Name = name
    voter.Phone = phone
    voter.Email = email
    voter.role= role

    db.session.commit()
    return redirect("/admin/getVoters")

@admin_bp.route("/voter/<nid>/deactivate", methods=["POST"])
def deactivate_voter(nid):

    voter = Voter.query.get_or_404(nid)
    if voter.is_active == False:
        voter.is_active = True
    else:
        voter.is_active = False









    db.session.commit()
    return redirect("/admin/getVoters")