from database_init import db



class VotingTopic(db.Model):
    __tablename__ = "voting_topic"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.String(500), nullable=False)
    deadline = db.Column(db.String(50), nullable=False)


class VotingOption(db.Model):
    __tablename__ = "voting_option"

    id = db.Column(db.Integer, primary_key=True)
    topic_id = db.Column(db.Integer, db.ForeignKey("voting_topic.id"), nullable=False)
    option_text = db.Column(db.String(200), nullable=False)

