# Security

This repository is intentionally a sanitized public review edition.

Please do not commit credentials, authentication cookies, browser profiles, raw publisher downloads, private run logs, internal infrastructure paths, or personal contact information.

Before adding files from the private production repository, review `docs/PUBLICATION_BOUNDARY.md` and run a secret scan locally. If a credential is ever committed, treat it as compromised and rotate it; deleting the file in a later commit does not remove it from Git history.

For medical-content concerns, distinguish a software/security vulnerability from an evidence or clinical-content issue. Clinical material should retain provenance and independent review rather than being changed solely to make an automated check pass.
