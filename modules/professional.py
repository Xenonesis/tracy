"""
Professional Platform Intelligence Module
Searches professional networks and job portals
"""

import asyncio
import aiohttp
import re
from typing import Dict, List, Any
from fake_useragent import UserAgent
from config import Config


class ProfessionalSearcher:
    """Professional platform searcher"""
    
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
        """Search professional platforms by email"""
        results = {}
        
        tasks = [
            self._search_linkedin(email),
            self._search_github(email),
            self._search_stackoverflow(email),
            self._search_angellist(email),
            self._search_crunchbase(email),
            self._search_behance(email),
            self._search_dribbble(email),
            self._search_kaggle(email)
        ]
        
        platform_results = await asyncio.gather(*tasks, return_exceptions=True)
        
        platforms = ['linkedin', 'github', 'stackoverflow', 'angellist', 
                    'crunchbase', 'behance', 'dribbble', 'kaggle']
        
        for platform, result in zip(platforms, platform_results):
            if not isinstance(result, Exception) and result:
                results[platform] = result
        
        return results
    
    async def _search_linkedin(self, email: str) -> Dict[str, Any]:
        """Search LinkedIn for email"""
        username = email.split('@')[0]
        domain = email.split('@')[1]
        company = domain.split('.')[0]
        
        # Generate potential LinkedIn URLs
        potential_profiles = [
            f'https://linkedin.com/in/{username}',
            f'https://linkedin.com/in/{username.replace(".", "")}',
            f'https://linkedin.com/in/{username.replace("_", "")}',
            f'https://linkedin.com/in/{username.replace("-", "")}',
            f'https://linkedin.com/in/{username}{company}',
            f'https://linkedin.com/in/{username}-{company}'
        ]
        
        session = await self._get_session()
        verified_profiles = []
        
        # Check if profiles exist (basic check)
        for profile_url in potential_profiles[:3]:  # Limit to avoid rate limiting
            try:
                async with session.head(profile_url) as response:
                    if response.status == 200:
                        verified_profiles.append({
                            'url': profile_url,
                            'status': 'Profile exists',
                            'confidence': 'Medium'
                        })
                    elif response.status == 999:  # LinkedIn rate limiting
                        verified_profiles.append({
                            'url': profile_url,
                            'status': 'Rate limited - manual check required',
                            'confidence': 'Unknown'
                        })
                
                await asyncio.sleep(1)  # Rate limiting
            
            except Exception as e:
                continue
        
        return {
            'platform': 'LinkedIn',
            'search_type': 'email',
            'email': email,
            'potential_profiles': potential_profiles,
            'verified_profiles': verified_profiles,
            'company_search': f'https://linkedin.com/company/{company}',
            'search_suggestions': [
                f'Search LinkedIn for "{username}"',
                f'Look for employees at {company}',
                f'Check LinkedIn Sales Navigator',
                'Use LinkedIn email finder tools'
            ],
            'note': 'LinkedIn has strict anti-scraping measures'
        }
    
    async def _search_github(self, email: str) -> Dict[str, Any]:
        """Search GitHub for email"""
        username = email.split('@')[0]
        session = await self._get_session()
        
        results = {
            'platform': 'GitHub',
            'search_type': 'email',
            'email': email,
            'profiles': [],
            'repositories': [],
            'commits': []
        }
        
        # Check if username exists as GitHub profile
        github_profiles = [
            username,
            username.replace('.', ''),
            username.replace('_', '-'),
            username.replace('-', '')
        ]
        
        for profile in github_profiles[:2]:  # Limit checks
            try:
                profile_url = f'https://github.com/{profile}'
                async with session.get(profile_url) as response:
                    if response.status == 200:
                        results['profiles'].append({
                            'username': profile,
                            'url': profile_url,
                            'status': 'Profile exists',
                            'needs_verification': True
                        })
                
                await asyncio.sleep(1)
            
            except Exception:
                continue
        
        # GitHub API searches (would require API key for full implementation)
        results['api_searches'] = [
            f'Search commits by email: {email}',
            f'Search repositories by email: {email}',
            f'Search issues by email: {email}',
            f'Search pull requests by email: {email}'
        ]
        
        results['manual_searches'] = [
            f'https://github.com/search?q={email}&type=commits',
            f'https://github.com/search?q={email}&type=issues',
            f'https://github.com/search?q={username}&type=users'
        ]
        
        return results
    
    async def _search_stackoverflow(self, email: str) -> Dict[str, Any]:
        """Search Stack Overflow for email"""
        username = email.split('@')[0]
        
        return {
            'platform': 'Stack Overflow',
            'search_type': 'email',
            'email': email,
            'potential_profiles': [
                f'https://stackoverflow.com/users/{username}',
                f'https://stackoverflow.com/search?q=user:{username}'
            ],
            'search_urls': [
                f'https://stackoverflow.com/search?q={email}',
                f'https://stackoverflow.com/search?q={username}'
            ],
            'related_sites': [
                f'https://stackexchange.com/search?q={email}',
                f'https://superuser.com/search?q={email}',
                f'https://serverfault.com/search?q={email}'
            ],
            'note': 'Stack Overflow search requires manual verification'
        }
    
    async def _search_angellist(self, email: str) -> Dict[str, Any]:
        """Search AngelList for email"""
        username = email.split('@')[0]
        
        return {
            'platform': 'AngelList (Wellfound)',
            'search_type': 'email',
            'email': email,
            'potential_profiles': [
                f'https://wellfound.com/{username}',
                f'https://angel.co/{username}'
            ],
            'search_suggestions': [
                f'Search for "{username}" on Wellfound',
                f'Look for startup employees with email domain',
                'Check investor profiles'
            ],
            'note': 'AngelList rebranded to Wellfound'
        }
    
    async def _search_crunchbase(self, email: str) -> Dict[str, Any]:
        """Search Crunchbase for email"""
        domain = email.split('@')[1]
        company = domain.split('.')[0]
        
        return {
            'platform': 'Crunchbase',
            'search_type': 'email',
            'email': email,
            'company_search': f'https://crunchbase.com/organization/{company}',
            'search_suggestions': [
                f'Search for company: {company}',
                f'Look for executives with email domain',
                'Check funding information',
                'Look for founder profiles'
            ],
            'note': 'Crunchbase requires subscription for detailed info'
        }
    
    async def _search_behance(self, email: str) -> Dict[str, Any]:
        """Search Behance for email"""
        username = email.split('@')[0]
        
        return {
            'platform': 'Behance',
            'search_type': 'email',
            'email': email,
            'potential_profiles': [
                f'https://behance.net/{username}',
                f'https://behance.net/{username.replace(".", "")}',
                f'https://behance.net/{username.replace("_", "")}'
            ],
            'search_url': f'https://behance.net/search/users?search={username}',
            'note': 'Behance is Adobe\'s creative portfolio platform'
        }
    
    async def _search_dribbble(self, email: str) -> Dict[str, Any]:
        """Search Dribbble for email"""
        username = email.split('@')[0]
        
        return {
            'platform': 'Dribbble',
            'search_type': 'email',
            'email': email,
            'potential_profiles': [
                f'https://dribbble.com/{username}',
                f'https://dribbble.com/{username.replace(".", "")}',
                f'https://dribbble.com/{username.replace("_", "")}'
            ],
            'search_url': f'https://dribbble.com/search/{username}',
            'note': 'Dribbble is a design portfolio platform'
        }
    
    async def _search_kaggle(self, email: str) -> Dict[str, Any]:
        """Search Kaggle for email"""
        username = email.split('@')[0]
        
        return {
            'platform': 'Kaggle',
            'search_type': 'email',
            'email': email,
            'potential_profiles': [
                f'https://kaggle.com/{username}',
                f'https://kaggle.com/{username.replace(".", "")}',
                f'https://kaggle.com/{username.replace("_", "")}'
            ],
            'search_suggestions': [
                f'Search Kaggle datasets by {username}',
                f'Look for competition participation',
                'Check notebook publications'
            ],
            'note': 'Kaggle is a data science competition platform'
        }
    
    async def search_by_name(self, full_name: str, company: str = None) -> Dict[str, Any]:
        """Search professional platforms by full name"""
        results = {
            'name': full_name,
            'company': company,
            'linkedin_searches': [],
            'github_searches': [],
            'general_searches': []
        }
        
        # Generate LinkedIn search URLs
        name_variations = [
            full_name,
            full_name.replace(' ', '-'),
            full_name.replace(' ', ''),
            full_name.lower().replace(' ', '-')
        ]
        
        for name in name_variations:
            results['linkedin_searches'].append(f'https://linkedin.com/in/{name}')
        
        if company:
            results['linkedin_searches'].append(
                f'https://linkedin.com/search/results/people/?keywords={full_name}&currentCompany=["{company}"]'
            )
        
        return results
    
    async def close(self):
        """Close the session"""
        if self.session:
            await self.session.close()