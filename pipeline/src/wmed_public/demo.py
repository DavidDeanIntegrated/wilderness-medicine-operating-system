from __future__ import annotations

from .gate import candidate_digest, publication_guard
from .models import Candidate, LifecycleState, Verification


def main() -> None:
    candidate = Candidate(
        topic_id="avalanche-rescue-demo",
        title="Avalanche Rescue Demonstration",
        markdown="Synthetic educational content for a publication-gate demonstration.",
        source_ids=["guideline-a", "guideline-b"],
    )

    digest = candidate_digest(candidate)

    blocked = Verification(
        candidate_sha256=digest,
        verdict="pass_with_revisions",
        major_findings=2,
        references_verified=True,
        numeric_claims_verified=False,
        evidence_currency_verified=True,
    )
    blocked_decision = publication_guard(candidate, blocked, LifecycleState.DRAFTED)

    accepted = Verification(
        candidate_sha256=digest,
        verdict="pass",
        references_verified=True,
        numeric_claims_verified=True,
        evidence_currency_verified=True,
    )
    accepted_decision = publication_guard(candidate, accepted, LifecycleState.VERIFIED)

    print("First candidate decision:", "ALLOWED" if blocked_decision.allowed else "BLOCKED")
    for reason in blocked_decision.reasons:
        print(" -", reason)

    print("\nCorrected + verified candidate decision:", "ALLOWED" if accepted_decision.allowed else "BLOCKED")
    for reason in accepted_decision.reasons:
        print(" -", reason)


if __name__ == "__main__":
    main()
