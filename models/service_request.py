from database_init import db

class ServiceRequest(db.Model):
    __tablename__ = 'service_request'

    id = db.Column(db.Integer, primary_key=True)
    citizen_name = db.Column(db.String(100), nullable=False)
    citizen_email = db.Column(db.String(100), nullable=False)
    service_type = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(500), nullable=False)
    status = db.Column(db.String(20), nullable=False, default='Submitted')
    