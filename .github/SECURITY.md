# Security Policy

## Reporting a Vulnerability

**Please do NOT report security vulnerabilities through public GitHub issues.**

If you discover a security vulnerability in MOVR DataHub Analytics, please report it privately by emailing **both**:

- **adparedes@proton.me**
- **mdamovr@mdausa.org**

Please include the following information in your report:

- Description of the vulnerability
- Steps to reproduce the issue
- Potential impact
- Any suggested fixes (optional)

You should receive a response within **72 hours** acknowledging receipt. We will work with you to understand and resolve the issue promptly.

---

## Supported Versions

| Version | Supported          |
|---------|--------------------|
| 0.1.x   | :white_check_mark: |

---

## Security Considerations for Clinical Data

### PHI (Protected Health Information)

This software is designed to work with **de-identified clinical data**.

**Important guidelines:**

1. **Never commit PHI to this repository** - The `.gitignore` is configured to block common PHI file patterns, but you are responsible for ensuring no PHI is committed.

2. **Use `_noPHI` files** - The setup wizard automatically prefers files with `_noPHI` suffix and skips files with `_PHI` suffix.

3. **Audit your data** - Before sharing any outputs, verify they do not contain identifiable information.

4. **Local processing only** - This tool processes data locally. No data is transmitted to external servers.

### Data Handling Best Practices

- Keep source Excel files in a separate directory (`source-movr-data/`) that is not part of the git repository
- Never edit original source files - treat them as read-only
- Review generated outputs before sharing
- Use the audit logging feature to track data transformations

---

## Security Features

### Built-in Protections

- **PHI file auto-skip**: Files containing `_PHI` in the name are automatically excluded from processing
- **Audit logging**: All data conversions are logged to `data/.audit/` for traceability
- **No network calls**: Core functionality operates entirely offline
- **Gitignore patterns**: Comprehensive patterns to prevent accidental commits of sensitive files

### Recommended Practices

1. **Environment isolation**: Use virtual environments to isolate dependencies
2. **Dependency updates**: Regularly update dependencies to patch known vulnerabilities
3. **Access control**: Limit access to source data directories
4. **Backup**: Maintain backups of source data separately from this repository

---

## Dependency Security

We recommend periodically auditing dependencies for vulnerabilities:

```bash
# Install pip-audit
pip install pip-audit

# Run security audit
pip-audit
```

Report any vulnerable dependencies as a security issue.

---

## Disclosure Policy

- Security issues will be addressed in the next patch release
- Critical vulnerabilities will receive expedited fixes
- Security advisories will be published via GitHub Security Advisories
- Credit will be given to reporters (unless anonymity is requested)

---

## Contact

- **Security issues**: adparedes@proton.me and mdamovr@mdausa.org
- **General questions**: [GitHub Discussions](https://github.com/openmovr/movr-datahub-analytics/discussions)
- **Bug reports**: [GitHub Issues](https://github.com/openmovr/movr-datahub-analytics/issues)

---

**Thank you for helping keep MOVR DataHub Analytics secure.**
