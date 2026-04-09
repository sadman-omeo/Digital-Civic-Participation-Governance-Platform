# ============================================================
#  Chatbot Models - AI Assistant for Voter Support
# ============================================================

from datetime import datetime
from typing import Dict, List, Optional
import uuid
import os
from dotenv import load_dotenv
from groq import Groq

# Load environment variables
load_dotenv()


class ChatbotService:
    """
    Groq-powered AI chatbot for voter support.
    Provides intelligent responses to voter inquiries about voting, democracy, and civic participation.
    """

    SYSTEM_PROMPT = """You are a friendly and helpful AI chatbot designed to assist users with questions about voting, democracy, and this voting app. 
You are part of a Voter Support System that encourages youth participation in democracy.

Your responsibilities:
- Provide clear, concise, and informative responses
- Be encouraging about civic participation and voting
- Help guide users through the voting process
- Answer questions about the app's features (chatbot and voting)
- Promote the sharing of "I Voted" stickers on social media to inspire youth
- Use appropriate emojis to make responses friendly and engaging
- Keep responses concise but helpful

Context:
- This is a Flask-based Voter Support System with an AI chatbot and virtual "I Voted" sticker feature
- Users can vote for candidates and receive a virtual "I Voted" sticker to share on social media
- Student ID: 23301111 | Lab 04 Flask API Assignment
- Available features: 
  * AI Chatbot for voter support 💬
  * Vote for candidates 🗳️
  * Share "I Voted" sticker on social media 📲"""

    def __init__(self):
        """Initialize Groq client for chatbot."""
        groq_api_key = os.getenv("groq_api")
        if not groq_api_key:
            raise ValueError("GROQ_API_KEY not found in .env file")
        self.client = Groq(api_key=groq_api_key)

    def get_reply(self, user_message: str) -> str:
        """
        Get an intelligent response from the Groq AI chatbot.
        
        Args:
            user_message: The user's question or statement
            
        Returns:
            AI-generated response from the chatbot
        """
        try:
            completion = self.client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": self.SYSTEM_PROMPT},
                    {"role": "user", "content": user_message}
                ],
                temperature=1,
                max_completion_tokens=1024,
                top_p=1,
                stream=False,
                stop=None
            )
            return completion.choices[0].message.content
        except Exception as e:
            return f"I'm having trouble connecting to my AI engine right now. Please try again in a moment. (Error: {str(e)})"


class ChatSession:
    """Represent a single chat session for a user."""

    def __init__(self, session_id: Optional[str] = None):
        """
        Initialize a chat session.
        
        Args:
            session_id: Optional session ID. If not provided, a new UUID will be generated.
        """
        self.session_id = session_id or str(uuid.uuid4())
        self.messages: List[Dict] = []

    def add_message(self, role: str, text: str) -> None:
        """
        Add a message to the session.
        
        Args:
            role: Either "user" or "bot"
            text: The message content
        """
        self.messages.append({
            "role": role,
            "text": text,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })

    def get_messages(self) -> List[Dict]:
        """Get all messages in the session."""
        return self.messages

    def get_message_count(self) -> int:
        """Get the total number of messages in the session."""
        return len(self.messages)


class ChatModel:
    """Manage all chat sessions and histories."""

    def __init__(self):
        """Initialize chat model with empty sessions."""
        self.sessions: Dict[str, ChatSession] = {}

    def get_or_create_session(self, session_id: Optional[str] = None) -> ChatSession:
        """
        Get an existing session or create a new one.
        
        Args:
            session_id: Optional session ID to retrieve
            
        Returns:
            ChatSession object
        """
        if session_id and session_id in self.sessions:
            return self.sessions[session_id]

        session = ChatSession(session_id)
        self.sessions[session.session_id] = session
        return session

    def add_message(self, session_id: str, role: str, text: str) -> None:
        """
        Add a message to a specific session.
        
        Args:
            session_id: The session ID
            role: Either "user" or "bot"
            text: The message content
        """
        session = self.get_or_create_session(session_id)
        session.add_message(role, text)

    def get_history(self, session_id: str) -> Optional[ChatSession]:
        """
        Get chat history for a specific session.
        
        Args:
            session_id: The session ID
            
        Returns:
            ChatSession object or None if not found
        """
        return self.sessions.get(session_id)

    def get_all_sessions(self) -> List[Dict]:
        """Get information about all active sessions."""
        return [
            {"session_id": sid, "message_count": session.get_message_count()}
            for sid, session in self.sessions.items()
        ]

    def clear_session(self, session_id: str) -> bool:
        """
        Delete a specific chat session.
        
        Args:
            session_id: The session ID to delete
            
        Returns:
            True if session was deleted, False if not found
        """
        if session_id in self.sessions:
            del self.sessions[session_id]
            return True
        return False
