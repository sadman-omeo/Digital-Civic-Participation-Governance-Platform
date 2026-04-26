from flask import Blueprint, render_template, request, session, redirect
from models.audit_log import AuditLog
from models.election_creation import ElectionCreation

audit_bp = Blueprint("audit", __name__, url_prefix="/admin")


def admin_required():
    """Returns redirect if user is not an admin, else None."""
    from models.voters import Voter
    voter_id = session.get("user_id")
    if not voter_id:
        return redirect("/auth/login")
    voter = Voter.query.get(voter_id)
    if not voter or voter.role != "admin":
        return redirect("/")
    return None


@audit_bp.route("/audit-logs")
def audit_logs():
    guard = admin_required()
    if guard:
        return guard

    # ── filter params from query string ──────────────────────────────────────
    filter_election = request.args.get("election_id", type=int)
    filter_status   = request.args.get("status", "")
    filter_ip       = request.args.get("ip", "").strip()

    query = AuditLog.query.order_by(AuditLog.timestamp.desc())

    if filter_election:
        query = query.filter_by(election_id=filter_election)
    if filter_status in ("success", "failed"):
        query = query.filter_by(status=filter_status)
    if filter_ip:
        query = query.filter(AuditLog.ip_address.like(f"%{filter_ip}%"))

    logs      = query.all()
    elections = ElectionCreation.query.order_by(ElectionCreation.title).all()

    # ── build per-IP summary so admin can spot hotspots quickly ──────────────
    ip_counts = {}
    for log in logs:
        if log.status == "success" and not log.cancelled:
            ip_counts[log.ip_address] = ip_counts.get(log.ip_address, 0) + 1

    # IPs that currently sit above the limit (for badge display in template)
    flagged_ips = {ip for ip, count in ip_counts.items() if count > 10}

    return render_template(
        "audit_logs.html",
        logs=logs,
        elections=elections,
        filter_election=filter_election,
        filter_status=filter_status,
        filter_ip=filter_ip,
        flagged_ips=flagged_ips,
        ip_counts=ip_counts,
    )