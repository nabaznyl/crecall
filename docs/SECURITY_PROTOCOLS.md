# Security & Protection Protocols (crecall)

## Current Foundations
- Local encryption via AES-256-CBC (OpenSSL) for transcripts.
- Passphrase stored with restricted permissions.
- Git hook memory creation (non-sensitive).

## Immediate Enhancements (Current / Planned)
1. Artifact Signing: Keyless Sigstore cosign signing for container images & release artifacts (wheel, sdist, SBOMs).
2. Integrity Hashing: SHA-256 checksums (future addition alongside signatures).
3. Signed Tags: GPG or keyless attestations for version tags (future).
4. Sensitive Pattern Scan: Pre-commit + CI secret scanning (gitleaks active).
5. Dependency Audit: Continuous SCA (pip-audit strict + safety report) in CI.
6. Secure Config: Enforce `.env` permissions (600) and exclude from VCS.
7. Clip Sanitization: Strip env vars matching high-risk keys (AWS, DB, cloud tokens).
8. Memory Redaction API: Redact or delete sensitive memory entries by pattern.
9. Rate Limiting: Basic per-IP limits on future public API endpoints.
10. Transport Security: Enforce HTTPS (reverse proxy) for API when externalized.
11. User Preference Security: Theme & personalization isolated from sensitive operational state.

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
- `cosign` for signing container images & release artifacts (keyless via GitHub OIDC).

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
Lean baseline; expand iteratively without bloat. Artifact signing provides provenance & tamper detection for distributed artifacts.

### Verification Examples

Container image (stable branch build):
```bash
cosign verify ghcr.io/nabaznyl/crecall:<git-sha>
```

Release artifact (wheel):
```bash
cosign verify-blob \
  --certificate backend/dist/<artifact>.whl.cert \
  --signature backend/dist/<artifact>.whl.sig \
  backend/dist/<artifact>.whl
```

Expected output includes `Verified OK` and issuer `https://token.actions.githubusercontent.com`.
