#!/usr/bin/env python3
"""
Tracy - Digital Footprint OSINT Tool
Main orchestrator for gathering digital intelligence
"""

import asyncio
import json
import argparse
from datetime import datetime
from typing import Dict, List, Any
import phonenumbers
from email_validator import validate_email, EmailNotValidError
import os
from pathlib import Path

from modules.social_media import SocialMediaSearcher
from modules.breach_checker import BreachChecker
from modules.search_engines import SearchEngineIntel
from modules.professional import ProfessionalSearcher
from modules.phone_intel import PhoneIntelligence
from modules.data_correlator import DataCorrelator
from modules.report_generator import ReportGenerator
from modules.util_dns_whois import resolve_dns, whois_lookup, email_domain_from_address
from config import Config


class Tracy:
    """Main OSINT orchestrator class"""
    
    def __init__(self):
        self.config = Config()
        self.results = {
            'target_info': {},
            'social_media': {},
            'breaches': {},
            'professional': {},
            'phone_intel': {},
            'search_results': {},
            'correlations': {},
            # New integrations
            'email_rep': {},
            'hunter': {},
            'dns_whois': {},
            'socialscan': {},
            'sherlock': {},
            'timestamp': datetime.now().isoformat()
        }
        
        # Initialize modules
        self.social_searcher = SocialMediaSearcher()
        self.breach_checker = BreachChecker()
        self.search_intel = SearchEngineIntel()
        self.professional_searcher = ProfessionalSearcher()
        self.phone_intel = PhoneIntelligence()
        self.correlator = DataCorrelator()
        self.report_gen = ReportGenerator()
    
    def validate_inputs(self, email: str = None, phone: str = None) -> Dict[str, Any]:
        """Validate and normalize input data"""
        validated = {'email': None, 'phone': None, 'errors': []}
        
        if email:
            try:
                validation = validate_email(email)
                validated['email'] = validation.email
            except EmailNotValidError as e:
                validated['errors'].append(f"Invalid email: {str(e)}")
        
        if phone:
            try:
                parsed_phone = phonenumbers.parse(phone, None)
                if phonenumbers.is_valid_number(parsed_phone):
                    validated['phone'] = phonenumbers.format_number(
                        parsed_phone, phonenumbers.PhoneNumberFormat.E164
                    )
                else:
                    validated['errors'].append("Invalid phone number format")
            except phonenumbers.NumberParseException as e:
                validated['errors'].append(f"Phone parsing error: {str(e)}")
        
        return validated
    
    async def investigate(self, email: str = None, phone: str = None) -> Dict[str, Any]:
        """Main investigation orchestrator"""
        print("🔍 Starting Tracy investigation...")
        
        # Validate inputs
        validated = self.validate_inputs(email, phone)
        if validated['errors']:
            return {'error': 'Validation failed', 'details': validated['errors']}
        
        self.results['target_info'] = {
            'email': validated['email'],
            'phone': validated['phone']
        }
        
        # Create investigation tasks
        tasks = []
        
        if validated['email']:
            print(f"📧 Investigating email: {validated['email']}")
            tasks.extend([
                self._search_social_media_email(validated['email']),
                self._check_breaches_email(validated['email']),
                self._search_professional_email(validated['email']),
                self._search_engines_email(validated['email']),
                self._emailrep_lookup(validated['email']),
                self._hunter_verify(validated['email']),
                self._dns_whois_for_email(validated['email']),
                self._socialscan_check(validated['email']),
                self._sherlock_check(validated['email'])
            ])
        
        if validated['phone']:
            print(f"📱 Investigating phone: {validated['phone']}")
            tasks.extend([
                self._search_social_media_phone(validated['phone']),
                self._get_phone_intelligence(validated['phone']),
                self._search_engines_phone(validated['phone'])
            ])
        
        # Execute all tasks concurrently
        print("🚀 Running concurrent searches...")
        await asyncio.gather(*tasks, return_exceptions=True)
        
        # Correlate data
        print("🔗 Correlating findings...")
        self.results['correlations'] = await self.correlator.correlate_data(self.results)
        
        # Cleanup any open aiohttp sessions in modules to avoid warnings
        await self._cleanup()
        
        print("✅ Investigation complete!")
        return self.results
    
    async def _search_social_media_email(self, email: str):
        """Search social media platforms by email"""
        try:
            results = await self.social_searcher.search_by_email(email)
            self.results['social_media'].update(results)
        except Exception as e:
            print(f"❌ Social media email search failed: {e}")
    
    async def _search_social_media_phone(self, phone: str):
        """Search social media platforms by phone"""
        try:
            results = await self.social_searcher.search_by_phone(phone)
            self.results['social_media'].update(results)
        except Exception as e:
            print(f"❌ Social media phone search failed: {e}")
    
    async def _check_breaches_email(self, email: str):
        """Check breach databases"""
        try:
            results = await self.breach_checker.check_email(email)
            self.results['breaches'] = results
        except Exception as e:
            print(f"❌ Breach check failed: {e}")
    
    async def _search_professional_email(self, email: str):
        """Search professional platforms"""
        try:
            results = await self.professional_searcher.search_by_email(email)
            self.results['professional'].update(results)
        except Exception as e:
            print(f"❌ Professional search failed: {e}")
    
    async def _search_engines_email(self, email: str):
        """Search engines intelligence"""
        try:
            results = await self.search_intel.search_email(email)
            if 'email' not in self.results['search_results']:
                self.results['search_results']['email'] = {}
            self.results['search_results']['email'].update(results)
        except Exception as e:
            print(f"❌ Search engine email search failed: {e}")
    
    async def _search_engines_phone(self, phone: str):
        """Search engines for phone"""
        try:
            results = await self.search_intel.search_phone(phone)
            if 'phone' not in self.results['search_results']:
                self.results['search_results']['phone'] = {}
            self.results['search_results']['phone'].update(results)
        except Exception as e:
            print(f"❌ Search engine phone search failed: {e}")
    
    async def _get_phone_intelligence(self, phone: str):
        """Get phone intelligence"""
        try:
            results = await self.phone_intel.analyze_phone(phone)
            self.results['phone_intel'] = results
        except Exception as e:
            print(f"❌ Phone intelligence failed: {e}")
    
    async def _cleanup(self):
        """Close any open aiohttp sessions held by modules."""
        try:
            if hasattr(self.social_searcher, "close"):
                await self.social_searcher.close()
        except Exception:
            pass
        try:
            if hasattr(self.breach_checker, "close"):
                await self.breach_checker.close()
        except Exception:
            pass
        try:
            if hasattr(self.search_intel, "close"):
                await self.search_intel.close()
        except Exception:
            pass
        try:
            if hasattr(self.phone_intel, "close"):
                await self.phone_intel.close()
        except Exception:
            pass
        try:
            if hasattr(self.professional_searcher, "close"):
                await self.professional_searcher.close()
        except Exception:
            pass

    def save_results(self, filename: str = None):
        """Save investigation results into results/<YYYY-MM-DD>/<YYYY-MM-DD_HH-mm-ss>/results.json.
        If a filename is provided and points to a .json inside 'results', it will be respected."""
        # Build dated directories
        date_str = datetime.now().strftime("%Y-%m-%d")
        ts_str = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        base_dir = Path("results") / date_str / ts_str
        base_dir.mkdir(parents=True, exist_ok=True)

        # Determine JSON path
        if filename:
            # If a custom filename is provided:
            custom_path = Path(filename)
            if not custom_path.is_absolute():
                custom_path = base_dir / custom_path.name
            json_path = custom_path
            # Ensure parent exists
            json_path.parent.mkdir(parents=True, exist_ok=True)
        else:
            json_path = base_dir / "results.json"

        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, default=str, ensure_ascii=False)

        print(f"💾 Results saved to: {json_path}")
        return str(json_path)
    
    def generate_report(self, format_type: str = 'html'):
        """Generate investigation report and store next to JSON under results/<date>/<timestamp>/report.html or report.pdf."""
        # Infer last save directory or create one if not exists
        date_str = datetime.now().strftime("%Y-%m-%d")
        ts_str = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        base_dir = Path("results") / date_str / ts_str

        # If we already saved JSON in this run, it exists; otherwise ensure it
        base_dir.mkdir(parents=True, exist_ok=True)

        report_filename = f"report.{format_type if format_type != 'json' else 'html' if format_type == 'html' else format_type}"
        # Let report_generator handle content creation; then move/write to our path if it returns content
        output_path = base_dir / report_filename

        # Some generators may expect to return a path; others return content. Handle both.
        generated = self.report_gen.generate(self.results, format_type)
        if isinstance(generated, (str, Path)) and Path(generated).exists():
            # Move/copy file to our output_path
            try:
                # Prefer copy to avoid cross-filesystem issues
                from shutil import copyfile
                copyfile(generated, output_path)
            except Exception:
                # If copy fails, try to write content
                try:
                    with open(generated, "r", encoding="utf-8", errors="ignore") as src, open(output_path, "w", encoding="utf-8") as dst:
                        dst.write(src.read())
                except Exception as e:
                    print(f"[WARN] Could not place report at {output_path}: {e}")
                    return str(generated)
        else:
            # Assume it's HTML/text content; write it
            try:
                with open(output_path, "w", encoding="utf-8") as f:
                    f.write(generated if isinstance(generated, str) else str(generated))
            except Exception as e:
                print(f"[WARN] Failed writing report content: {e}")
                return None

        return str(output_path)

    # ---------------- New integration helpers ----------------

    async def _emailrep_lookup(self, email: str):
        """Query EmailRep.io if enabled and key present."""
        import aiohttp
        if not self.config.ENABLE_EMAILREP:
            return
        # Per-integration gate: if no key, warn and skip
        if not self.config.EMAILREP_API_KEY:
            print("[WARN] Set your API first: EMAILREP_API_KEY missing; skipping EmailRep")
            self.results['email_rep'] = {'status': 'no_key', 'warning': 'Set your API first'}
            return
        headers = {'User-Agent': 'Tracy-OSINT-Tool', 'Key': self.config.EMAILREP_API_KEY}
        url = f"https://emailrep.io/{email}"
        try:
            timeout = aiohttp.ClientTimeout(total=self.config.REQUEST_TIMEOUT)
            async with aiohttp.ClientSession(timeout=timeout, headers=headers) as session:
                async with session.get(url) as resp:
                    data = await resp.json(content_type=None)
                    self.results['email_rep'] = {
                        'status': resp.status,
                        'data': data,
                        'source': 'EmailRep.io'
                    }
        except Exception as e:
            self.results['email_rep'] = {'error': str(e), 'source': 'EmailRep.io'}

    async def _hunter_verify(self, email: str):
        """Verify deliverability via Hunter.io if enabled."""
        import aiohttp
        if not self.config.ENABLE_HUNTER:
            return
        # Per-integration gate
        if not self.config.HUNTER_API_KEY:
            print("[WARN] Set your API first: HUNTER_API_KEY missing; skipping Hunter")
            self.results['hunter'] = {'status': 'no_key', 'warning': 'Set your API first'}
            return
        url = f"https://api.hunter.io/v2/email-verifier?email={email}&api_key={self.config.HUNTER_API_KEY}"
        try:
            timeout = aiohttp.ClientTimeout(total=self.config.REQUEST_TIMEOUT)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.get(url) as resp:
                    data = await resp.json(content_type=None)
                    self.results['hunter'] = {'status': resp.status, 'data': data, 'source': 'Hunter.io'}
        except Exception as e:
            self.results['hunter'] = {'error': str(e), 'source': 'Hunter.io'}

    async def _dns_whois_for_email(self, email: str):
        """Run DNS and WHOIS for the email's domain if enabled."""
        if not self.config.ENABLE_DNS_WHOIS:
            return
        domain = email_domain_from_address(email)
        if not domain:
            self.results['dns_whois'] = {'error': 'No domain parsed from email'}
            return
        try:
            dns_records = resolve_dns(domain)
            whois_info = whois_lookup(domain)
            self.results['dns_whois'] = {'dns': dns_records, 'whois': whois_info}
        except Exception as e:
            self.results['dns_whois'] = {'error': str(e)}

    async def _socialscan_check(self, email: str):
        """Check presence on platforms via socialscan CLI/library if enabled."""
        if not self.config.ENABLE_SOCIALSCAN:
            return
        # Prefer subprocess to avoid import issues; socialscan CLI prints JSON per target optionally.
        import subprocess, sys, json
        try:
            # socialscan supports emails and usernames; run for email only
            cmd = [sys.executable, "-m", "socialscan", email, "--json"]
            proc = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            output = proc.stdout.strip()
            data = []
            for line in output.splitlines():
                try:
                    data.append(json.loads(line))
                except Exception:
                    continue
            self.results['socialscan'] = {
                'returncode': proc.returncode,
                'results': data,
                'stderr': proc.stderr.strip()[:500]
            }
        except Exception as e:
            self.results['socialscan'] = {'error': str(e)}

    async def _sherlock_check(self, email: str):
        """Run Sherlock for likely usernames derived from the email if enabled."""
        if not self.config.ENABLE_SHERLOCK:
            return
        import subprocess, sys, json
        username = (email.split("@")[0] or "").strip()
        if not username:
            self.results['sherlock'] = {'error': 'No username derived from email'}
            return
        try:
            # Try calling sherlock if installed in PATH; if not installed, record note
            # Using --print-found to reduce output; JSON output varies across forks, capture stdout.
            cmd = ["sherlock", username, "--print-found"]
            proc = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
            self.results['sherlock'] = {
                'returncode': proc.returncode,
                'found': proc.stdout.splitlines()[-200:],  # last lines
                'stderr': proc.stderr.strip()[:500]
            }
        except FileNotFoundError:
            self.results['sherlock'] = {'status': 'not_installed', 'note': 'Install sherlock CLI to enable (pip or git).'}
        except Exception as e:
            self.results['sherlock'] = {'error': str(e)}


