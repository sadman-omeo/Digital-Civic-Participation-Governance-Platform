from datetime import datetime

def parse_deadline(deadline_str):
    formats = [
        "%Y-%m-%dT%H:%M",
        "%Y-%m-%d %H:%M",
        "%Y-%m-%d"
    ]

    for fmt in formats:
        try:
            return datetime.strptime(deadline_str, fmt)
        except ValueError:
            continue
    return None


def is_election_locked(election):
    deadline = parse_deadline(election.deadline)
    if not deadline:
        return True
    return datetime.now() >= deadline
