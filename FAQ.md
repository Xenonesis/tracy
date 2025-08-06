# FAQ

Frequently asked questions about Tracy.

## What is Tracy?

Tracy is a privacy‑respecting OSINT orchestrator that gathers digital‑footprint signals from public sources starting with an email and/or phone number. It aggregates results, correlates them, and outputs reports and an interactive dashboard.

## Does Tracy require API keys?

No. Tracy runs with safe defaults and will still produce meaningful link‑outs and results. Some integrations (e.g., HaveIBeenPwned, DeHashed, EmailRep, Hunter) require API keys to return live data. Without keys, modules degrade gracefully and annotate results.

## How do I configure keys?

Copy .env.example to .env and fill the keys you need. See README “Configuration” for variables and feature toggles. You can disable any integration via ENABLE_* flags.

## Will Tracy scrape websites?

Tracy prefers link‑outs and minimal HEAD checks to respect Terms of Service. Where APIs or public JSON endpoints exist (e.g., DuckDuckGo Instant Answers), Tracy uses them. Some modules only provide actionable links rather than scraping.

## Where are results saved?

Under results/YYYY-MM-DD/YYYY-MM-DD_HH-MM-SS/:
- results.json
- report.html (default)
Additional report formats may be generated via report_generator.py.

## How do I run the dashboard?

From README’s “Interactive Dashboard” section. Common one‑liner:
```
python -c "from modules.dashboard import InteractiveDashboard; app = InteractiveDashboard(); app.run()"
```
It starts at http://127.0.0.1:8050 and allows running an investigation by email or viewing existing results.

## Why do some modules say “no_key” or “Link provided”?

These modules require API keys or accounts to return live data. Tracy surfaces helpful links or statuses so users can verify manually or add keys later.

## Can I add new sources?

Yes. Add a new module under modules/ and wire it in tracy.py, respecting async patterns, safe HTTP calls, feature flags, and ToS. Document the feature and keys in README and CONTRIBUTING.

## How are risks scored?

- breach_checker computes a coarse risk score based on breach count.
- phone_intel uses simple heuristics (number validity, type, carrier/location presence).
These are indicative only—always interpret in context.

## PDF report output?

HTML/Markdown/Text are generated natively. For PDF, you may integrate a renderer (e.g., wkhtmltopdf or a headless browser) and adapt report_generator; see ROADMAP.

## socialscan / sherlock not found?

Install them and ensure they’re on PATH:
```
pip install socialscan
# Sherlock may require separate install or repo clone
```
Tracy will annotate results if a tool is unavailable rather than failing hard.

## Is Docker supported?

Not yet. It’s on the ROADMAP. You can create a simple image, but ensure network/DNS and certificates are configured for outbound calls.

## Responsible use?

Only investigate targets you are authorized to assess. Follow laws and service terms. Handle outputs securely. See SECURITY.md and README ethics notes.
