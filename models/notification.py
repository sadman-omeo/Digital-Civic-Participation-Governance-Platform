
from database_init import db

class Notification(db.Model):
    __tablename__ = "notification"

    id = db.Column(db.Integer, primary_key=True)
    voter_id = db.Column(db.String(20), db.ForeignKey("voter.NID"), nullable=False)
    election_id = db.Column(db.Integer, db.ForeignKey("election_creation.id"), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    message = db.Column(db.String(500), nullable=False)
    type = db.Column(db.String(50), nullable=False)  # start / end / result
    is_read = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now(), nullable=False)