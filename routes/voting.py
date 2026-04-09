# ============================================================
#  Voting Routes - Vote Casting and "I Voted" Sticker Endpoints
# ============================================================

from flask import Blueprint, request, jsonify
from models import VotingModel

# Initialize voting blueprint
vote_bp = Blueprint('vote', __name__, url_prefix='/api/vote')

# Initialize voting model
voting_model = VotingModel()


@vote_bp.route("", methods=["POST"])
def cast_vote():
    """
    Cast a vote for a candidate and receive a virtual "I Voted" sticker.
    
    This endpoint promotes youth participation by providing a virtual sticker
    that can be shared on social media to encourage other young voters.

    Body (JSON):
        {
            "voter_id"  : "<string>",
            "candidate" : "Candidate A" | "Candidate B" | "Candidate C"
        }

    Returns (JSON):
        { "voter_id", "candidate", "sticker_url", "share_message", "timestamp" }
    """
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body must be JSON."}), 400

    voter_id = data.get("voter_id", "").strip()
    candidate = data.get("candidate", "").strip()

    if not voter_id:
        return jsonify({"error": "Missing 'voter_id'."}), 400
    if not candidate:
        return jsonify({"error": "Missing 'candidate'."}), 400
    if not voting_model.is_valid_candidate(candidate):
        return jsonify({
            "error": f"Invalid candidate. Choose from: {voting_model.get_candidates()}"
        }), 400
    if voting_model.has_voted(voter_id):
        vote_info = voting_model.get_vote_info(voter_id)
        return jsonify({
            "error": "You have already voted!",
            "voter_id": voter_id,
            "voted_for": vote_info.candidate
        }), 409

    try:
        vote = voting_model.cast_vote(voter_id, candidate)
        sticker_url = request.host_url + "api/vote/sticker?voter_id=" + voter_id
        share_message = (
            f"🗳️ I just voted for {candidate}! "
            "Exercise your right — every vote shapes our future! #IVoted #Democracy #YouthVotes"
        )

        return jsonify({
            "message": "Vote cast successfully! 🎉",
            "voter_id": voter_id,
            "candidate": candidate,
            "sticker_url": sticker_url,
            "share_message": share_message,
            "timestamp": vote.timestamp
        }), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400


@vote_bp.route("/status", methods=["GET"])
def vote_status():
    """
    Check if a voter has already cast their vote.

    Query param: ?voter_id=<string>
    
    Returns:
        { "voter_id", "has_voted", "voted_for": (optional), "voted_at": (optional) }
    """
    voter_id = request.args.get("voter_id", "").strip()
    if not voter_id:
        return jsonify({"error": "Provide 'voter_id' as a query parameter."}), 400

    if voting_model.has_voted(voter_id):
        vote_info = voting_model.get_vote_info(voter_id)
        return jsonify({
            "voter_id": voter_id,
            "has_voted": True,
            "voted_for": vote_info.candidate,
            "voted_at": vote_info.timestamp
        }), 200

    return jsonify({"voter_id": voter_id, "has_voted": False}), 200


@vote_bp.route("/stats", methods=["GET"])
def vote_stats():
    """
    Get overall voting statistics.
    
    Returns candidate-wise vote counts, percentages, and last update time.
    """
    stats = voting_model.get_vote_stats()
    return jsonify(stats), 200


@vote_bp.route("/sticker", methods=["GET"])
def get_sticker():
    """
    Get the virtual "I Voted" sticker for a voter to share on social media.
    
    This sticker encourages youth participation and can be shared on Twitter, 
    Facebook, and other social platforms.

    Query param: ?voter_id=<string>

    Returns (JSON): sticker data with SVG content and social media links
    """
    voter_id = request.args.get("voter_id", "").strip()
    if not voter_id:
        return jsonify({"error": "Provide 'voter_id' as a query parameter."}), 400

    try:
        sticker_data = voting_model.generate_sticker(voter_id)
        return jsonify(sticker_data), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 404


@vote_bp.route("/candidates", methods=["GET"])
def get_candidates():
    """Return the list of valid candidates available for voting."""
    return jsonify({"candidates": voting_model.get_candidates()}), 200
