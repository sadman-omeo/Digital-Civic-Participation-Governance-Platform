from database_init import db
class Voter(db.Model):
    NID = db.Column(db.String(20), primary_key=True)
    Name = db.Column(db.String(100), nullable=False)
    Password = db.Column(db.String(200), nullable=False)
    Phone = db.Column(db.String(15), unique=True, nullable=False)
    Email = db.Column(db.String(120), unique=True, nullable=False)
    role = db.Column(db.String(20), default="voter")
    is_active = db.Column(db.Boolean, default=True)
    has_voted = db.Column(db.Boolean, default=False)
    # path to uploaded registration photo (relative to static/uploads)
    photo = db.Column(db.String(200), nullable=True)
    # Pickled face encoding vector (list/array) computed at registration
    face_encoding = db.Column(db.PickleType, nullable=True)
    # New fields for tracking vote information and edits
    last_vote_candidate = db.Column(db.String(255), nullable=True)
    last_vote_election = db.Column(db.String(255), nullable=True)
    vote_notes = db.Column(db.Text, nullable=True)
    last_edited_at = db.Column(db.DateTime, nullable=True)