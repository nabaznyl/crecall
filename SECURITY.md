# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 0.1.x-dev | :white_check_mark: (Development) |

## Reporting a Vulnerability

**Please do NOT report security vulnerabilities through public GitHub issues.**

Instead, please report them via email to: [Your contact email here]

You should receive a response within 48 hours. If for some reason you do not, please follow up to ensure we received your original message.

Please include the following information:

- Type of issue (e.g. buffer overflow, SQL injection, cross-site scripting, etc.)
- Full paths of source file(s) related to the manifestation of the issue
- The location of the affected source code (tag/branch/commit or direct URL)
- Any special configuration required to reproduce the issue
- Step-by-step instructions to reproduce the issue
- Proof-of-concept or exploit code (if possible)
- Impact of the issue, including how an attacker might exploit it

## Security Best Practices

When using crecall:

1. **Environment Variables**: Never commit `.env` files with sensitive credentials
2. **Database**: Use strong passwords for PostgreSQL deployments
3. **Network**: Run behind a reverse proxy (nginx/caddy) with TLS in production
4. **Updates**: Keep dependencies up to date (run `pip install -U -r requirements.txt` regularly)
5. **Secrets**: Use environment-based secret management, never hardcode credentials

## Known Security Considerations

- **Integrity Verification**: Clip integrity verification on retrieval is not yet implemented (tracked in TODO.md)
- **Authentication**: No built-in authentication system (designed for single-user local deployment)
- **Rate Limiting**: Basic rate limiting implemented for admin endpoints only

## Security-Related Configuration

See [CONFIGURATION.md](CONFIGURATION.md) for security-related settings:
- `HMAC_SECRET_KEY`: Used for clip integrity signatures
- `DB_URL`: Database connection string (keep secure)