async def main():
    """CLI interface"""
    parser = argparse.ArgumentParser(description='Tracy - Digital Footprint OSINT Tool')
    parser.add_argument('--email', help='Target email address')
    parser.add_argument('--phone', help='Target phone number')
    parser.add_argument('--output', help='Output filename')
    parser.add_argument('--report', choices=['html', 'pdf', 'json'], 
                       default='html', help='Report format')
    
    args = parser.parse_args()
    
    if not args.email and not args.phone:
        print("❌ Please provide at least an email or phone number")
        return
    
    # Initialize Tracy
    tracy = Tracy()
    
    # Run investigation
    results = await tracy.investigate(email=args.email, phone=args.phone)
    
    if 'error' in results:
        print(f"❌ Investigation failed: {results['error']}")
        if 'details' in results:
            for detail in results['details']:
                print(f"   - {detail}")
        return
    
    # Save results (JSON)
    output_file = tracy.save_results(args.output)

    # Generate report (HTML/PDF/JSON)
    report_file = tracy.generate_report(args.report)
    if report_file:
        print(f"📊 Report generated: {report_file}")
    else:
        print("📊 Report generation skipped or failed.")
    
    # Print summary
    print("\n" + "="*50)
    print("🎯 INVESTIGATION SUMMARY")
    print("="*50)
    
    if results['target_info']['email']:
        print(f"📧 Email: {results['target_info']['email']}")
    if results['target_info']['phone']:
        print(f"📱 Phone: {results['target_info']['phone']}")
    
    print(f"\n🔍 Platforms searched: {len([k for k in results.keys() if results[k]])}")
    print(f"🔗 Correlations found: {len(results.get('correlations', {}))}")
    
    if results.get('breaches'):
        breach_count = len(results['breaches'].get('breaches', []))
        print(f"🚨 Breaches found: {breach_count}")
    
    print(f"\n📁 Full results: {output_file}")
    print(f"📊 Report: {report_file}")


if __name__ == "__main__":
    asyncio.run(main())
