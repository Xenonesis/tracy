# Changelog

All notable changes to this project will be documented in this file.
The format follows Keep a Changelog and Semantic Versioning where practical.

## Unreleased
- Documentation: Comprehensive README with architecture, usage, dashboard, and troubleshooting
- Docs: CONTRIBUTING.md, CODE_OF_CONDUCT.md, SECURITY.md, CHANGELOG.md, ROADMAP.md, FAQ.md, TROUBLESHOOTING.md
- Orchestrator: tracy.py async investigation for email/phone with validation
- Modules:
  - social_media.py: platform heuristics, public link-outs, safe HEAD checks
  - breach_checker.py: HIBP + DeHashed integrations (optional keys), live-search links
  - search_engines.py: dork generation, Google/Bing link-outs, DuckDuckGo instant results
  - phone_intel.py: libphonenumber intelligence + risk assessment
  - util_dns_whois.py: DNS+WHOIS via dnspython/python-whois
  - report_generator.py: HTML/Markdown/Text/JSON reports via Jinja2
  - dashboard.py: Dash/Plotly interactive dashboard
- Config:
  - config.py feature flags, timeouts, UA rotation, dashboard settings
  - .env.example with keys and ENABLE_* toggles
- Outputs:
  - results/<date>/<timestamp>/results.json and report.html
