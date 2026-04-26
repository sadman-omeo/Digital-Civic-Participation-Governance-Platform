from database_init import db

class VoteToken(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    token = db.Column(db.String(200), unique=True)
    voter_id = db.Column(db.Integer, db.ForeignKey("voter.NID"))
    created_at = db.Column(db.DateTime)
    expires_at = db.Column(db.DateTime)
    used = db.Column(db.Boolean, default=False)