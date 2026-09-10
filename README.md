# Wilderness Medicine Knowledge OS

Wilderness Medicine Knowledge OS is a physician-facing, evidence-based publishing system for wilderness medicine education.

Its job is not simply to ask an AI model to write an article. The project separates **source retrieval**, **evidence extraction**, **medical writing**, **independent verification**, and **publication control** so that a generated chapter cannot reach the reference site just because a language model says it is correct.

**Core rule:** AI can propose knowledge. Deterministic software controls state and publication.

Live reference site: https://wilderness-med-os.vercel.app

Public review repository: https://github.com/DavidDeanIntegrated/wilderness-medicine-operating-system

> **Public Review Edition**
>
> This repository preserves the clinician-facing explanation, architecture, and representative production outputs of the working system. It is intentionally not a byte-for-byte production mirror. Raw source corpora, private infrastructure, credentials, production logs, browser sessions, internal audit artifacts, and private Git history are excluded. The production CLI examples below are shown so reviewers can understand exactly how an article moves through the system; the public repository includes a small runnable reference implementation of the deterministic publication gate.

---

## What this project is trying to do

A traditional review article often involves one person searching the literature, deciding what matters, drafting the article, checking citations, and editing the final version. This project breaks those jobs apart and makes each step inspectable.

A topic begins with a defined clinical scope. The system then searches for evidence, stores the source material locally, turns that evidence into a structured packet of claims, writes a draft from that packet, and sends the draft through an independent verification step. Only after the software publication gate is satisfied can the article move into the published corpus.

For an Emergency Medicine attending, the easiest mental model is:

```text
Clinical topic
    ↓
Define what the article must answer
    ↓
Search and retrieve source literature
    ↓
Build a structured evidence packet
    ↓
Write the chapter from that packet
    ↓
Independent adversarial verification
    ↓
Deterministic publication gate
    ↓
Published reference article
```

The important point is that the **writer is not the final authority**. A draft can be rejected, revised, sent back for more research, or quarantined instead of published.

---

## Who does what?

| Stage | What happens | Primary control |
|---|---|---|
| Topic / contract | Defines the clinical questions, required sections, and scope boundaries | Human-authored curriculum + deterministic validation |
| Discovery | Searches PubMed and configured web-search providers for relevant evidence | Software |
| Retrieval | Downloads and stores source text with provenance | Software |
| Research | Converts the local corpus into structured clinical claims, numeric claims, controversies, and gaps | Research model, constrained by the stored evidence |
| Drafting | Writes the educational chapter using the evidence packet and local corpus | Writer model |
| Verification | A separate fresh-context verifier looks for unsupported claims, citation problems, numeric errors, missing qualifiers, and recommendation problems | Verifier model + deterministic checks |
| Publication gate | Recomputes whether the exact candidate is allowed to publish | Deterministic software |
| Publication | Writes the accepted chapter into the durable corpus and advances topic state | Deterministic software |

The system intentionally gives different jobs to different components. A language model can suggest content, but it cannot directly mark its own article as published.

---

## A real example: the avalanche article

The `avalanche-rescue` chapter is a useful example of why the pipeline is built this way.

The evidence corpus included the current Wilderness Medical Society avalanche guideline, ICAR MedCom recommendations, ERC guidance, and supporting studies. The research stage converted those sources into structured clinical and numeric claims before the writer ever produced prose.

The first verifier did **not** approve the article. It found three major problems in the clinical summary, so publication remained blocked. After correction, a second verification still found two major issues and the topic was quarantined. The article was corrected again and re-verified. Only the third verification returned a clean pass with no critical, major, or minor findings and `publication_allowed: true`.

That is the intended behavior: the system should be willing to stop an article that sounds polished but is not yet sufficiently supported.

A sanitized summary of that verification sequence is included in:

`examples/avalanche-verification.md`

The full internal production record is intentionally not distributed in the public repository.

---

# Getting this public review repository running

## 1. Clone the repository

```bash
git clone https://github.com/DavidDeanIntegrated/wilderness-medicine-operating-system.git
cd wilderness-medicine-operating-system
```

## 2. Create an isolated Python environment

The public reference implementation requires Python 3.12 or newer.

```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e "./pipeline[dev]"
```

## 3. Run the public safety-gate demonstration

