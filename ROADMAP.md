# Roadmap

High-level plan for Tracy’s evolution. Subject to change based on community needs and responsible-use constraints.

## 1. Core Capabilities

- Correlation Engine v2
  - Confidence scoring per signal (email/phone/username/domain)
  - Entity resolution across modules with provenance metadata
  - Duplicate suppression and normalization

- Professional/Community Integrations
  - Additional platforms (StackOverflow deep links, GitLab/Bitbucket heuristics, Medium/Dev.to mentions)
  - Company-centric discovery (press releases, staff pages, job postings)

- Reporting Enhancements
  - Themed HTML templates (light/dark, print-friendly)
  - PDF export via optional renderer (documented dependency)
  - Custom sections toggles (include/exclude modules)

## 2. OSINT Integrations

- Email/Identity
  - More reputation services behind feature flags
  - Enrichment link-outs (Gravatar hashes, PGP keyservers)

- Phone
  - Country-specific sources expansion (EU/LatAm/APAC directories)
  - Spam/scam datasets link-outs

- DNS/Network
  - Passive DNS link-outs (e.g., securitytrails-like endpoints)
  - Subdomain discovery: safe-only methodology (no brute force)

## 3. UX & Dashboard

- Dashboard Improvements
  - Persisted workspace: choose a saved results.json and explore
  - Filters: by module, risk, time, platform
  - Graph improvements: clustering, node details side panel, export graph

- CLI Ergonomics
  - Configurable concurrency limits and backoff
  - Verbosity flags and structured logs (JSONL)
  - Dry-run mode (generate dorks/links without making any network calls)

## 4. Packaging & Distribution

- Docker image (optional, opt-in only)
  - Clear instructions, minimal permissions, safe defaults

- Binary distribution (research)
  - PyInstaller/Briefcase experiments
  - Documented limitations for network-heavy tooling

## 5. Quality & Compliance

- Docs
  - How-to guides per module (email-only, phone-only, DNS/WHOIS-only)
  - Expanded troubleshooting and FAQ
  - Ethical use case guides and templates for authorization

- Testing
  - Mocked tests for network modules
  - CI to validate basic flows (lint, type check, docs links)

## Principles

- Respect platform Terms of Service; link-out over scraping wherever appropriate
- Degrade gracefully with missing API keys
- Guardrails for rate limiting and safe automation
- Transparency: make it clear what data came from where and when

If you’d like to help with any roadmap item, open an issue to coordinate work and avoid overlap.
