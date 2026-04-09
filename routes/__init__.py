"""Routes package for Voter Support System."""

from .ui import ui_bp
from .chatbot import chat_bp
from .voting import vote_bp

__all__ = ["ui_bp", "chat_bp", "vote_bp"]

