
from datetime import datetime
from flask import Blueprint, render_template, session, redirect, url_for
from database_init import db
from models.notification import Notification
from models.election_creation import ElectionCreation
from models.voters import Voter

notification_bp = Blueprint("notification_bp", __name__, url_prefix="/notifications")


def parse_time(time_str):
    formats = [
        "%Y-%m-%dT%H:%M",
        "%Y-%m-%d %H:%M",
        "%Y-%m-%d"
    ]

    for fmt in formats:
        try:
            return datetime.strptime(time_str, fmt)
        except ValueError:
            continue
    return None


def generate_notifications():
    elections = ElectionCreation.query.all()
    voters = Voter.query.all()
    now = datetime.now()

    for election in elections:
        start_time = parse_time(election.start_time)
        end_time = parse_time(election.deadline)

        if start_time and start_time <= now and not election.start_notified:
            for voter in voters:
                new_notification = Notification(
                    voter_id=voter.NID,
                    election_id=election.id,
                    title="Election Started",
                    message=f"The election '{election.title}' has started. You can now vote.",
                    type="start"
                )
                db.session.add(new_notification)

            election.start_notified = True

        if end_time and end_time <= now and not election.end_notified:
            for voter in voters:
                new_notification = Notification(
                    voter_id=voter.NID,
                    election_id=election.id,
                    title="Election Closed",
                    message=f"The election '{election.title}' has ended. Voting is now closed.",
                    type="end"
                )
                db.session.add(new_notification)

            election.end_notified = True

        if election.result_published and not election.result_notified:
            for voter in voters:
                new_notification = Notification(
                    voter_id=voter.NID,
                    election_id=election.id,
                    title="Result Published",
                    message=f"The result for '{election.title}' has been published.",
                    type="result"
                )
                db.session.add(new_notification)

            election.result_notified = True

    db.session.commit()


@notification_bp.route("/")
def notifications_page():
    voter_id = session.get("user_id")
    if not voter_id:
        return redirect("/auth/login")

    generate_notifications()

    notifications = Notification.query.filter_by(
        voter_id=voter_id
    ).order_by(Notification.created_at.desc()).all()

    return render_template("notifications.html", notifications=notifications)


@notification_bp.route("/mark_read/<int:notification_id>")
def mark_read(notification_id):
    voter_id = session.get("user_id")
    if not voter_id:
        return redirect("/auth/login")

    notification = Notification.query.filter_by(
        id=notification_id,
        voter_id=voter_id
    ).first()

    if notification:
        notification.is_read = True
        db.session.commit()

    return redirect(url_for("notification_bp.notifications_page"))


@notification_bp.route("/mark_all_read")
def mark_all_read():
    voter_id = session.get("user_id")
    if not voter_id:
        return redirect("/auth/login")

    notifications = Notification.query.filter_by(
        voter_id=voter_id,
        is_read=False
    ).all()

    for notification in notifications:
        notification.is_read = True

    db.session.commit()
    return redirect(url_for("notification_bp.notifications_page"))