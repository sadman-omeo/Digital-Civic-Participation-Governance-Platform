from flask_socketio import SocketIO

# single socketio instance to avoid circular imports
# use threading async mode to avoid eventlet deprecation warnings
socketio = SocketIO(cors_allowed_origins="*", async_mode="threading")
