# Tracy — Digital Footprint OSINT Tool

Tracy is a modern Open Source Intelligence (OSINT) orchestrator that maps a target’s digital footprint starting from an email and/or phone number. It runs concurrent, privacy‑respecting checks across social platforms, breach sources, search engines, DNS/WHOIS, and reputation/verification services, correlates signals, and generates reports and an interactive dashboard.

Key goals:
- Safe defaults using only publicly available information, with optional API integrations
- Async-first architecture for fast concurrent investigations
- Clean output artifacts (JSON + HTML/Markdown/Text reports) and a visual dashboard

--------------------------------------------------------------------------------

## Highlights

- Email and phone as inputs
- Concurrent OSINT modules:
  - Social media discovery (public/profile heuristics and actionable links)
  - Breach intelligence (HIBP, DeHashed, plus live-search links)
  - Search engine dorking (Google/Bing link-out + DuckDuckGo instant answers)
  - Phone intelligence (carrier/region/timezone via libphonenumber, OSINT sources)
  - DNS and WHOIS lookups (dnspython + python-whois)
  - Reputation/verification (EmailRep, Hunter)
  - Optional presence checks (socialscan, Sherlock usernames)
- Correlation engine to summarize cross-signal insights
- Report generator: HTML, Markdown, Text, JSON
- Interactive dashboard (Dash/Plotly) for exploration

--------------------------------------------------------------------------------

## Architecture Overview

Entry point:
- tracy.py — Orchestrates the entire investigation lifecycle:
  - Validates inputs (email, phone)
  - Runs async tasks for selected modules
  - Correlates findings
  - Saves structured results and generates a report

Core modules (modules/):
- social_media.py
  - Searches by email/phone with platform-specific strategies
  - Uses safe methods (HEAD checks, public search links, minimal rate-limited calls)
- breach_checker.py
  - Integrations for HaveIBeenPwned (requires API), DeHashed (requires credentials)
  - Provides live-search links for BreachDirectory and LeakCheck
  - Aggregates breaches/pastes and computes a simple risk score
- search_engines.py
  - Generates dorks for email/phone
  - Google/Bing results provided as link-outs (respecting ToS)
  - DuckDuckGo Instant Answer API usage where applicable
  - Reverse phone helper with public resources
- phone_intel.py
  - Validates and formats numbers (E.164, national, international)
  - Carrier/region/timezones via libphonenumber
  - OSINT sources by region; simple risk assessment
- util_dns_whois.py
  - DNS record resolution (A/AAAA/MX/NS/TXT)
  - WHOIS lookup via python-whois
- report_generator.py
  - HTML/Markdown/Text/JSON report generation via Jinja2
- dashboard.py
  - Dash/Plotly-driven interactive dashboard to browse and visualize results

Configuration:
- config.py — Centralizes feature toggles, API keys via .env, timeouts, user-agents, and dashboard settings

--------------------------------------------------------------------------------

## Installation

Prerequisites:
- Python 3.10+ recommended
- pip and virtualenv (optional but recommended)
- On Windows, ensure build tools are available for any packages that may require them

1) Clone and setup environment
```
git clone https://github.com/your-org/tracy.git
cd tracy
python -m venv .venv
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # macOS/Linux
```

2) Install dependencies
```
pip install --upgrade pip
pip install -r requirements.txt
```

3) Configure environment
- Copy .env.example to .env and fill the keys you want to enable
```
cp .env.example .env
```

Minimum usage does not require any API keys, but some integrations will be no-ops without them.

--------------------------------------------------------------------------------

## Configuration

Environment variables (.env) read by config.py:

API keys (optional):
- SHODAN_API_KEY
- TWITTER_BEARER_TOKEN
- HAVEIBEENPWNED_API_KEY
- DEHASHED_API_KEY
- DEHASHED_USERNAME
- EMAILREP_API_KEY
- HUNTER_API_KEY

Feature toggles (defaults to true if missing):
- ENABLE_EMAILREP
- ENABLE_HIBP
- ENABLE_HUNTER
- ENABLE_SOCIALSCAN
- ENABLE_DNS_WHOIS
- ENABLE_SHERLOCK

Operational settings:
- REQUEST_TIMEOUT (default 30)
- RATE_LIMIT_DELAY (default 1)
- MAX_RESULTS_PER_PLATFORM (default 50)
- DASH_HOST/DASH_PORT/DASH_DEBUG for the dashboard

Fill .env similar to:
```
# Example
EMAILREP_API_KEY=your_emailrep_api_key_here
HUNTER_API_KEY=your_hunter_api_key_here
HAVEIBEENPWNED_API_KEY=your_hibp_api_key_here
DEHASHED_API_KEY=your_dehashed_api_key_here
DEHASHED_USERNAME=your_dehashed_username_here

ENABLE_EMAILREP=true
ENABLE_HIBP=true
ENABLE_HUNTER=true
ENABLE_SOCIALSCAN=true
ENABLE_DNS_WHOIS=true
ENABLE_SHERLOCK=true
```

--------------------------------------------------------------------------------

## Usage

Basic CLI:
```
python tracy.py --email target@example.com
python tracy.py --phone +15551234567
python tracy.py --email target@example.com --phone +15551234567
```

Options:
- --email EMAIL            Email address to investigate
- --phone PHONE            Phone number to investigate
- --output FILE            Optional custom results JSON path under results/
- --report {html,pdf,json} Report format; defaults to html
  - Note: HTML/Markdown/Text are generated by report_generator.py
  - For pdf you may need a local converter/renderer; otherwise HTML is recommended

