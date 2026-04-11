# ============================================================
#  Chatbot Routes - AI Assistant Endpoints
# ============================================================

from flask import Blueprint, request, jsonify, render_template
from models.chatbot import ChatbotService, ChatModel

# Initialize chatbot blueprint
chat_bp = Blueprint('chat', __name__, url_prefix='/api/chat')

# Initialize services
chatbot_service = ChatbotService()
chat_model = ChatModel()


@chat_bp.route("", methods=["POST"])
def chat():
    """
    Send a message to the AI chatbot and receive a reply.
    
    The chatbot provides voter support, answering questions about voting,
    democracy, and encouraging civic participation.

    Body (JSON):
        { "session_id": "<string>", "message": "<string>" }

    Returns (JSON):
        { "session_id", "user_message", "bot_reply", "timestamp" }
    """
    data = request.get_json()
    if not data or "message" not in data:
        return jsonify({"error": "Missing 'message' in request body."}), 400

    session_id = data.get("session_id")
    user_message = data["message"].strip()

    if not user_message:
        return jsonify({"error": "Message cannot be empty."}), 400

    # Get or create session
    session = chat_model.get_or_create_session(session_id)
    session_id = session.session_id

    # Get bot reply from AI chatbot
    bot_reply = chatbot_service.get_reply(user_message)

    # Store messages in session history
    chat_model.add_message(session_id, "user", user_message)
    chat_model.add_message(session_id, "bot", bot_reply)

    return jsonify({
        "session_id": session_id,
        "user_message": user_message,
        "bot_reply": bot_reply,
        "timestamp": chat_model.sessions[session_id].messages[-1]["timestamp"]
    }), 200


@chat_bp.route("/chatbot", methods=["GET"])
def chatbot_page():
    return render_template("chatbot.html")


@chat_bp.route("/history", methods=["GET"])
def chat_history():
    """
    Retrieve complete chat history for a session.

    Query param: ?session_id=<string>

    Returns (JSON):
        { "session_id", "message_count", "history": [ ... ] }
    """
    session_id = request.args.get("session_id", "").strip()
    if not session_id:
        return jsonify({"error": "Provide 'session_id' as a query parameter."}), 400

    history = chat_model.get_history(session_id)
    if not history:
        return jsonify({"error": "Session not found."}), 404

    return jsonify({
        "session_id": session_id,
        "message_count": history.get_message_count(),
        "history": history.get_messages()
    }), 200


@chat_bp.route("/sessions", methods=["GET"])
def chat_sessions():
    """List all active chat session IDs with message counts."""
    sessions = chat_model.get_all_sessions()
    return jsonify({
        "total_sessions": len(sessions),
        "sessions": sessions
    }), 200


@chat_bp.route("/clear", methods=["DELETE"])
def clear_chat():
    """
    Delete chat history for a specific session.

    Body (JSON):  { "session_id": "<string>" }
    """
    data = request.get_json()
    if not data or "session_id" not in data:
        return jsonify({"error": "Missing 'session_id' in request body."}), 400

    session_id = data["session_id"]
    if chat_model.clear_session(session_id):
        return jsonify({"message": f"Chat history for '{session_id}' cleared."}), 200
    return jsonify({"error": "Session not found."}), 404
