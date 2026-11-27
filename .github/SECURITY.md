# Security Policy

## Supported versions

Security fixes are applied to the latest release and the current `main` branch. Older pre-release snapshots are not maintained unless a release note explicitly says otherwise.

## Reporting a vulnerability

Do **not** open a public issue with exploit details, credentials, private repository content, or personal data.

Use GitHub's **Report a vulnerability** flow for this repository when it is available. If private vulnerability reporting is unavailable, open a minimal public issue asking the maintainer to establish a private contact channel; do not include technical details until that channel exists.

Include the affected version or commit, impact, reproduction conditions, and a minimal proof of concept that contains no real secrets or third-party data.

## Secret handling

Reporivet does not generate or modify `.gitignore`. A project's existing ignore rules are not a security boundary and do not protect content that was already tracked. If a credential, private key, token, or sensitive data file is committed, revoke or rotate it immediately and then remove it from Git history where appropriate.