Example:
```
python tracy.py --email jane.doe@example.com --report html
```

Outputs:
- Results are stored under results/YYYY-MM-DD/YYYY-MM-DD_HH-MM-SS/
  - results.json — full structured data
  - report.html — generated report next to results.json

--------------------------------------------------------------------------------

## Interactive Dashboard

Launch the dashboard to explore investigation data interactively.

Run:
```
python -c "from modules.dashboard import InteractiveDashboard; app = InteractiveDashboard(); app.run()"
```
By default:
- URL: http://127.0.0.1:8050
- Enter an email and click “Search” to run a fresh investigation
- Summary cards, tabs (Summary, Breaches, Social, Professional, Correlations, Network Graph, Raw Data)

You can also load previously saved results by modifying dashboard initialization, e.g.:
```
from modules.dashboard import InteractiveDashboard
dash = InteractiveDashboard()
dash.load_investigation_data('results/2025-08-06/2025-08-06_11-13-45/results.json')
dash.run()
```

--------------------------------------------------------------------------------

## Data Flow

1) tracy.py validates inputs (email with email-validator, phone with phonenumbers)
2) Async tasks execute per enabled feature:
   - social_media: platform heuristics, public link-outs, minimal HEAD checks
   - breach_checker: HIBP/DeHashed (if configured), live-search links for others
   - search_engines: produced Google/Bing link-outs + DDG instant answers
   - phone_intel: libphonenumber signals + OSINT sources
   - util_dns_whois: DNS + WHOIS
   - email reputation/verification: EmailRep/Hunter (if keys present)
   - optional tools: socialscan, sherlock
3) Results aggregated and correlated
4) Results serialized under results/<date>/<timestamp>
5) Report generated (HTML/Markdown/Text/JSON)
6) Optional: Visualize in Dash

--------------------------------------------------------------------------------

## Notes on Integrations and Ethics

- This tool uses only publicly available endpoints by default. Some modules provide links rather than scraping results, to respect Terms of Service.
- Where APIs require keys (HIBP, DeHashed, EmailRep, Hunter), the module gracefully degrades when keys are missing.
- socialscan and sherlock are optional and may need separate installation or CLI availability on PATH. If unavailable, the tool records a status note rather than failing.

Legal and responsible use:
- Use only on targets you are authorized to assess
- Comply with all local laws and platform policies
- Avoid aggressive automation; respect rate limits and robots directives
- Reports may contain sensitive information; handle securely

--------------------------------------------------------------------------------

## Examples

Run with email only:
```
python tracy.py --email alice@example.com
```

Run with phone only:
```
python tracy.py --phone +442071234567
```

Custom output location:
```
python tracy.py --email alice@example.com --output results/custom_run/results.json
```

Generate JSON instead of HTML:
```
python tracy.py --email alice@example.com --report json
```

--------------------------------------------------------------------------------

## Output Structure

results/YYYY-MM-DD/YYYY-MM-DD_HH-MM-SS/
- results.json
- report.html (default)
- report.md / report.txt / tracy_report_*.{html,md,txt,json} as applicable

Top-level JSON keys:
- target_info: { email, phone }
- social_media: platform-indexed findings
- breaches: { breaches[], pastes[], total_breaches, risk_score, sources_checked[] }
- professional: platform-indexed findings (from modules like LinkedIn/GitHub heuristics)
- phone_intel: validation, carrier, region/timezone, risk assessment, OSINT sources
- search_results: { email: {google_results, bing_results, duckduckgo_results, dorking_queries}, phone: {...} }
- dns_whois: { dns: {...}, whois: {...} }
- email_rep / hunter / socialscan / sherlock: integration-specific payloads
- correlations: summarization and cross-platform matches
- timestamp: ISO 8601

--------------------------------------------------------------------------------

## Troubleshooting

- SSL/Certificates: If aiohttp/cert verification errors occur, ensure system certificates are up to date.
- HTTP 429 / Rate limits: Modules intentionally limit requests; still, try again later or reduce queries.
- Missing keys: If a module warns about a missing API key, populate .env and re-run.
- socialscan/sherlock not found: Install and ensure on PATH. Example:
  - pip install socialscan
  - sherlock may require separate installation (pip or cloned repo)
- Windows firewall: If DNS/WHOIS fails, ensure outbound DNS queries and WHOIS ports are not blocked.
- Package versions: See requirements.txt. If conflicts arise, consider a fresh virtualenv.

--------------------------------------------------------------------------------

## Requirements

See requirements.txt for pinned versions. Major libraries:
- aiohttp, asyncio
- phonenumbers, email-validator
- dnspython, python-whois
- Dash, Plotly, pandas, networkx
- jinja2
- fake-useragent
- Optional: socialscan, shodan, tweepy, praw, linkedin-api, googlesearch-python, etc.

--------------------------------------------------------------------------------

## Roadmap

- Additional professional and community platform adapters
- Deeper correlation heuristics and confidence scoring
- Optional headless browser flows for authenticated sources (behind feature flags)
- Export improvements (PDF theming, CSV selectors)
- Docker support and packaged binaries

--------------------------------------------------------------------------------

## License

This project is intended for educational and authorized security research. Use responsibly and lawfully. See LICENSE if included in this repository.
