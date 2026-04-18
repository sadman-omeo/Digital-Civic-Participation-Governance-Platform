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