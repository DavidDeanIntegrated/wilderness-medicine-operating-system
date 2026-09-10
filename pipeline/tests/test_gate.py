from wmed_public.gate import candidate_digest, publication_guard
from wmed_public.models import Candidate, LifecycleState, Verification


def make_candidate() -> Candidate:
    return Candidate(topic_id="demo", title="Demo", markdown="content", source_ids=["s1"])


def passing_verification(candidate: Candidate) -> Verification:
    return Verification(
        candidate_sha256=candidate_digest(candidate),
        verdict="pass",
        references_verified=True,
        numeric_claims_verified=True,
        evidence_currency_verified=True,
    )


def test_verified_candidate_can_publish():
    candidate = make_candidate()
    decision = publication_guard(candidate, passing_verification(candidate), LifecycleState.VERIFIED)
    assert decision.allowed
    assert decision.reasons == []


def test_changed_candidate_is_blocked():
    candidate = make_candidate()
    verification = passing_verification(candidate)
    candidate.markdown = "changed after verification"
    decision = publication_guard(candidate, verification, LifecycleState.VERIFIED)
    assert not decision.allowed
    assert "exact candidate" in " ".join(decision.reasons)


def test_major_finding_blocks_publication():
    candidate = make_candidate()
    verification = passing_verification(candidate)
    verification.major_findings = 1
    decision = publication_guard(candidate, verification, LifecycleState.VERIFIED)
    assert not decision.allowed


def test_wrong_state_blocks_publication():
    candidate = make_candidate()
    decision = publication_guard(candidate, passing_verification(candidate), LifecycleState.DRAFTED)
    assert not decision.allowed
