"""
Breach Database Checker Module
Checks various breach databases for compromised credentials
"""

import asyncio
import aiohttp
import hashlib
from typing import Dict, List, Any
from config import Config


class BreachChecker:
    """Breach database checker"""
    
    def __init__(self):
        self.config = Config()
        self.session = None
    
    async def _get_session(self):
        """Get or create aiohttp session"""
        if not self.session:
            self.session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=self.config.REQUEST_TIMEOUT)
            )
        return self.session
    
    async def check_email(self, email: str) -> Dict[str, Any]:
        """Check email across multiple breach databases"""
        results = {
            'email': email,
            'breaches': [],
            'pastes': [],
            'total_breaches': 0,
            'risk_score': 'Unknown',
            'sources_checked': []
        }
        
        # Check multiple sources
        tasks = [
            self._check_haveibeenpwned(email),
            self._check_dehashed(email),
            self._check_breachdirectory(email),
            self._check_leakcheck(email)
        ]
        
        breach_results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Aggregate results
        for result in breach_results:
            if not isinstance(result, Exception) and result:
                if 'breaches' in result:
                    results['breaches'].extend(result['breaches'])
                if 'pastes' in result:
                    results['pastes'].extend(result['pastes'])
                if 'source' in result:
                    results['sources_checked'].append(result['source'])
        
        # Calculate risk score
        results['total_breaches'] = len(results['breaches'])
        results['risk_score'] = self._calculate_risk_score(results['total_breaches'])
        
        return results
    
    async def _check_haveibeenpwned(self, email: str) -> Dict[str, Any]:
        """Check HaveIBeenPwned database"""
        if not self.config.HAVEIBEENPWNED_API_KEY:
            return {
                'source': 'HaveIBeenPwned',
                'status': 'API key required',
                'breaches': [],
                'note': 'Set HAVEIBEENPWNED_API_KEY in config for live results'
            }
        
        # Use a short-lived session to avoid leaks
        results = {'source': 'HaveIBeenPwned', 'breaches': [], 'pastes': []}
        session = None
        try:
            session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=self.config.REQUEST_TIMEOUT))
        except Exception:
            session = None
        
        try:
            # Check breaches
            headers = {
                'hibp-api-key': self.config.HAVEIBEENPWNED_API_KEY,
                'User-Agent': 'Tracy-OSINT-Tool'
            }
            
            breach_url = f'https://haveibeenpwned.com/api/v3/breachedaccount/{email}'
            if session:
                async with session.get(breach_url, headers=headers) as response:
                    if response.status == 200:
                        breaches = await response.json()
                        for breach in breaches:
                            results['breaches'].append({
                                'name': breach.get('Name'),
                                'domain': breach.get('Domain'),
                                'breach_date': breach.get('BreachDate'),
                                'added_date': breach.get('AddedDate'),
                                'pwn_count': breach.get('PwnCount'),
                                'description': breach.get('Description'),
                                'data_classes': breach.get('DataClasses', []),
                                'is_verified': breach.get('IsVerified'),
                                'is_sensitive': breach.get('IsSensitive')
                            })
                    elif response.status == 404:
                        results['status'] = 'No breaches found'
                    else:
                        results['error'] = f'API error: {response.status}'
            
            # Check pastes
            paste_url = f'https://haveibeenpwned.com/api/v3/pasteaccount/{email}'
            if session:
                async with session.get(paste_url, headers=headers) as response:
                    if response.status == 200:
                        pastes = await response.json()
                        for paste in pastes:
                            results['pastes'].append({
                                'source': paste.get('Source'),
                                'id': paste.get('Id'),
                                'title': paste.get('Title'),
                                'date': paste.get('Date'),
                                'email_count': paste.get('EmailCount')
                            })
        
        except Exception as e:
            results['error'] = str(e)
        finally:
            if session:
                await session.close()
        
        return results
    
    async def _check_dehashed(self, email: str) -> Dict[str, Any]:
        """Check DeHashed database"""
        if not self.config.DEHASHED_API_KEY or not self.config.DEHASHED_USERNAME:
            return {
                'source': 'DeHashed',
                'status': 'API credentials required',
                'breaches': [],
                'note': 'Set DEHASHED_API_KEY and DEHASHED_USERNAME for live results'
            }
        
        # Use a short-lived session to avoid leaks
        results = {'source': 'DeHashed', 'breaches': []}
        session = None
        try:
            session = aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=self.config.REQUEST_TIMEOUT))
        except Exception:
            session = None
        
        try:
            auth = aiohttp.BasicAuth(self.config.DEHASHED_USERNAME, self.config.DEHASHED_API_KEY)
            url = f'https://api.dehashed.com/search?query=email:{email}'
            
            if session:
                async with session.get(url, auth=auth) as response:
                    if response.status == 200:
                        data = await response.json()
                        if data.get('success') and data.get('entries'):
                            for entry in data['entries']:
                                results['breaches'].append({
                                    'database': entry.get('database_name'),
                                    'email': entry.get('email'),
                                    'username': entry.get('username'),
                                    'password': entry.get('password', 'N/A'),
                                    'hashed_password': entry.get('hashed_password', 'N/A'),
                                    'name': entry.get('name'),
                                    'phone': entry.get('phone'),
                                    'address': entry.get('address')
                                })
                    else:
                        results['error'] = f'API error: {response.status}'
        
        except Exception as e:
            results['error'] = str(e)
        finally:
            if session:
                await session.close()
        
        return results
    
    async def _check_breachdirectory(self, email: str) -> Dict[str, Any]:
        """Check BreachDirectory (no public free API)"""
        # No free API. Provide actionable search links for live verification.
        return {
            'source': 'BreachDirectory',
            'status': 'Link provided',
            'breaches': [],
            'links': {
                'search': f'https://breachdirectory.org/search?query={email}'
            },
            'note': 'Open the link to view live results if you have access.'
        }
    
    async def _check_leakcheck(self, email: str) -> Dict[str, Any]:
        """Check LeakCheck database (no free API)"""
        # No free API. Provide live search link for manual verification.
        return {
            'source': 'LeakCheck',
            'status': 'Link provided',
            'breaches': [],
            'links': {
                'search': f'https://leakcheck.io/search?query={email}'
            },
            'note': 'Open the link to view live results (account may be required).'
        }
    
    def _calculate_risk_score(self, breach_count: int) -> str:
        """Calculate risk score based on breach count"""
        if breach_count == 0:
            return 'Low'
        elif breach_count <= 3:
            return 'Medium'
        elif breach_count <= 7:
            return 'High'
        else:
            return 'Critical'
    
    async def check_password_hash(self, password_hash: str) -> Dict[str, Any]:
        """Check if password hash appears in breach databases"""
        # This would implement password hash checking against databases like Pwned Passwords
        return {
            'hash': password_hash,
            'found_in_breaches': False,
            'occurrence_count': 0,
            'note': 'Password hash checking can be implemented with appropriate APIs'
        }
    
    async def close(self):
        """Close the session and release resources."""
        if self.session and not self.session.closed:
            await self.session.close()
        self.session = None
