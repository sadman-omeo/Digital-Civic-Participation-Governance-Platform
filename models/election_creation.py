# models/election_creation.py
from database_init import db

class ElectionCreation(db.Model):
    __tablename__ = "election_creation"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.String(500), nullable=False)
    start_time = db.Column(db.String(50), nullable=False)  # added for election start reminder
    deadline = db.Column(db.String(50), nullable=False)
    result_published = db.Column(db.Boolean, default=False, nullable=False)  # added for result published notification
    start_notified = db.Column(db.Boolean, default=False, nullable=False)  # added to avoid duplicate start notifications
    end_notified = db.Column(db.Boolean, default=False, nullable=False)  # added to avoid duplicate end notifications
    result_notified = db.Column(db.Boolean, default=False, nullable=False)  # added to avoid duplicate result notifications

    options = db.relationship(
        "VotingOption",
        backref="election",
        cascade="all, delete-orphan",
        lazy=True
    )


class VotingOption(db.Model):
    __tablename__ = "voting_option"

    id = db.Column(db.Integer, primary_key=True)
    option_text = db.Column(db.String(200), nullable=False)
    election_id = db.Column(
        db.Integer,
        db.ForeignKey("election_creation.id"),
        nullable=False
    )
    vote_count = db.Column(db.Integer, default=0, nullable=False)