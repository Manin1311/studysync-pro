from flask_sqlalchemy import SQLAlchemy  # pyright: ignore[reportMissingImports]
from flask_login import LoginManager  # pyright: ignore[reportMissingImports]

# Create extensions here to avoid circular imports
db = SQLAlchemy()
login_manager = LoginManager()

from flask_socketio import SocketIO
socketio = SocketIO(cors_allowed_origins="*")

