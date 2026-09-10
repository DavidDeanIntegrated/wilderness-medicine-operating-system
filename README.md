# Wilderness Medicine Operating System — Public Review Edition

Wilderness Medicine Knowledge OS is a physician-facing, evidence-based publishing system for wilderness medicine education.

This repository is a **sanitized public review edition**. It is designed to show clinicians and technical reviewers how the system is structured without exposing private infrastructure, credentials, raw licensed source material, browser sessions, production logs, or historical metadata from the private development repository.

**Core rule:** AI can propose knowledge. Deterministic software controls state and publication.

Live reference site: https://wilderness-med-os.vercel.app

## What the system does

A topic begins with a defined clinical scope. The production system searches for evidence, retrieves source material with provenance, turns that evidence into structured claims, writes a draft, independently verifies the draft, and only then asks deterministic software whether the exact verified candidate is eligible for publication.

```text
Clinical topic
    ↓
Define required clinical scope
    ↓
Search and retrieve evidence
    ↓
Build a structured evidence packet
    ↓
Generate a draft
    ↓
Independent adversarial verification
    ↓
Deterministic publication gate
    ↓
Published reference article
```

The writer is deliberately **not** the final authority. A polished article can still be revised, sent back for additional research, quarantined, or blocked from publication.

## Separation of responsibilities

| Stage | Purpose | Primary control |
|---|---|---|
| Topic contract | Defines questions, required sections, and scope | Human-authored curriculum + deterministic validation |
| Discovery | Finds candidate literature | Software/search providers |
| Retrieval | Stores usable source material and provenance | Software |
| Research | Converts evidence into structured clinical and numeric claims | Research model constrained by retrieved evidence |
| Drafting | Writes educational prose from the evidence packet | Writer model |
| Verification | Searches for unsupported claims, numeric errors, citation problems, missing qualifiers, and unsafe recommendations | Separate verifier + deterministic checks |
| Publication gate | Recomputes whether the exact candidate may publish | Deterministic software |
| Publication | Advances accepted content into the durable corpus | Deterministic software |

## Why the gate matters

The public reference implementation in `pipeline/` demonstrates the core invariant: a verification record must be bound to the exact candidate being published, blocking findings must be zero, and required evidence checks must pass. A model cannot publish merely by returning a field that says `publication_allowed: true`.

A real production example is summarized in `examples/avalanche-verification.md`: an avalanche chapter was blocked twice before a later candidate passed verification.

## What is intentionally not in this repository

This public edition does **not** contain:

- API keys, `.env` files, credentials, or tokens;
- the private repository's Git history;
- raw retrieved journal/guideline text or publisher PDFs;
- `knowledge/evidence/`, retrieval caches, or browser profiles;
- production `runs/`, drafts, quarantine records, or internal audit artifacts;
- VPS paths, cron wrappers, SSH/VNC details, backup configuration, or messaging integrations;
- Claude session URLs or private model-session identifiers; or
- personal email addresses.

See `docs/PUBLICATION_BOUNDARY.md` for the public/private boundary used to create this edition.

## Clone this public review repository

```bash
git clone https://github.com/DavidDeanIntegrated/wilderness-medicine-operating-system.git
cd wilderness-medicine-operating-system
```

## Run the public gate demonstration

Requires Python 3.12+.

```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -e "./pipeline[dev]"
pytest pipeline/tests
wmed-public-demo
```

The demo creates one rejected candidate and one accepted candidate and shows that the publication decision is computed by code.

## Repository layout

```text
docs/                    Architecture and public/private boundary
examples/                Sanitized production example
pipeline/                 Small public reference implementation of the publication gate
README.md                 Clinician-facing overview
SECURITY.md               Security and disclosure guidance
NOTICE.md                 Public-review status and licensing note
```

## Relationship to the production system

This is **not a byte-for-byte mirror** of the private production repository. The production system contains substantially more retrieval, evidence-normalization, model-routing, validation, revision, audit, site-generation, and deployment code. This edition intentionally exposes the architecture and a representative deterministic safety mechanism while keeping private operational material and source corpora out of public Git history.

## Medical-use note

The project is an educational reference and software/research project. Generated or published content should not be treated as a substitute for local protocols, specialist consultation, or clinician judgment at the point of care.
