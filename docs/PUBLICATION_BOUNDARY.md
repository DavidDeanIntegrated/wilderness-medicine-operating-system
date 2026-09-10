# Public / Private Publication Boundary

This file records the sanitization policy for the public review repository.

## Public by design

- clinician-facing project overview;
- conceptual architecture and safety principles;
- generic configuration examples containing no values;
- small reference implementations of deterministic safety mechanisms;
- synthetic examples and sanitized descriptions of production behavior;
- links to the already-public reference site.

## Review before publishing

- production source code copied from the private repository;
- model prompts containing internal annotations or operator names;
- configuration files that reveal infrastructure topology;
- production reports that include costs, host paths, deployment details, or operator decisions;
- generated medical reports if their metadata includes private provenance or non-redistributable material.

## Keep private

- `.env` and all credentials/tokens;
- browser profiles, cookies, saved sessions, authentication state;
- raw retrieved PDFs, journal/guideline text, and evidence caches unless redistribution rights are established;
- production run directories, drafts, verification payloads, quarantine records, and internal audit trails;
- VPS/host-specific paths, SSH/VNC details, cron wrappers, backup destinations, messaging integrations;
- private Git history containing personal email addresses or model-session URLs.

## History rule

The public repository begins with a new Git history. It is not a fork and does not preserve commit objects from the private repository. This prevents deleted historical metadata from becoming public later.
