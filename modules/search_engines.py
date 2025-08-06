"""
Search Engine Intelligence Module
Performs advanced search engine queries and dorking
"""

import asyncio
import aiohttp
import re
from typing import Dict, List, Any
from urllib.parse import quote
from fake_useragent import UserAgent
from config import Config
from contextlib import asynccontextmanager


class SearchEngineIntel:
    """Search engine intelligence gatherer"""
    
    def __init__(self):
        self.config = Config()
        self.ua = UserAgent()
        self.session = None
    
    async def _get_session(self):
        """Get or create aiohttp session"""
        if not self.session:
            self.session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=self.config.REQUEST_TIMEOUT),
                headers={'User-Agent': self.ua.random}
            )
        return self.session

    @asynccontextmanager
    async def session_scope(self):
        """
        Provide a temporary session for one-off requests without leaking.
        Prefer this over self._get_session() when doing limited calls.
        """
        session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=self.config.REQUEST_TIMEOUT),
            headers={'User-Agent': self.ua.random}
        )
        try:
            yield session
        finally:
            await session.close()
    
    async def search_email(self, email: str) -> Dict[str, Any]:
        """Search for email across search engines"""
        results = {
            'email': email,
            'google_results': [],
            'bing_results': [],
            'duckduckgo_results': [],
            'dorking_queries': [],
            'social_mentions': [],
            'professional_mentions': []
        }
        
        # Generate search queries
        queries = self._generate_email_queries(email)
        results['dorking_queries'] = queries
        
        # Search engines
        tasks = [
            self._google_search(email, queries[:5]),  # Limit queries to avoid rate limiting
            self._bing_search(email, queries[:5]),
            self._duckduckgo_search(email, queries[:5])
        ]
        
        search_results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        if not isinstance(search_results[0], Exception):
            results['google_results'] = search_results[0]
        if not isinstance(search_results[1], Exception):
            results['bing_results'] = search_results[1]
        if not isinstance(search_results[2], Exception):
            results['duckduckgo_results'] = search_results[2]
        
        return results
    
    async def search_phone(self, phone: str) -> Dict[str, Any]:
        """Search for phone number across search engines"""
        results = {
            'phone': phone,
            'google_results': [],
            'bing_results': [],
            'truecaller_info': {},
            'reverse_lookup': {},
            'dorking_queries': []
        }
        
        # Generate phone search queries
        queries = self._generate_phone_queries(phone)
        results['dorking_queries'] = queries
        
        # Search engines
        tasks = [
            self._google_search(phone, queries[:5]),
            self._bing_search(phone, queries[:5]),
            self._reverse_phone_lookup(phone)
        ]
        
        search_results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        if not isinstance(search_results[0], Exception):
            results['google_results'] = search_results[0]
        if not isinstance(search_results[1], Exception):
            results['bing_results'] = search_results[1]
        if not isinstance(search_results[2], Exception):
            results['reverse_lookup'] = search_results[2]
        
        return results
    
    def _generate_email_queries(self, email: str) -> List[str]:
        """Generate Google dorking queries for email"""
        username = email.split('@')[0]
        domain = email.split('@')[1]
        
        queries = [
            f'"{email}"',
            f'"{email}" -site:linkedin.com',
            f'"{email}" site:facebook.com',
            f'"{email}" site:twitter.com',
            f'"{email}" site:instagram.com',
            f'"{email}" site:github.com',
            f'"{email}" site:stackoverflow.com',
            f'"{email}" site:reddit.com',
            f'"{email}" filetype:pdf',
            f'"{email}" filetype:doc',
            f'"{email}" filetype:docx',
            f'"{email}" filetype:xls',
            f'"{email}" "contact" OR "email"',
            f'"{username}" site:{domain}',
            f'"{username}" "{domain.split(".")[0]}"',
            f'"{email}" "resume" OR "cv"',
            f'"{email}" "profile" OR "about"',
            f'"{email}" "phone" OR "mobile"',
            f'"{email}" "address" OR "location"',
            f'intext:"{email}" site:pastebin.com',
            f'intext:"{email}" site:paste.org',
            f'"{email}" "breach" OR "leak" OR "dump"'
        ]
        
        return queries
    
    def _generate_phone_queries(self, phone: str) -> List[str]:
        """Generate search queries for phone number"""
        # Format variations
        clean_phone = re.sub(r'[^\d]', '', phone)
        formatted_variations = [
            phone,
            clean_phone,
            f"+{clean_phone[1:]}" if clean_phone.startswith('1') else f"+1{clean_phone}",
            f"({clean_phone[1:4]}) {clean_phone[4:7]}-{clean_phone[7:]}" if len(clean_phone) == 11 else phone,
            f"{clean_phone[:3]}-{clean_phone[3:6]}-{clean_phone[6:]}" if len(clean_phone) >= 10 else phone
        ]
        
        queries = []
        for variation in formatted_variations:
            queries.extend([
                f'"{variation}"',
                f'"{variation}" -site:whitepages.com',
                f'"{variation}" site:facebook.com',
                f'"{variation}" site:linkedin.com',
                f'"{variation}" "contact" OR "phone"',
                f'"{variation}" "business" OR "company"',
                f'"{variation}" "resume" OR "cv"'
            ])
        
        return list(set(queries))  # Remove duplicates
    
    async def _google_search(self, query: str, queries: List[str]) -> List[Dict[str, Any]]:
        """Perform Google search using public HTML endpoint (metadata only, no scraping of results)."""
        # We avoid parsing Google HTML to respect ToS. Provide direct search URLs as actionable links.
        results = []
        for q in queries[:3]:  # keep minimal to avoid hitting rate limits
            results.append({
                'query': q,
                'engine': 'Google',
                'status': 'Link provided',
                'url': f'https://www.google.com/search?q={quote(q)}',
                'note': 'Open the link to view live results in the browser'
            })
        return results
    
    async def _bing_search(self, query: str, queries: List[str]) -> List[Dict[str, Any]]:
        """Perform Bing search using public HTML endpoint (metadata only)."""
        results = []
        for q in queries[:3]:
            results.append({
                'query': q,
                'engine': 'Bing',
                'status': 'Link provided',
                'url': f'https://www.bing.com/search?q={quote(q)}',
                'note': 'Open the link to view live results in the browser'
            })
        return results
    
    async def _duckduckgo_search(self, query: str, queries: List[str]) -> List[Dict[str, Any]]:
        """Perform DuckDuckGo search via JSON endpoint (free, no key)."""
        # Use DuckDuckGo Instant Answer API for structured results when possible.
        results: List[Dict[str, Any]] = []
        try:
            async with self.session_scope() as session:
                for q in queries[:2]:
                    # DDG Instant Answer API
                    url = f'https://api.duckduckgo.com/?q={quote(q)}&format=json&no_redirect=1&no_html=1'
                    async with session.get(url) as resp:
                        if resp.status == 200:
                            data = await resp.json(content_type=None)
                            packaged = {
                                'query': q,
                                'engine': 'DuckDuckGo',
                                'status': 'OK',
                                'api_url': url,
                                'AbstractText': data.get('AbstractText') or '',
                                'AbstractURL': data.get('AbstractURL') or '',
                                'Heading': data.get('Heading') or '',
                                'RelatedTopics': []
                            }
                            # Extract a few related topics as links (if present)
                            rt = data.get('RelatedTopics') or []
                            links = []
                            for item in rt:
                                if isinstance(item, dict):
                                    if 'FirstURL' in item and 'Text' in item:
                                        links.append({'title': item.get('Text'), 'url': item.get('FirstURL')})
                                    # Some items contain nested Topics
                                    if 'Topics' in item and isinstance(item['Topics'], list):
                                        for t in item['Topics']:
                                            if 'FirstURL' in t and 'Text' in t:
                                                links.append({'title': t.get('Text'), 'url': t.get('FirstURL')})
                            packaged['RelatedTopics'] = links[:5]
                            results.append(packaged)
                        else:
                            results.append({
                                'query': q,
                                'engine': 'DuckDuckGo',
                                'status': f'Error: {resp.status}',
                                'api_url': url
                            })
                    await asyncio.sleep(1)
        except Exception as e:
            results.append({'engine': 'DuckDuckGo', 'error': str(e)})
        return results
    
    async def _reverse_phone_lookup(self, phone: str) -> Dict[str, Any]:
        """Perform reverse phone lookup using free OSINT-friendly endpoints."""
        # We will provide actionable public lookups and spam sources without scraping protected content.
        e164 = re.sub(r'[^\d+]', '', phone)
        country_hint = 'us'  # best-effort default; real region comes from phone_intel module
        lookups = {
            'opencnam': f'https://api.opencnam.com/v3/phone/{quote(e164)}',  # free limited unauth endpoints sometimes rate limited
            'duckduckgo_search': f'https://duckduckgo.com/?q={quote(e164)}',
            'google_search': f'https://www.google.com/search?q={quote(e164)}',
            'who_called': f'https://www.whocalled.us/lookup/{quote(e164)}',
            'spamhouse_info': 'https://www.spamhaus.org/faq/section/Spamhaus%20DBL'
        }
        return {
            'phone': phone,
            'public_endpoints': lookups,
            'notes': [
                'OpenCNAM unauthenticated calls may be throttled; treat as best-effort.',
                'Open links to view live data; do not rely on cached placeholders.'
            ]
        }
    
    async def advanced_dorking(self, target: str, target_type: str = 'email') -> Dict[str, Any]:
        """Perform advanced Google dorking"""
        if target_type == 'email':
            queries = self._generate_advanced_email_dorks(target)
        else:
            queries = self._generate_advanced_phone_dorks(target)
        
        return {
            'target': target,
            'target_type': target_type,
            'advanced_queries': queries,
            'categories': {
                'social_media': [q for q in queries if any(site in q for site in ['facebook', 'twitter', 'instagram'])],
                'professional': [q for q in queries if any(site in q for site in ['linkedin', 'github', 'stackoverflow'])],
                'documents': [q for q in queries if 'filetype:' in q],
                'breaches': [q for q in queries if any(term in q for term in ['breach', 'leak', 'dump', 'paste'])],
                'contact_info': [q for q in queries if any(term in q for term in ['contact', 'phone', 'address'])]
            }
        }
    
    def _generate_advanced_email_dorks(self, email: str) -> List[str]:
        """Generate advanced Google dorks for email"""
        username = email.split('@')[0]
        domain = email.split('@')[1]
        company = domain.split('.')[0]
        
        return [
            # Document searches
            f'"{email}" filetype:pdf "resume" OR "cv"',
            f'"{email}" filetype:doc OR filetype:docx "contact"',
            f'"{email}" filetype:xls OR filetype:xlsx',
            f'"{email}" filetype:ppt OR filetype:pptx',
            
            # Social media deep searches
            f'site:facebook.com "{email}" OR "{username}"',
            f'site:twitter.com "{email}" OR "{username}"',
            f'site:instagram.com "{username}"',
            f'site:linkedin.com/in "{username}" OR "{email}"',
            
            # Professional platforms
            f'site:github.com "{email}" OR "{username}"',
            f'site:stackoverflow.com "{email}" OR "{username}"',
            f'site:gitlab.com "{email}" OR "{username}"',
            f'site:bitbucket.org "{email}" OR "{username}"',
            
            # Forums and communities
            f'site:reddit.com "{email}" OR "{username}"',
            f'site:quora.com "{email}" OR "{username}"',
            f'site:medium.com "{email}" OR "{username}"',
            
            # Breach and leak searches
            f'"{email}" site:pastebin.com OR site:paste.org',
            f'"{email}" "database" "leak" OR "breach"',
            f'"{email}" "dump" OR "hacked"',
            
            # Company and professional info
            f'"{email}" "{company}" "employee" OR "staff"',
            f'"{email}" "phone" OR "mobile" OR "cell"',
            f'"{email}" "address" OR "location"',
            
            # Advanced combinations
            f'"{username}" "{company}" -site:{domain}',
            f'"{email}" ("contact us" OR "about us" OR "team")',
            f'"{email}" ("biography" OR "bio" OR "profile")'
        ]
    
    def _generate_advanced_phone_dorks(self, phone: str) -> List[str]:
        """Generate advanced Google dorks for phone"""
        clean_phone = re.sub(r'[^\d]', '', phone)
        
        return [
            f'"{phone}" "contact" OR "phone"',
            f'"{phone}" "business" OR "company"',
            f'"{phone}" "address" OR "location"',
            f'"{phone}" filetype:pdf',
            f'"{phone}" site:facebook.com',
            f'"{phone}" site:linkedin.com',
            f'"{phone}" "resume" OR "cv"',
            f'"{clean_phone}" "directory" OR "listing"'
        ]
    
    async def close(self):
        """Close the session and release resources."""
        if self.session and not self.session.closed:
            await self.session.close()
        self.session = None
