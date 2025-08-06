# Security Policy

Tracy is an OSINT tool that can surface sensitive information. Please handle all findings responsibly and report any security concerns privately.

## Supported Versions

We aim to keep the default branch secure. Report issues against the latest commit on the default branch.

## Reporting a Vulnerability

Please do NOT open public issues for security vulnerabilities.

1. Prepare your report:
   - Affected component/file(s)
   - Description of the issue and impact
   - Steps to reproduce (PoC if applicable)
   - Suggested remediation (if known)
   - Your environment details (OS, Python version), commit hash
   - Any logs or stack traces (sanitize sensitive data)

2. Send it privately:
   - Preferred: use the repository’s security advisory feature (if enabled)
   - Otherwise: email the maintainer listed in repository metadata or README

We will acknowledge receipt within 5 working days and aim to provide a remediation plan and/or patch timeline as soon as possible, depending on severity and scope.

## Scope

- Vulnerabilities in Tracy’s codebase (e.g., input handling, report generation, dashboard UI, network operations)
- Supply-chain concerns in Tracy’s dependency usage (e.g., unsafe defaults, unpinned critical deps)
- Insecure defaults that could result in data leakage or abuse

Out of scope:
- Vulnerabilities in third-party services or websites queried by Tracy
- Abuse of APIs belonging to other platforms
- Misuse of Tracy against unauthorized targets (see Responsible Use)

## Coordinated Disclosure

We follow a responsible disclosure model:
- You report privately.
- We validate, prioritize, and work on a fix.
- We may publish a security advisory and credits once a patch is available and users have reasonable time to upgrade.

## Hardening and Best Practices

- Prefer running in an isolated virtual environment.
- Keep dependencies up to date (see requirements.txt).
- Avoid storing secrets in code; use .env and restrict access.
- Limit enabled integrations to those you need (see ENABLE_* flags).
- Respect rate limits; avoid aggressive automation patterns.
- Secure artifacts in results/ as they may contain sensitive data.

## Responsible Use

Tracy is intended for authorized security research and educational purposes only. Always obtain proper consent before investigating a target. Comply with applicable laws and service terms. Handle sensitive data with care.