```bash
pytest pipeline/tests
wmed-public-demo
```

The demo creates one rejected candidate and one accepted candidate. It demonstrates the central publication invariant: the decision to publish is recomputed by deterministic code and is bound to the exact candidate that was verified.

The full production system contains additional retrieval, research, drafting, verification, orchestration, audit, site-generation, and deployment code. Those components are documented below so clinicians and technical reviewers can inspect how the working production system behaves, but they are not all distributed in this sanitized repository.

---

# How an article is produced

The production orchestrator can run the workflow automatically, but it is easier to understand the mechanics by looking at the stages separately.

Assume we are working on a topic called `avalanche-rescue`.

The output examples below are **abridged and representative**. Production runs save much more detailed machine-readable records, and exact CLI formatting can change as the software evolves. The `wmed` commands shown in this section describe the full production system; they are included here for transparency rather than as a claim that every production component is distributed in the public review repository.

## Step 1 - inspect the topic

```bash
wmed topics show avalanche-rescue
```

This shows the topic definition, its current lifecycle state, and any prerequisite topics.

Example output (abridged):

```text
{
  "definition": {
    "topic_id": "avalanche-rescue",
    "title": "Avalanche Burial, Rescue, and Resuscitation",
    "domain": "avalanche"
  },
  "state": {
    "status": "pending"
  },
  "unmet_prerequisites": []
}
```

Clinically, this means the article has a known scope and is eligible to begin work; it is not yet a draft or a published chapter.

## Step 2 - preview the literature search

```bash
wmed discover avalanche-rescue --dry-run
```

Dry-run mode shows the planned PubMed and web-search queries without spending API money or changing state.

Example output (abridged):

```text
query plan for avalanche-rescue (no calls made):
  pubmed (unmetered):
    - avalanche burial rescue resuscitation guideline
    - avalanche victim hypothermia extracorporeal life support
  web search:
    - Wilderness Medical Society avalanche guideline
    - ICAR avalanche recommendations
    - ERC special circumstances avalanche resuscitation
  estimated cost: ~$0.015
```

When the plan looks appropriate:

```bash
wmed discover avalanche-rescue
```

Discovery finds candidate sources; it does not yet treat them as accepted evidence.

A completed discovery run might summarize itself like this:

```text
discovery complete: avalanche-rescue
  candidate sources found: 18
  duplicates / already-known sources removed: 4
  candidates remaining for retrieval: 14
  saved: runs/.../discovery.json
```

The important distinction is that **search results are candidates, not evidence**. A title appearing in PubMed or web search does not automatically become a source the writer can rely on.

## Step 3 - retrieve the source material

```bash
wmed retrieve avalanche-rescue
```

The retrieval layer attempts to obtain usable source text and stores provenance, identifiers, and content locally. This creates the evidence corpus that later model calls are allowed to use.

For the real avalanche production run, the resulting corpus was summarized as:

```text
retrieval complete: avalanche-rescue
  sources in corpus: 14
  full text: 10
  substantial text: 1
  abstract only: 3
  omitted: 0
  truncated: 0
```

A source can therefore exist in the corpus at different levels of completeness. The pipeline keeps track of that distinction rather than treating an abstract and a full guideline as equivalent.

## Step 4 - turn sources into structured evidence

```bash
wmed research avalanche-rescue --dry-run
wmed research avalanche-rescue
```

The research model does **not** primarily write the article. Its job is to create a structured evidence packet: clinical claims, quantitative claims, controversies, and knowledge gaps tied back to source material.

Conceptually, a simplified claim might look like:

```text
Claim: Prolonged burial with an obstructed airway is associated with poor survival.
Evidence: ICAR 2023 + WMS 2024
Type: prognosis / resuscitation
Numeric dependency: burial-duration thresholds stored separately and verified
```

The actual packet is machine-readable and contains much more provenance than this simplified example.

The avalanche research call produced output conceptually like:

```text
research complete: avalanche-rescue
  clinical claims: 35
  numeric claims: 74
  controversies: 8
  knowledge gaps: 13
  model validation retry: 1
  stage cost: $1.8561
```

After deterministic normalization and evidence-bound corrections, the packet that ultimately went to publication contained:

```text
evidence packet ready
  clinical claims: 58
  numeric claims: 83
  contract coverage: 11 / 11 requirements
  blocking evidence problems: 0
```

