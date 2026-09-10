# Architecture

## Design objective

The system is designed around a simple failure model: language models are useful for searching, extracting, synthesizing, drafting, and criticism, but none of those roles should be trusted to unilaterally change the publication state of medical content.

The production architecture therefore separates probabilistic model work from deterministic state transitions.

## Conceptual pipeline

```text
Topic contract
  → discovery
  → retrieval + provenance
  → structured evidence packet
  → draft candidate
  → fresh-context verification
  → deterministic publication guard
  → published corpus
```

### Topic contract

A topic starts with explicit scope: what clinical questions must be answered, what sections are required, and what the article should not claim. Coverage can therefore be checked rather than inferred from prose quality.

### Discovery and retrieval

Search results are candidates, not evidence. Retrieval determines what usable source text is actually available and records provenance. The private production corpus may distinguish full text, substantial text, abstract-only evidence, and failed retrievals.

### Structured research

The research stage converts the available corpus into structured clinical claims, quantitative claims, controversies, and gaps. This creates an inspectable layer between literature and prose.

### Drafting

The writer generates a candidate from the evidence packet and permitted corpus. Generation does not advance the topic to a published state.

### Verification

A separate verifier reviews the candidate in fresh context. It looks for citation mismatches, unsupported recommendations, numeric errors, missing qualifiers, and scope problems. Deterministic validators can independently check machine-verifiable invariants.

### Publication guard

The final guard is code. At minimum it can require:

1. the verification record is bound to the exact candidate digest;
2. the verifier returned an acceptable verdict;
3. no blocking findings remain;
4. required numeric/reference/evidence checks passed; and
5. the lifecycle transition is legal.

The reference implementation in `pipeline/src/wmed_public/gate.py` demonstrates this concept without exposing the production implementation.

## Why candidate binding matters

If verification applies to candidate A but publication silently publishes candidate B, the verification step is meaningless. The guard therefore hashes the canonical candidate payload and compares that digest with the digest recorded by verification.

## Why quarantine is a valid outcome

The pipeline is designed to stop safely. A run that discovers that the evidence is insufficient or that a draft contains major unsupported claims can finish in a quarantined or research-required state. That is a safety success, not merely an engineering failure.
