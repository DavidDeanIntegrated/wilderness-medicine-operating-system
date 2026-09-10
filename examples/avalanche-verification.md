# Production behavior example: avalanche article

This is a sanitized summary of a real production workflow. It contains no raw source corpus, model-session links, machine paths, or private run identifiers.

The `avalanche-rescue` chapter illustrates why the pipeline separates generation from publication.

The research stage assembled a structured packet from current avalanche authorities and supporting studies. The writer then produced a candidate. The first independent verification did **not** approve publication: it found three major problems, so the publication guard remained closed.

After correction, a second verification still found two major issues and required additional work. The topic was quarantined rather than published.

A later corrected candidate was explicitly re-verified. The third verification returned a clean pass with no critical, major, or minor findings and the deterministic guard confirmed that the verified candidate was the exact candidate being considered for publication.

```text
candidate 1
  verifier: pass_with_revisions
  major findings: 3
  publication: blocked

candidate 2
  verifier: research_required
  major findings: 2
  state: quarantined
  publication: blocked

candidate 3
  verifier: pass
  blocking findings: 0
  candidate digest: matched
  publication guard: allowed
```

The lesson is not that automated verification is infallible. It is that the system is structurally willing to refuse polished model output and requires an auditable transition before publication.
