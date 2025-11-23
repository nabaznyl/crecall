# Security & Protection Protocols (crecall)

## Current Foundations
- Local encryption via AES-256-CBC (OpenSSL) for transcripts.
- Passphrase stored with restricted permissions.
- Git hook memory creation (non-sensitive).

## Immediate Enhancements (Planned)
1. Integrity Hashing: SHA-256 for release artifacts; publish `CHECKSUMS.txt`.
2. Signed Tags: GPG sign version tags (e.g., `v0.1.0d-2`).
3. Sensitive Pattern Scan: Pre-commit hook scanning (tokens, secrets, keys).
4. Dependency Audit: Weekly SCA (pip + npm) severity report.
5. Secure Config: Enforce `.env` file permission (600) and deny accidental commits.
6. Clip Sanitization: Strip env vars matching high-risk keys (AWS, DB, cloud tokens).
7. Memory Redaction API: Redact or delete sensitive memory entries by pattern.
8. Rate Limiting: Basic per-IP limits on future public API endpoints.
9. Transport Security: Enforce HTTPS (reverse proxy) for API when externalized.
10. User Preference Security: Theme & personalization isolated from sensitive operational state.

## Future Roadmap
- Field-Level Encryption: Encrypt sensitive memory segments individually.
- Tamper-Evident Ledger: Hash-chain for clips & high-importance memories.
- Role-Based Access Control: Multi-user permission layers (read/write/admin).
- Security Events Stream: Publish audit events (create/modify/delete ops). 
- Secret Vault Integration: Support retrieval of encryption key from Vault/KMS.

## Clip & Memory Sanitization Rules
| Target | Rule |
|--------|------|
| API keys | Replace with `***MASKED***` if entropy & pattern match |
| Private paths | Collapse to basename only if flagged private |
| Terminal secrets | Drop lines containing `export KEY=` or tokens |
| Large blobs | Truncate beyond 4KB with checksum marker |

## Recommended Tooling
- `trufflehog` / `gitleaks` for secret scanning.
- `pip-audit` / `npm audit` for dependency vulnerabilities.
- `bandit` for Python static security checks.

## Pre-Commit Example (Concept)
```bash
#!/usr/bin/env bash
SECRETS=$(gitleaks detect --no-git -s . || true)
if [ -n "$SECRETS" ]; then
  echo "[SECURITY] Potential secrets detected; aborting commit." >&2
  exit 1
fi
exit 0
```

## High-Level Architecture Security Layers
```
[Frontend] -- sanitized requests --> [API Layer] -- validation --> [DB]
               |                         |                |
        LocalStorage theme        Auth (future)       Encrypted fields
```

## Incident Response (Future)
1. Freeze new writes (maintenance flag).
2. Snapshot DB + logs.
3. Triage affected clips/memories.
4. Redact + restore service.
5. Publish post-incident summary memory tagged `security-incident`.

---
Lean baseline; expand iteratively without bloat.
