from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, Field


class LifecycleState(StrEnum):
    DRAFTED = "drafted"
    VERIFIED = "verified"
    QUARANTINED = "quarantined"
    PUBLISHED = "published"


class Candidate(BaseModel):
    topic_id: str
    title: str
    markdown: str
    source_ids: list[str] = Field(default_factory=list)


class Verification(BaseModel):
    candidate_sha256: str
    verdict: str
    critical_findings: int = 0
    major_findings: int = 0
    minor_findings: int = 0
    references_verified: bool = False
    numeric_claims_verified: bool = False
    evidence_currency_verified: bool = False


class PublicationDecision(BaseModel):
    allowed: bool
    reasons: list[str] = Field(default_factory=list)