This packet is the bridge between the literature and the prose. It allows later stages to ask not only "does this paragraph sound medically reasonable?" but also "which stored evidence supports this exact recommendation or number?"

## Step 5 - draft the article

```bash
wmed draft avalanche-rescue
```

The writer receives the evidence packet and the local evidence corpus. It is expected to cite stored sources using repository source identifiers rather than inventing references.

A simplified sentence in the draft may look like:

```markdown
Resuscitation decisions after avalanche burial depend on airway status,
burial duration, core temperature, serum potassium, and the broader clinical
context described in current rescue algorithms. [@icar-avalanche-2023]
```

The citation marker points back to a source already known to the system.

A successful drafting stage may end with a summary like:

```text
draft candidate: avalanche-rescue
  writer generations used: 2
  required sections present: yes
  citations resolve to stored sources: yes
  contract coverage: 11 / 11
  numeric blocking findings: 0
  candidate saved for verification
```

Not every generated draft is adopted. In the avalanche run, the writer's candidate needed correction to its structured clinical summary before it could advance. That is expected behavior: generation and acceptance are separate steps.

## Step 6 - independently verify the draft

```bash
wmed verify avalanche-rescue
```

The verifier is deliberately separate from the writer. It reviews the candidate against the evidence packet and corpus rather than simply proofreading the prose.

Among other things, the pipeline checks whether:

- cited sources actually support the statements attached to them;
- medication doses, temperatures, durations, altitudes, pressures, thresholds, and other quantitative claims are evidence-bound;
- recommendations have adequate support and appropriate qualifiers;
- references resolve to real stored sources;
- the article remains within the topic's defined clinical scope; and
- the exact candidate being considered for publication is the one that was verified.

A failed verification does not become a published article. Depending on the findings, the workflow can revise the draft, return to research, or quarantine the topic.

The avalanche article is particularly useful because its terminal-level results show all three possibilities: correction, quarantine, and eventual approval.

First verification:

```text
verification: avalanche-rescue
  verdict: pass_with_revisions
  critical findings: 0
  major findings: 3
  minor findings: 0
  references verified: true
  publication_allowed: false

RESULT: publication blocked - correction required
```

Second verification after correction:

```text
verification: avalanche-rescue
  verdict: research_required
  critical findings: 0
  major findings: 2
  minor findings: 0
  publication_allowed: false

STATE: quarantined
RESULT: article cannot publish
```

Third verification after the remaining problems were corrected and a new verification was explicitly run:

```text
verification: avalanche-rescue
  verdict: pass
  critical findings: 0
  major findings: 0
  minor findings: 0
  numeric claims verified: true
  references verified: true
  evidence currency verified: true
  publication_allowed: true

STATE: verified
```

This is the central safety feature of the system. A polished draft is not enough. The exact article candidate must survive an independent evidence-based review before the software will even consider publication.

## Step 7 - ask the publication gate what it would do

```bash
wmed publish avalanche-rescue --dry-run
```

This is an important distinction: publication permission is recomputed by code. The writer or verifier cannot simply set a flag that bypasses the gate.

Example dry-run output:

```text
publication guard: ALLOWED
  topic: avalanche-rescue
  basis: verifier_direct
  candidate matches verified candidate: yes
  verification record bound to candidate: yes
  blocking findings: 0

DRY RUN - nothing published
```

If the gate is satisfied:

```bash
wmed publish avalanche-rescue
```

The accepted chapter is written to the durable report corpus, the lifecycle state is advanced, and the publication record is preserved.

A successful publication looks conceptually like:

```text
publication guard: ALLOWED
publishing avalanche-rescue...
  report: knowledge/reports/avalanche-rescue.md
  state: verified -> published
  changelog: written
  publication manifest: written
  git commit: created

PUBLISHED: Avalanche Burial, Rescue, and Resuscitation
```

Once the commit is pushed and the static site builds successfully, the deployment check can report:

```text
site build: passed
deployment: READY
live chapter:
  /topics/avalanche-rescue/
```

At that point the article has crossed a very different threshold from "the AI generated a draft." It has a stored evidence corpus, structured claim packet, verification history, publication decision, lifecycle state, and version-controlled published artifact.

---

