from datetime import datetime
from database_init import db


class AuditLog(db.Model):
    # Correct SQLAlchemy table naming attribute to map to the audit_log table
    __tablename__ = "audit_log"

    id            = db.Column(db.Integer, primary_key=True)
    voter_nid     = db.Column(db.String(20), db.ForeignKey("voter.NID"), nullable=True)
    election_id   = db.Column(db.Integer,    db.ForeignKey("election_creation.id"), nullable=True)
    candidate_id  = db.Column(db.Integer,    db.ForeignKey("voting_option.id"), nullable=True)
    ip_address    = db.Column(db.String(64),  nullable=False)
    status        = db.Column(db.String(16),  nullable=False)   # "success" | "failed"
    fail_reason   = db.Column(db.String(200), nullable=True)    # populated only on failure
    cancelled     = db.Column(db.Boolean,     default=False, nullable=False)
    timestamp     = db.Column(db.DateTime,    default=datetime.utcnow, nullable=False)