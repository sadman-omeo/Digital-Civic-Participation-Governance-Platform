from database_init import db


class Candidate(db.Model):
    __tablename__ = "candidate"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(500), nullable=True)
    image = db.Column(db.String(200), nullable=True)