## The normal automated path

The same stages can be orchestrated by the pipeline instead of being called manually.

A zero-spend test of the scheduled workflow is:

```bash
wmed run-next --test --topic avalanche-rescue
```

A real topic run can then be started with:

```bash
wmed run-next --topic avalanche-rescue
```

`run-next` handles the stage ordering, budget checks, verification/revision logic, publication path, and deployment checks. The individual commands above are still useful because they show what the orchestrator is doing under the hood.

A successful automated run might look like this from the operator's point of view:

```text
selected topic: avalanche-rescue
budget check: continue

[1/7] discovery ........ complete
[2/7] retrieval ........ complete
[3/7] research ......... evidence packet ready
[4/7] drafting ......... candidate created
[5/7] verification ..... pass
[6/7] publication ...... allowed / published
[7/7] deployment ....... READY

final state: published
```

In a more complicated case, the same summary may instead stop at:

```text
[5/7] verification ..... research_required
final state: quarantined
publication: NOT attempted
```

That is a successful safety outcome, not a failed software run.

Real production topics can include additional steps such as evidence annotation, packet normalization, clinical-summary validation, gap closure, adjudication, revision, or quarantine recovery. Those details are intentionally not required to understand the basic architecture.

---

# Production system architecture

The full production system is organized approximately as follows. These directories explain the architecture; most are intentionally not included in this public review repository.

```text
curriculum/             Human-authored topics, domains, contracts, and source registry
state/                  Machine-owned lifecycle state
knowledge/evidence/     Retrieved source material and evidence records
knowledge/drafts/       Draft article candidates
knowledge/verification/ Verification records
knowledge/reports/      Articles that passed the publication pathway
knowledge/quarantine/   Work that was explicitly stopped from publication
pipeline/               Python package and deterministic CLI
config/                 Model routing, budgets, evidence policy, and pricing
runs/                   Per-run logs, manifests, costs, and audit records
site/                   Astro static reference site
docs/                   Design decisions, run reports, and operations documentation
```

The durable medical corpus is Markdown/YAML rather than an opaque database. That makes changes version-controlled and reviewable with ordinary Git history.

## What is included in this public repository

```text
docs/                    Public architecture and publication-boundary documentation
examples/                Sanitized production verification example
pipeline/                 Runnable reference implementation of the deterministic gate
README.md                 Clinician-facing system explanation
SECURITY.md               Security and disclosure guidance
NOTICE.md                 Public-review and licensing note
```

---

# Safety and governance principles

This project contains medical educational material, so several rules are intentionally stricter than they would be in a generic AI writing project.

The publication system must never be weakened to make an article pass. Numeric clinical claims require explicit evidence. DOI and PMID identifiers must resolve to real publications. Drafts and quarantined material do not render as published chapters. State transitions occur through the pipeline rather than by manually editing a status field. Publication writes are designed to be atomic so a failed publication does not leave the corpus half-updated.

Most importantly, **no article is published solely because an LLM says that it is accurate**.

The public repository demonstrates the publication-boundary logic without distributing private operational details or raw source material.

---

# Reference site

The educational website is a static reference site generated from accepted content in the production report corpus.

Live reference site: https://wilderness-med-os.vercel.app

The site adds navigation, search, references, status information, and print-friendly presentation, but it does not decide whether an article is medically acceptable. The publication pipeline makes that decision before the article reaches the site.

Site-generation and deployment infrastructure remain in the private production system and are not required to review the public architecture.

---

# Useful deeper documentation in this public edition

For readers who want more detail after understanding the basic workflow:

- `docs/ARCHITECTURE.md` - separation of probabilistic model roles from deterministic state transitions
- `docs/PUBLICATION_BOUNDARY.md` - what is deliberately public versus private
- `examples/avalanche-verification.md` - sanitized real production verification sequence
- `SECURITY.md` - security and disclosure guidance
- `pipeline/` - runnable reference implementation of the publication gate

The README is intentionally the high-level explanation. The public repository exposes enough of the architecture and safety mechanism for review while keeping private evidence corpora, operational infrastructure, and audit artifacts out of public Git history.

---

## Medical-use note

This project is an educational reference and software/research project. Generated or published content should not be treated as a substitute for local protocols, specialist consultation, or clinician judgment at the point of care.
