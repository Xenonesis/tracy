# Contributing to Tracy

Thanks for your interest in contributing! This document outlines how to propose changes, report bugs, request features, and submit pull requests.

## Code of Conduct

By participating, you agree to uphold our standards of respectful and inclusive collaboration. See CODE_OF_CONDUCT.md.

## Getting Started

1) Fork the repository and create a feature branch
```
git checkout -b feat/your-feature
```

2) Create a virtual environment and install dependencies
```
python -m venv .venv
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # macOS/Linux
pip install --upgrade pip
pip install -r requirements.txt
```

3) Create a local .env
```
cp .env.example .env
# add any API keys for integrations you intend to test
```

4) Run basic checks
- Lint/style (if applicable in your setup)
- Run the CLI
```
python tracy.py --email example@example.com --report html
```

- Optionally run the dashboard:
```
python -c "from modules.dashboard import InteractiveDashboard; app = InteractiveDashboard(); app.run()"
```

## Project Structure

- tracy.py — entrypoint/orchestrator
- modules/
  - social_media.py, breach_checker.py, search_engines.py, phone_intel.py, util_dns_whois.py
  - data_correlator.py, report_generator.py, dashboard.py
- config.py, requirements.txt, .env.example
- results/ — generated artifacts

## Development Guidelines

- Keep modules async where possible (aiohttp + asyncio).
- Respect third‑party Terms of Service; avoid scraping that violates ToS.
- Feature flags should default to safe behavior and degrade gracefully without API keys.
- Log warnings instead of failing when optional deps are missing (e.g., sherlock, socialscan).
- Add docstrings and type hints for new functions/classes.
- Ensure new features are documented in README and/or relevant .md docs.

## Pull Request Process

1. Open an issue first for larger changes to get alignment.
2. Write clear commit messages following Conventional Commits where possible:
   - feat:, fix:, docs:, refactor:, chore:, test:
3. Add tests/examples if applicable (even as usage snippets).
4. Update documentation for any user-facing changes.
5. Ensure PRs remain focused; small, incremental changes are easier to review.

## Reporting Bugs

Please include:
- Tracy version/commit
- OS and Python version
- Steps to reproduce
- Expected vs. actual behavior
- Relevant logs or stack traces (sanitize sensitive info)

## Requesting Features

Describe the problem you’re trying to solve, proposed solution, any alternatives considered, and potential impact on UX/ethics/compliance.

## Security Issues

Do not create public issues for sensitive security problems. See SECURITY.md for our coordinated disclosure policy.

## License

By contributing, you agree your contributions will be licensed under the project’s license as described in LICENSE (if present).
