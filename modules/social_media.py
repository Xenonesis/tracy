"""
Social Media Intelligence Module
Searches across various social media platforms
"""

import asyncio
import aiohttp
import re
from typing import Dict, List, Any
from urllib.parse import quote
from fake_useragent import UserAgent
from config import Config


class SocialMediaSearcher:
    """Social media platform searcher"""
    
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
    
    async def search_by_email(self, email: str) -> Dict[str, Any]:
        """Search social media platforms by email"""
        results = {}
        
        tasks = [
            self._search_facebook_email(email),
            self._search_twitter_email(email),
            self._search_instagram_email(email),
            self._search_linkedin_email(email),
            self._search_reddit_email(email),
            self._search_github_email(email),
            self._search_tiktok_email(email)
        ]
        
        platform_results = await asyncio.gather(*tasks, return_exceptions=True)
        
        platforms = ['facebook', 'twitter', 'instagram', 'linkedin', 'reddit', 'github', 'tiktok']
        for platform, result in zip(platforms, platform_results):
            if not isinstance(result, Exception) and result:
                results[platform] = result
        
        return results
    
    async def search_by_phone(self, phone: str) -> Dict[str, Any]:
        """Search social media platforms by phone"""
        results = {}
        
        tasks = [
            self._search_facebook_phone(phone),
            self._search_twitter_phone(phone),
            self._search_telegram_phone(phone),
            self._search_whatsapp_phone(phone)
        ]
        
        platform_results = await asyncio.gather(*tasks, return_exceptions=True)
        
        platforms = ['facebook', 'twitter', 'telegram', 'whatsapp']
        for platform, result in zip(platforms, platform_results):
            if not isinstance(result, Exception) and result:
                results[platform] = result
        
        return results
    
    async def _search_facebook_email(self, email: str) -> Dict[str, Any]:
        """Search Facebook for email (limited due to privacy restrictions)"""
        return {
            'platform': 'Facebook',
            'search_type': 'email',
            'query': email,
            'results': [],
            'note': 'Facebook search limited due to privacy restrictions',
            'recommendations': [
                'Try manual search on Facebook',
                'Check if email is associated with public Facebook posts',
                'Look for the email in Facebook group member lists (if accessible)'
            ]
        }
    
    async def _search_twitter_email(self, email: str) -> Dict[str, Any]:
        """Provide actionable public search links for X/Twitter (no free API)."""
        username = email.split('@')[0]
        queries = [
            f'"{email}"',
            f'{username}',
            f'"{email}" OR {username}'
        ]
        links = [f'https://twitter.com/search?q={quote}&src=typed_query' for quote in [q.replace(" ", "%20") for q in queries]]
        return {
            'platform': 'Twitter',
            'search_type': 'email',
            'query': email,
            'public_search_links': links,
            'note': 'Open links to view live results; official API requires a key.'
        }
    
    async def _search_instagram_email(self, email: str) -> Dict[str, Any]:
        """Search Instagram for email"""
        return {
            'platform': 'Instagram',
            'search_type': 'email',
            'query': email,
            'results': [],
            'note': 'Instagram search requires specialized tools or manual investigation',
            'recommendations': [
                'Check if email username exists as Instagram handle',
                'Search for email in Instagram bio descriptions',
                'Use Instagram username enumeration tools'
            ]
        }
    
    async def _search_linkedin_email(self, email: str) -> Dict[str, Any]:
        """Search LinkedIn: provide public search links and check profile URLs via HEAD lightly."""
        session = await self._get_session()
        username = email.split('@')[0]
        company = email.split('@')[1].split('.')[0]
        candidates = [
            f'https://www.linkedin.com/in/{username}',
            f'https://www.linkedin.com/in/{username.replace(".", "")}',
            f'https://www.linkedin.com/in/{username.replace("_", "")}'
        ]
        verified = []
        for url in candidates[:2]:
            try:
                async with session.head(url) as resp:
                    status = resp.status
                if status == 200:
                    verified.append({'url': url, 'status': 'Exists (HTTP 200)', 'confidence': 'Medium'})
                elif status in (301, 302, 999):
                    verified.append({'url': url, 'status': f'Redirect/Rate limited ({status})', 'confidence': 'Unknown'})
                await asyncio.sleep(0.5)
            except Exception:
                continue
        public_links = {
            'site_search': f'https://www.linkedin.com/search/results/people/?keywords={username}',
            'company_people': f'https://www.linkedin.com/search/results/people/?currentCompany=["{company}"]&keywords={username}'
        }
        return {
            'platform': 'LinkedIn',
            'search_type': 'email',
            'query': email,
            'potential_profiles': candidates,
            'verified_profiles': verified,
            'public_search_links': public_links,
            'note': 'LinkedIn blocks scraping; links provided for live results.'
        }
    
    async def _search_reddit_email(self, email: str) -> Dict[str, Any]:
        """Search Reddit via public JSON endpoints (free)."""
        session = await self._get_session()
        username = email.split('@')[0]
        results: List[Dict[str, Any]] = []
        # 1) Reddit search JSON (no auth; may be rate limited)
        search_url = f'https://www.reddit.com/search.json?q={email}'
        try:
            async with session.get(search_url, headers={'User-Agent': self.ua.random}) as resp:
                if resp.status == 200:
                    data = await resp.json(content_type=None)
                    posts = []
                    for child in (data.get('data', {}).get('children', []) or [])[:5]:
                        d = child.get('data', {})
                        posts.append({'title': d.get('title'), 'subreddit': d.get('subreddit'), 'permalink': f'https://reddit.com{d.get("permalink", "")}'})
                    results.append({'type': 'search', 'url': search_url, 'posts': posts})
                else:
                    results.append({'type': 'search', 'url': search_url, 'status': f'HTTP {resp.status}'})
        except Exception as e:
            results.append({'type': 'search', 'error': str(e), 'url': search_url})
        return {
            'platform': 'Reddit',
            'search_type': 'email',
            'query': email,
            'results': results,
            'search_urls': [
                f'https://www.reddit.com/search/?q={email}',
                f'https://www.reddit.com/user/{username}'
            ]
        }
    
    async def _search_github_email(self, email: str) -> Dict[str, Any]:
        """Search GitHub: live profile HEAD checks and public search links (free)."""
        session = await self._get_session()
        username = email.split('@')[0]
        checks = []
        try:
            url = f'https://github.com/{username}'
            async with session.head(url) as resp:
                if resp.status == 200:
                    checks.append({'type': 'profile_found', 'url': url, 'status': 'HTTP 200'})
                else:
                    checks.append({'type': 'profile_check', 'url': url, 'status': f'HTTP {resp.status}'})
        except Exception as e:
            checks.append({'type': 'profile_check_error', 'url': f'https://github.com/{username}', 'error': str(e)})
        search_links = {
            'commits_by_email': f'https://github.com/search?q={email}&type=commits',
            'issues_by_email': f'https://github.com/search?q={email}&type=issues',
            'users_by_username': f'https://github.com/search?q={username}&type=users'
        }
        return {
            'platform': 'GitHub',
            'search_type': 'email',
            'query': email,
            'results': checks,
            'public_search_links': search_links
        }
    
    async def _search_tiktok_email(self, email: str) -> Dict[str, Any]:
        """Provide TikTok public URLs for live verification (no free API)."""
        username = email.split('@')[0]
        return {
            'platform': 'TikTok',
            'search_type': 'email',
            'query': email,
            'search_urls': [
                f'https://www.tiktok.com/@{username}',
                f'https://www.tiktok.com/@{username.replace(".", "")}'
            ],
            'note': 'Open links to view live results.'
        }
    
    async def _search_facebook_phone(self, phone: str) -> Dict[str, Any]:
        """Search Facebook for phone number"""
        return {
            'platform': 'Facebook',
            'search_type': 'phone',
            'query': phone,
            'results': [],
            'note': 'Facebook phone search heavily restricted',
            'recommendations': [
                'Try Facebook friend finder (if you have an account)',
                'Check if phone is linked to Facebook account recovery',
                'Look for phone number in public Facebook posts'
            ]
        }
    
    async def _search_twitter_phone(self, phone: str) -> Dict[str, Any]:
        """Search Twitter for phone number"""
        return {
            'platform': 'Twitter',
            'search_type': 'phone',
            'query': phone,
            'results': [],
            'note': 'Twitter phone search requires API access',
            'search_suggestions': [
                f'Search tweets containing: "{phone}"',
                'Check Twitter account recovery options',
                'Look for phone in Twitter bio descriptions'
            ]
        }
    
    async def _search_telegram_phone(self, phone: str) -> Dict[str, Any]:
        """Search Telegram for phone number"""
        return {
            'platform': 'Telegram',
            'search_type': 'phone',
            'query': phone,
            'results': [],
            'note': 'Telegram search requires specialized tools',
            'recommendations': [
                'Use Telegram contact discovery (if phone is in contacts)',
                'Check Telegram username directories',
                'Look for phone in Telegram channel descriptions'
            ]
        }
    
    async def _search_whatsapp_phone(self, phone: str) -> Dict[str, Any]:
        """Search WhatsApp for phone number"""
        return {
            'platform': 'WhatsApp',
            'search_type': 'phone',
            'query': phone,
            'results': [],
            'note': 'WhatsApp search limited to contact discovery',
            'recommendations': [
                'Add phone to contacts and check WhatsApp',
                'Look for WhatsApp profile picture and status',
                'Check WhatsApp Business directory if applicable'
            ]
        }
    
    async def close(self):
        """Close the session and release resources."""
        if self.session and not self.session.closed:
            await self.session.close()
        self.session = None
