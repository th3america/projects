# Security and permission model

- Default operation is read-only (`scan`, `plan`).
- System changes require explicit interactive approval.
- Never put SSH private keys, Cloudmind credentials, browser cookies, API keys or corporate passwords in GitHub or public exports.
- Use SSH keys and a dedicated non-root admin account. Do not expose Ollama's unauthenticated local API publicly.
- Bind local inference to loopback unless a separately reviewed private-network design requires otherwise.
- Keep corporate UI sessions in user-managed browser profiles. Do not bypass MFA/CAPTCHA or provider controls.
- Treat model output and downloaded content as untrusted input. Tool execution must pass policy checks and be logged.
- Keep authoritative Mindvault immutable; operate on a verified local copy with provenance.
- Require a second confirmation for destructive operations, publishing, purchases, account changes and deletion.
