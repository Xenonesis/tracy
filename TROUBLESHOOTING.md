# Troubleshooting

Common issues and fixes when running Tracy.

## Installation and Environment

### Problem: pip install fails or times out
- Ensure Python 3.10+ is installed and on PATH.
- Upgrade tooling:
```
python -m pip install --upgrade pip setuptools wheel
```
- Use a clean virtual environment:
```
python -m venv .venv
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # macOS/Linux
pip install -r requirements.txt
```
- If a specific package fails, try installing it alone to see the error:
```
pip install package_name==version
```

### Problem: Build tools/compiler errors on Windows
- Install “Build Tools for Visual Studio” and ensure C++ build tools are selected.
- Alternatively, try older/newer binary wheels if available for the package.

## Runtime Errors

### Problem: SSL certificate verify failed
- Update certs on your OS. On macOS: run Install Certificates.command from your Python folder.
- Try upgrading certifi:
```
pip install --upgrade certifi
```

### Problem: HTTP 429 / rate-limited
- Wait and retry later.
- Reduce queries; modules already keep calls minimal.
- Disable non-essential integrations temporarily via ENABLE_* flags in .env.

### Problem: Missing API keys or “no_key” status
- Copy .env.example to .env and fill the keys you intend to use.
- Ensure the feature toggle is true (e.g., ENABLE_HIBP=true).
- Restart your shell after editing .env if your environment doesn’t auto-load it.

### Problem: socialscan / sherlock not found
- Install and ensure they’re on PATH:
```
pip install socialscan
# Sherlock may require separate installation or a repo clone
```
- If still unavailable, Tracy will log a status and continue.

### Problem: WHOIS or DNS lookups failing
- Confirm outbound DNS and WHOIS traffic is allowed by firewall.
- Some TLDs/registrars throttle or block automated WHOIS; results may vary.
- Retry with a different network if corporate proxy blocks WHOIS.

### Problem: “Please provide at least an email or phone number”
- The CLI requires at least one of: --email or --phone.
- Examples:
```
python tracy.py --email user@example.com
python tracy.py --phone +15551234567
```

### Problem: Email validation error
- Ensure the email is correctly formatted. The validator may reject uncommon but invalid forms.
- Try quoting on shells if special characters are present.

### Problem: Phone parsing error
- Provide country code (E.164) when possible: +<country><number>, e.g., +15551234567.
- Some shortcodes or service numbers may be unsupported by libphonenumber.

## Dashboard Issues

### Problem: Dashboard doesn’t start
- Port already in use. Change port in .env (DASH_PORT) or run on a different one.
- Verify Dash/Flask/Werkzeug versions match requirements.txt.

### Problem: Dashboard loads but “No data available”
- Enter an email and click “Search” to run an investigation.
- Or load an existing results.json via code:
```
from modules.dashboard import InteractiveDashboard
dash = InteractiveDashboard()
dash.load_investigation_data('results/YYYY-MM-DD/TS/results.json')
dash.run()
```

### Problem: Network graph empty
- If few signals are found, the graph may have only the target node.
- Try a different target or enable more integrations with valid API keys.

## Reports and Outputs

### Problem: Report not found or empty
- tracy.py writes results then calls report_generator. Check console output for the exact paths.
- Default outputs:
  - results/YYYY-MM-DD/YYYY-MM-DD_HH-MM-SS/results.json
  - results/YYYY-MM-DD/YYYY-MM-DD_HH-MM-SS/report.html

### Problem: PDF export
- HTML/Markdown/Text are supported out-of-the-box.
- For PDF, integrate a renderer (wkhtmltopdf/headless browser) and extend report_generator. See ROADMAP.

## Performance and Reliability

### Problem: Slow runs
- Network latency and rate limits dominate. Limit enabled modules via ENABLE_* toggles.
- Ensure a stable network with working DNS resolution.
- Avoid running multiple heavy OSINT tools concurrently on the same machine.

### Problem: Event loop / asyncio warnings
- The orchestrator cleans up sessions, but noisy environments may still emit warnings.
- Ensure modules are closed after runs and avoid nested loops when importing from external environments.

## Getting Help

- Check README, FAQ, and ROADMAP for guidance and context.
- Open an issue with:
  - OS, Python version
  - Steps to reproduce
  - Logs/tracebacks (sanitized)
  - Tracy commit hash and whether running inside a venv
- For security-sensitive problems, follow SECURITY.md instead of opening a public issue.
