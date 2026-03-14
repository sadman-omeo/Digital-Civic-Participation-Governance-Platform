# models/election_creation.py
from database_init import db

class ElectionCreation(db.Model):
    __tablename__ = "election_creation"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.String(500), nullable=False)
    deadline = db.Column(db.String(50), nullable=False)

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