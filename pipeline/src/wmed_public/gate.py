from __future__ import annotations

import hashlib
import json

from .models import Candidate, LifecycleState, PublicationDecision, Verification


def candidate_digest(candidate: Candidate) -> str:
    """Hash a canonical representation of the exact candidate under review."""
    payload = candidate.model_dump(mode="json")
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def publication_guard(
    candidate: Candidate,
    verification: Verification,
    current_state: LifecycleState,
) -> PublicationDecision:
    """Compute publication eligibility without trusting a model-authored allow flag."""
    reasons: list[str] = []

    if current_state is not LifecycleState.VERIFIED:
        reasons.append("topic is not in the verified lifecycle state")

    digest = candidate_digest(candidate)
    if verification.candidate_sha256 != digest:
        reasons.append("verification is not bound to the exact candidate")

    if verification.verdict != "pass":
        reasons.append(f"verifier verdict is {verification.verdict!r}, not 'pass'")

    if verification.critical_findings:
        reasons.append("critical findings remain")
    if verification.major_findings:
        reasons.append("major findings remain")

    if not verification.references_verified:
        reasons.append("references have not been verified")
    if not verification.numeric_claims_verified:
        reasons.append("numeric claims have not been verified")
    if not verification.evidence_currency_verified:
        reasons.append("evidence currency has not been verified")

    return PublicationDecision(allowed=not reasons, reasons=reasons)
