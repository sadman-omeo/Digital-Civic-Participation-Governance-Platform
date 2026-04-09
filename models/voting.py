# ============================================================
#  Voting Models - Virtual Sticker and Vote Management
# ============================================================

from datetime import datetime
from typing import Dict, List, Optional


class VoteRecord:
    """Represent a single vote cast by a voter."""

    def __init__(self, voter_id: str, candidate: str):
        """
        Initialize a vote record.
        
        Args:
            voter_id: Unique identifier for the voter
            candidate: The candidate voted for
        """
        self.voter_id = voter_id
        self.candidate = candidate
        self.timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")


class VotingModel:
    """
    Manage voting system and "I Voted" virtual sticker distribution.
    
    Features:
    - Track votes from unique voters
    - Prevent duplicate voting
    - Generate voting statistics
    - Manage virtual "I Voted" stickers for social media sharing
    """

    CANDIDATES = ["Candidate A", "Candidate B", "Candidate C"]
    
    STICKER_SVG_TEMPLATE = """<svg xmlns='http://www.w3.org/2000/svg' width='300' height='300' viewBox='0 0 300 300'>
  <circle cx='150' cy='150' r='145' fill='#1a237e' stroke='#ffd600' stroke-width='8'/>
  <circle cx='150' cy='150' r='130' fill='none' stroke='#ffd600' stroke-width='3'/>
  <text x='150' y='100' text-anchor='middle' font-family='Arial Black' font-size='26'
        font-weight='900' fill='#ffd600'>I VOTED</text>
  <text x='150' y='170' text-anchor='middle' font-family='Arial' font-size='60'>🗳️</text>
  <text x='150' y='220' text-anchor='middle' font-family='Arial' font-size='14'
        fill='#ffffff'>#YouthVotes #Democracy</text>
  <text x='150' y='248' text-anchor='middle' font-family='Arial' font-size='11'
        fill='#aaaaaa'>My voice. My vote. My future.</text>
</svg>"""

    def __init__(self):
        """Initialize voting model with vote tracking."""
        self.votes_cast: Dict[str, VoteRecord] = {}
        self.vote_counts: Dict[str, int] = {c: 0 for c in self.CANDIDATES}

    def is_valid_candidate(self, candidate: str) -> bool:
        """
        Check if a candidate is valid.
        
        Args:
            candidate: The candidate name to validate
            
        Returns:
            True if valid, False otherwise
        """
        return candidate in self.CANDIDATES

    def has_voted(self, voter_id: str) -> bool:
        """
        Check if a voter has already cast their vote.
        
        Args:
            voter_id: The voter's unique ID
            
        Returns:
            True if voter has voted, False otherwise
        """
        return voter_id in self.votes_cast

    def cast_vote(self, voter_id: str, candidate: str) -> VoteRecord:
        """
        Cast a vote for a candidate.
        
        Args:
            voter_id: The voter's unique ID
            candidate: The candidate to vote for
            
        Returns:
            VoteRecord object
            
        Raises:
            ValueError: If voter already voted or candidate is invalid
        """
        if self.has_voted(voter_id):
            raise ValueError(f"Voter {voter_id} has already voted")
        if not self.is_valid_candidate(candidate):
            raise ValueError(f"Invalid candidate: {candidate}")

        vote = VoteRecord(voter_id, candidate)
        self.votes_cast[voter_id] = vote
        self.vote_counts[candidate] = self.vote_counts.get(candidate, 0) + 1
        return vote

    def get_vote_info(self, voter_id: str) -> Optional[VoteRecord]:
        """
        Get voting information for a voter.
        
        Args:
            voter_id: The voter's unique ID
            
        Returns:
            VoteRecord object or None if not found
        """
        return self.votes_cast.get(voter_id)

    def get_vote_stats(self) -> Dict:
        """
        Get overall voting statistics.
        
        Returns:
            Dictionary with total votes, candidate breakdown, and percentages
        """
        total = sum(self.vote_counts.values())
        stats = []
        for candidate in self.CANDIDATES:
            count = self.vote_counts.get(candidate, 0)
            stats.append({
                "candidate": candidate,
                "votes": count,
                "percentage": round((count / total * 100), 2) if total > 0 else 0
            })
        return {
            "total_votes": total,
            "candidates": stats,
            "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

    def get_candidates(self) -> List[str]:
        """Get list of all valid candidates."""
        return self.CANDIDATES

    def generate_sticker(self, voter_id: str) -> Dict:
        """
        Generate a virtual "I Voted" sticker for sharing on social media.
        
        Args:
            voter_id: The voter's unique ID
            
        Returns:
            Dictionary with sticker data and social media info
            
        Raises:
            ValueError: If voter has not voted yet
        """
        vote_info = self.get_vote_info(voter_id)
        if not vote_info:
            raise ValueError("Voter ID not found. Please vote first.")

        return {
            "voter_id": voter_id,
            "candidate": vote_info.candidate,
            "voted_at": vote_info.timestamp,
            "sticker_title": "I Voted! 🗳️",
            "sticker_svg": self.STICKER_SVG_TEMPLATE.strip(),
            "share_caption": (
                "🗳️ I just VOTED and I'm proud of it! "
                "Your vote is your voice — use it! 💪 "
                "#IVoted #YouthVotes #Democracy #MakeYourVoiceHeard"
            ),
            "social_links": {
                "twitter": "https://twitter.com/intent/tweet?text=I+just+VOTED+%23IVoted+%23YouthVotes",
                "facebook": "https://www.facebook.com/sharer/sharer.php?u=&quote=I+just+VOTED+%23IVoted"
            }
        }
