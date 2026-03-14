"""Governance Protocol - 治理协议"""

from .protocol import GovernanceProtocol, Proposal, Vote

__all__ = ["GovernanceProtocol", "Proposal", "Vote"]


class Proposal:
    """提案"""
    def __init__(self, id, title, description, proposer):
        self.id = id
        self.title = title
        self.description = description
        self.proposer = proposer
        self.votes = {}
        self.status = "pending"


class Vote:
    """投票"""
    def __init__(self, voter, proposal_id, decision):
        self.voter = voter
        self.proposal_id = proposal_id
        self.decision = decision  # approve, reject, abstain


class GovernanceProtocol:
    """治理协议"""

    def __init__(self):
        self._proposals = {}
        self._approval_threshold = 0.5

    async def create_proposal(self, title, description, proposer):
        """创建提案"""
        proposal_id = f"PROP_{len(self._proposals) + 1}"
        proposal = Proposal(proposal_id, title, description, proposer)
        self._proposals[proposal_id] = proposal
        return proposal

    async def vote(self, proposal_id, voter, decision):
        """投票"""
        if proposal_id in self._proposals:
            self._proposals[proposal_id].votes[voter] = decision

    async def execute_proposal(self, proposal_id):
        """执行提案"""
        proposal = self._proposals.get(proposal_id)
        if not proposal:
            return False

        # 计算投票结果
        approve_count = sum(1 for v in proposal.votes.values() if v == "approve")
        total_votes = len(proposal.votes)

        if total_votes > 0 and approve_count / total_votes >= self._approval_threshold:
            proposal.status = "approved"
            return True

        proposal.status = "rejected"
        return False
