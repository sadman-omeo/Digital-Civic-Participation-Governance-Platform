from flask import Blueprint, redirect, request, jsonify, render_template
from database_init import db
from models.service_request import ServiceRequest

s_bp = Blueprint("s_bp", __name__, url_prefix="/service_requests")


@s_bp.route("/")
def service_requests_page():
    requests = ServiceRequest.query.all()
    return render_template("service_request.html", requests=requests)



# POST - Create request [POST]
@s_bp.route("/add_service_request", methods=["POST"])
def add_service_request():
    citizen_name = request.values.get("citizen_name")
    citizen_email = request.values.get("citizen_email")
    service_type = request.values.get("service_type")
    description = request.values.get("description")

    if not citizen_name or not service_type or not description:
        return "All fields are required", 400

    new_req = ServiceRequest(
        citizen_name=citizen_name,
        citizen_email=citizen_email,
        service_type=service_type,
        description=description
    )
    

    db.session.add(new_req)
    db.session.commit()
    return redirect("/service_requests")
    #return jsonify("/service_requests")
    #return jsonify({"message" : "Service request created!"}, 201)




# GET - View all requests (API)
@s_bp.route("/get_service_requests", methods=["GET"])
def get_service_requests():

    requests = ServiceRequest.query.all()

    return jsonify([
        {
            "id": r.id,
            "citizen_name": r.citizen_name,
            "citizen_email": r.citizen_email,
            "service_type": r.service_type,
            "description": r.description,
            "status": r.status
        }
        for r in requests
    ])




# PUT - Update request status
@s_bp.route("/update_service_request/<int:request_id>", methods=["POST"])
def update_service_request(request_id):

    req = ServiceRequest.query.get(request_id)

    if not req:
        return "Request not found", 404

    status = request.values.get("status")

    if status:
        req.status = status

    db.session.commit()

    return redirect("/service_requests")





# DELETE - Delete request
@s_bp.route("/delete_service_request/<int:request_id>", methods=["DELETE"])
def delete_service_request(request_id):

    req = ServiceRequest.query.get(request_id)

    if not req:
        return "Request not found", 404

    db.session.delete(req)
    db.session.commit()

    return redirect("/service_requests")
    
