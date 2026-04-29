# routes/results.py
from io import BytesIO
from datetime import datetime
from threading import Lock  # added

import matplotlib
matplotlib.use("Agg")
from matplotlib.figure import Figure  # changed

from flask import Blueprint, render_template, request, send_file, make_response, jsonify, session, redirect, url_for
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

from models.election_creation import ElectionCreation, VotingOption
from models.voters import Voter  # added

result_bp = Blueprint("result_bp", __name__, url_prefix="/results")

def admin_only_guard():  # added
    voter_id = session.get("user_id")
    if not voter_id:
        return None, redirect("/auth/login")

    user = Voter.query.get(voter_id)
    if not user or user.role != "admin":
        return None, redirect("/dashboard")

    return user, None


chart_lock = Lock()  # added


def get_election_data(election_id):
    election = ElectionCreation.query.get(election_id)
    if not election:
        return None, [], [], []

    options = VotingOption.query.filter_by(election_id=election_id).all()
    labels = [option.option_text for option in options]
    votes = [option.vote_count or 0 for option in options]

    return election, options, labels, votes


@result_bp.route("/")
def results_page():
    elections = ElectionCreation.query.order_by(ElectionCreation.id.desc()).all()

    selected_election_id = request.args.get("election_id", type=int)
    if not selected_election_id and elections:
        selected_election_id = elections[0].id

    selected_election = None
    options = []
    total_votes = 0
    winner = None

    if selected_election_id:
        selected_election, options, labels, votes = get_election_data(selected_election_id)

        if selected_election:
            total_votes = sum(votes)

            if options and total_votes > 0:
                winner = max(options, key=lambda option: option.vote_count or 0)

    return render_template(
        "results.html",
        elections=elections,
        selected_election=selected_election,
        options=options,
        total_votes=total_votes,
        winner=winner
    )


@result_bp.route("/bar-chart/<int:election_id>")
def bar_chart(election_id):
    election, options, labels, votes = get_election_data(election_id)

    if not election:
        return "Election not found", 404

    with chart_lock:  # added
        fig = Figure(figsize=(10, 5))  # changed
        ax = fig.subplots()  # changed

        bars = ax.bar(labels, votes)

        ax.set_title(f"Bar Chart - {election.title}")
        ax.set_xlabel("Candidates")
        ax.set_ylabel("Votes")
        ax.tick_params(axis="x", rotation=15)

        max_vote = max(votes) if votes else 0
        extra_height = 0.5 if max_vote == 0 else max_vote * 0.05

        for bar, vote in zip(bars, votes):
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                vote + extra_height,
                str(vote),
                ha="center",
                va="bottom"
            )

        fig.tight_layout()

        img = BytesIO()
        fig.savefig(img, format="png", bbox_inches="tight")  # changed
        img.seek(0)

    response = make_response(send_file(img, mimetype="image/png"))
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response


@result_bp.route("/pie-chart/<int:election_id>")
def pie_chart(election_id):
    election, options, labels, votes = get_election_data(election_id)

    if not election:
        return "Election not found", 404

    with chart_lock:  # added
        fig = Figure(figsize=(7, 7))  # changed
        ax = fig.subplots()  # changed

        if sum(votes) == 0:
            ax.text(
                0.5, 0.5,
                "No votes yet",
                ha="center",
                va="center",
                fontsize=18,
                transform=ax.transAxes
            )
            ax.axis("off")
        else:
            ax.pie(votes, labels=labels, autopct="%1.1f%%", startangle=90)
            ax.set_title(f"Pie Chart - {election.title}")
            ax.axis("equal")

        fig.tight_layout()

        img = BytesIO()
        fig.savefig(img, format="png", bbox_inches="tight")  # changed
        img.seek(0)

    response = make_response(send_file(img, mimetype="image/png"))
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response


@result_bp.route("/download-pdf/<int:election_id>")
def download_pdf(election_id):
    election, options, labels, votes = get_election_data(election_id)

    if not election:
        return "Election not found", 404

    total_votes = sum(votes)
    winner = None

    if options and total_votes > 0:
        winner = max(options, key=lambda option: option.vote_count or 0)

    pdf_buffer = BytesIO()
    pdf = canvas.Canvas(pdf_buffer, pagesize=A4)

    width, height = A4
    y = height - 50

    pdf.setTitle(f"{election.title} Results")
    pdf.setFont("Helvetica-Bold", 18)
    pdf.drawString(50, y, "Election Result Report")

    y -= 30
    pdf.setFont("Helvetica", 12)
    pdf.drawString(50, y, f"Election Title: {election.title}")

    y -= 20
    pdf.drawString(50, y, f"Description: {election.description}")

    y -= 20
    pdf.drawString(50, y, f"Start Time: {election.start_time}")

    y -= 20
    pdf.drawString(50, y, f"Deadline: {election.deadline}")

    y -= 20
    pdf.drawString(50, y, f"Generated At: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    y -= 30
    pdf.setFont("Helvetica-Bold", 13)
    pdf.drawString(50, y, f"Total Votes: {total_votes}")

    y -= 20
    if winner:
        pdf.drawString(50, y, f"Winner: {winner.option_text} ({winner.vote_count} votes)")
    else:
        pdf.drawString(50, y, "Winner: No winner yet")

    y -= 35
    pdf.setFont("Helvetica-Bold", 14)
    pdf.drawString(50, y, "Candidate-wise Results")

    y -= 25
    pdf.setFont("Helvetica", 12)

    for index, option in enumerate(options, start=1):
        percentage = (option.vote_count / total_votes * 100) if total_votes > 0 else 0
        pdf.drawString(
            60,
            y,
            f"{index}. {option.option_text} - {option.vote_count} votes ({percentage:.2f}%)"
        )
        y -= 22

        if y < 60:
            pdf.showPage()
            y = height - 50
            pdf.setFont("Helvetica", 12)

    pdf.save()
    pdf_buffer.seek(0)

    return send_file(
        pdf_buffer,
        mimetype="application/pdf",
        as_attachment=True,
        download_name=f"election_{election.id}_results.pdf"
    )



@result_bp.route("/live")
def live_results_page():  # added
    user, blocked_response = admin_only_guard()
    if blocked_response:
        return blocked_response

    elections = ElectionCreation.query.order_by(ElectionCreation.id.desc()).all()
    return render_template("live_results.html", elections=elections)


@result_bp.route("/api/elections")
def live_results_elections_api():  # added
    user, blocked_response = admin_only_guard()
    if blocked_response:
        return jsonify({"error": "Unauthorized"}), 403

    elections = ElectionCreation.query.order_by(ElectionCreation.id.desc()).all()

    return jsonify([
        {
            "id": election.id,
            "title": election.title
        }
        for election in elections
    ])


@result_bp.route("/api/election/<int:election_id>")
def live_results_single_election_api(election_id):  # added
    user, blocked_response = admin_only_guard()
    if blocked_response:
        return jsonify({"error": "Unauthorized"}), 403

    election = ElectionCreation.query.get(election_id)
    if not election:
        return jsonify({"error": "Election not found"}), 404

    options = VotingOption.query.filter_by(election_id=election_id).all()

    return jsonify({
        "id": election.id,
        "title": election.title,
        "options": [
            {
                "id": option.id,
                "name": option.option_text,
                "votes": option.vote_count
            }
            for option in options
        ]
    })
