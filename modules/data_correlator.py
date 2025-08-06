"""
Data Correlation Module
Correlates and links data from different sources
"""

import re
from typing import Dict, List, Any, Set
from datetime import datetime


class DataCorrelator:
    """Data correlation and analysis engine"""
    
    def __init__(self):
        self.correlation_rules = self._initialize_correlation_rules()
    
    def _initialize_correlation_rules(self) -> Dict[str, Any]:
        """Initialize correlation rules and patterns"""
        return {
            'username_patterns': [
                r'([a-zA-Z0-9._-]+)@',  # Email username
                r'/([a-zA-Z0-9._-]+)$',  # URL username
                r'@([a-zA-Z0-9._-]+)',   # Social media handle
            ],
            'name_patterns': [
                r'([A-Z][a-z]+ [A-Z][a-z]+)',  # First Last
                r'([A-Z][a-z]+\s+[A-Z]\.\s+[A-Z][a-z]+)',  # First M. Last
            ],
            'company_patterns': [
                r'@([a-zA-Z0-9.-]+\.[a-zA-Z]{2,})',  # Email domain
                r'([A-Z][a-zA-Z\s&]+(?:Inc|LLC|Corp|Ltd))',  # Company names
            ],
            'location_patterns': [
                r'([A-Z][a-z]+,\s*[A-Z]{2})',  # City, State
                r'([A-Z][a-z]+,\s*[A-Z][a-z]+)',  # City, Country
            ]
        }
    
    async def correlate_data(self, investigation_results: Dict[str, Any]) -> Dict[str, Any]:
        """Main correlation function"""
        correlations = {
            'usernames': {},
            'names': {},
            'companies': {},
            'locations': {},
            'cross_platform_matches': {},
            'timeline': [],
            'confidence_scores': {},
            'relationship_graph': {},
            'summary': {}
        }
        
        # Extract and correlate usernames
        correlations['usernames'] = self._correlate_usernames(investigation_results)
        
        # Extract and correlate names
        correlations['names'] = self._correlate_names(investigation_results)
        
        # Extract and correlate companies
        correlations['companies'] = self._correlate_companies(investigation_results)
        
        # Extract and correlate locations
        correlations['locations'] = self._correlate_locations(investigation_results)
        
        # Find cross-platform matches
        correlations['cross_platform_matches'] = self._find_cross_platform_matches(investigation_results)
        
        # Build timeline
        correlations['timeline'] = self._build_timeline(investigation_results)
        
        # Calculate confidence scores
        correlations['confidence_scores'] = self._calculate_confidence_scores(correlations)
        
        # Build relationship graph
        correlations['relationship_graph'] = self._build_relationship_graph(correlations)
        
        # Generate summary
        correlations['summary'] = self._generate_correlation_summary(correlations)
        
        return correlations
    
    def _correlate_usernames(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Correlate usernames across platforms"""
        usernames = {}
        
        # Extract from email
        target_email = results.get('target_info', {}).get('email')
        if target_email:
            base_username = target_email.split('@')[0]
            usernames[base_username] = {
                'source': 'email',
                'platforms': ['email'],
                'variations': self._generate_username_variations(base_username)
            }
        
        # Extract from social media results
        social_results = results.get('social_media', {})
        for platform, data in social_results.items():
            if isinstance(data, dict):
                potential_usernames = data.get('potential_usernames', [])
                for username in potential_usernames:
                    if username not in usernames:
                        usernames[username] = {
                            'source': 'social_media',
                            'platforms': [platform],
                            'variations': []
                        }
                    else:
                        usernames[username]['platforms'].append(platform)
        
        # Extract from professional platforms
        professional_results = results.get('professional', {})
        for platform, data in professional_results.items():
            if isinstance(data, dict):
                potential_profiles = data.get('potential_profiles', [])
                for profile_url in potential_profiles:
                    username = self._extract_username_from_url(profile_url)
                    if username and username not in usernames:
                        usernames[username] = {
                            'source': 'professional',
                            'platforms': [platform],
                            'variations': []
                        }
                    elif username:
                        usernames[username]['platforms'].append(platform)
        
        return usernames
    
    def _correlate_names(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Correlate names found across sources"""
        names = {
            'full_names': [],
            'first_names': [],
            'last_names': [],
            'nicknames': [],
            'confidence_scores': {}
        }
        
        # Extract names from various sources
        all_text = self._extract_all_text_from_results(results)
        
        for text in all_text:
            # Find full names
            full_name_matches = re.findall(self.correlation_rules['name_patterns'][0], text)
            names['full_names'].extend(full_name_matches)
            
            # Find names with middle initial
            middle_initial_matches = re.findall(self.correlation_rules['name_patterns'][1], text)
            names['full_names'].extend(middle_initial_matches)
        
        # Remove duplicates and calculate confidence
        names['full_names'] = list(set(names['full_names']))
        
        # Extract first and last names
        for full_name in names['full_names']:
            parts = full_name.split()
            if len(parts) >= 2:
                names['first_names'].append(parts[0])
                names['last_names'].append(parts[-1])
        
        names['first_names'] = list(set(names['first_names']))
        names['last_names'] = list(set(names['last_names']))
        
        return names
    
    def _correlate_companies(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Correlate company information"""
        companies = {
            'email_domain_companies': [],
            'mentioned_companies': [],
            'employment_history': [],
            'confidence_scores': {}
        }
        
        # Extract from email domain
        target_email = results.get('target_info', {}).get('email')
        if target_email:
            domain = target_email.split('@')[1]
            company_name = domain.split('.')[0].title()
            companies['email_domain_companies'].append({
                'name': company_name,
                'domain': domain,
                'source': 'email_domain'
            })
        
        # Extract from professional platforms
        professional_results = results.get('professional', {})
        for platform, data in professional_results.items():
            if isinstance(data, dict) and 'company_search' in data:
                company_url = data['company_search']
                company_name = self._extract_company_from_url(company_url)
                if company_name:
                    companies['mentioned_companies'].append({
                        'name': company_name,
                        'source': platform,
                        'url': company_url
                    })
        
        return companies
    
    def _correlate_locations(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Correlate location information"""
        locations = {
            'phone_locations': [],
            'mentioned_locations': [],
            'timezones': [],
            'countries': []
        }
        
        # Extract from phone intelligence
        phone_intel = results.get('phone_intel', {})
        if phone_intel:
            location_info = phone_intel.get('location_info', {})
            if location_info.get('location'):
                locations['phone_locations'].append({
                    'location': location_info['location'],
                    'country': location_info.get('country'),
                    'source': 'phone_analysis'
                })
            
            timezone_info = phone_intel.get('timezone_info', {})
            if timezone_info.get('timezones'):
                locations['timezones'].extend(timezone_info['timezones'])
        
        return locations
    
    def _find_cross_platform_matches(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Find matches across different platforms"""
        matches = {
            'username_matches': {},
            'email_matches': {},
            'phone_matches': {},
            'profile_matches': {}
        }
        
        target_email = results.get('target_info', {}).get('email')
        target_phone = results.get('target_info', {}).get('phone')
        
        if target_email:
            base_username = target_email.split('@')[0]
            
            # Check social media platforms
            social_results = results.get('social_media', {})
            for platform, data in social_results.items():
                if isinstance(data, dict):
                    potential_usernames = data.get('potential_usernames', [])
                    if base_username in potential_usernames:
                        if base_username not in matches['username_matches']:
                            matches['username_matches'][base_username] = []
                        matches['username_matches'][base_username].append(platform)
            
            # Check professional platforms
            professional_results = results.get('professional', {})
            for platform, data in professional_results.items():
                if isinstance(data, dict):
                    potential_profiles = data.get('potential_profiles', [])
                    for profile_url in potential_profiles:
                        if base_username in profile_url:
                            if base_username not in matches['profile_matches']:
                                matches['profile_matches'][base_username] = []
                            matches['profile_matches'][base_username].append({
                                'platform': platform,
                                'url': profile_url
                            })
        
        return matches
    
    def _build_timeline(self, results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Build timeline of findings"""
        timeline = []
        
        # Add investigation start
        timeline.append({
            'timestamp': results.get('timestamp'),
            'event': 'Investigation started',
            'source': 'tracy',
            'details': results.get('target_info', {})
        })
        
        # Add breach dates if available
        breaches = results.get('breaches', {}).get('breaches', [])
        for breach in breaches:
            if isinstance(breach, dict) and breach.get('breach_date'):
                timeline.append({
                    'timestamp': breach['breach_date'],
                    'event': f"Data breach: {breach.get('name', 'Unknown')}",
                    'source': 'breach_database',
                    'details': breach
                })
        
        # Sort timeline by timestamp
        timeline.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
        
        return timeline
    
    def _calculate_confidence_scores(self, correlations: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate confidence scores for correlations"""
        scores = {
            'overall_confidence': 0,
            'username_confidence': 0,
            'identity_confidence': 0,
            'location_confidence': 0
        }
        
        # Username confidence
        username_matches = correlations.get('cross_platform_matches', {}).get('username_matches', {})
        if username_matches:
            max_platforms = max(len(platforms) for platforms in username_matches.values())
            scores['username_confidence'] = min(max_platforms * 20, 100)  # Max 100%
        
        # Identity confidence (based on name correlations)
        names = correlations.get('names', {}).get('full_names', [])
        if names:
            scores['identity_confidence'] = min(len(names) * 30, 100)
        
        # Location confidence
        locations = correlations.get('locations', {})
        location_sources = len([k for k, v in locations.items() if v])
        scores['location_confidence'] = min(location_sources * 25, 100)
        
        # Overall confidence (weighted average)
        scores['overall_confidence'] = (
            scores['username_confidence'] * 0.4 +
            scores['identity_confidence'] * 0.3 +
            scores['location_confidence'] * 0.3
        )
        
        return scores
    
    def _build_relationship_graph(self, correlations: Dict[str, Any]) -> Dict[str, Any]:
        """Build relationship graph for visualization"""
        nodes = []
        edges = []
        
        # Add target nodes
        nodes.append({
            'id': 'target',
            'label': 'Target',
            'type': 'target',
            'size': 30
        })
        
        # Add username nodes
        usernames = correlations.get('usernames', {})
        for username, data in usernames.items():
            nodes.append({
                'id': f'username_{username}',
                'label': username,
                'type': 'username',
                'size': 20,
                'platforms': data.get('platforms', [])
            })
            
            # Connect to target
            edges.append({
                'from': 'target',
                'to': f'username_{username}',
                'label': 'uses_username'
            })
        
        # Add platform nodes
        all_platforms = set()
        for username_data in usernames.values():
            all_platforms.update(username_data.get('platforms', []))
        
        for platform in all_platforms:
            nodes.append({
                'id': f'platform_{platform}',
                'label': platform.title(),
                'type': 'platform',
                'size': 15
            })
            
            # Connect usernames to platforms
            for username, data in usernames.items():
                if platform in data.get('platforms', []):
                    edges.append({
                        'from': f'username_{username}',
                        'to': f'platform_{platform}',
                        'label': 'found_on'
                    })
        
        return {
            'nodes': nodes,
            'edges': edges,
            'layout': 'force-directed'
        }
    
    def _generate_correlation_summary(self, correlations: Dict[str, Any]) -> Dict[str, Any]:
        """Generate correlation summary"""
        summary = {
            'total_usernames_found': len(correlations.get('usernames', {})),
            'total_platforms_found': 0,
            'cross_platform_matches': 0,
            'confidence_level': 'Low',
            'key_findings': [],
            'recommendations': []
        }
        
        # Count platforms
        all_platforms = set()
        usernames = correlations.get('usernames', {})
        for username_data in usernames.values():
            all_platforms.update(username_data.get('platforms', []))
        summary['total_platforms_found'] = len(all_platforms)
        
        # Count cross-platform matches
        username_matches = correlations.get('cross_platform_matches', {}).get('username_matches', {})
        summary['cross_platform_matches'] = len(username_matches)
        
        # Determine confidence level
        overall_confidence = correlations.get('confidence_scores', {}).get('overall_confidence', 0)
        if overall_confidence >= 80:
            summary['confidence_level'] = 'High'
        elif overall_confidence >= 50:
            summary['confidence_level'] = 'Medium'
        else:
            summary['confidence_level'] = 'Low'
        
        # Generate key findings
        if summary['cross_platform_matches'] > 0:
            summary['key_findings'].append(f"Found {summary['cross_platform_matches']} cross-platform username matches")
        
        if summary['total_platforms_found'] > 5:
            summary['key_findings'].append(f"Target has presence on {summary['total_platforms_found']} platforms")
        
        # Generate recommendations
        if summary['confidence_level'] == 'High':
            summary['recommendations'].append("High confidence correlations found - proceed with detailed analysis")
        else:
            summary['recommendations'].append("Low confidence - consider additional data sources")
        
        if summary['cross_platform_matches'] > 0:
            summary['recommendations'].append("Verify cross-platform matches manually")
        
        return summary
    
    def _generate_username_variations(self, username: str) -> List[str]:
        """Generate common username variations"""
        variations = [
            username,
            username.replace('.', ''),
            username.replace('_', ''),
            username.replace('-', ''),
            username.replace('.', '_'),
            username.replace('_', '.'),
            username.lower(),
            username.upper()
        ]
        
        return list(set(variations))
    
    def _extract_username_from_url(self, url: str) -> str:
        """Extract username from profile URL"""
        patterns = [
            r'/([a-zA-Z0-9._-]+)/?$',
            r'/in/([a-zA-Z0-9._-]+)',
            r'/@([a-zA-Z0-9._-]+)',
            r'/user/([a-zA-Z0-9._-]+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        
        return None
    
    def _extract_company_from_url(self, url: str) -> str:
        """Extract company name from URL"""
        patterns = [
            r'/company/([a-zA-Z0-9._-]+)',
            r'/organization/([a-zA-Z0-9._-]+)',
            r'//([a-zA-Z0-9.-]+)\.'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1).replace('-', ' ').title()
        
        return None
    
    def _extract_all_text_from_results(self, results: Dict[str, Any]) -> List[str]:
        """Extract all text content from investigation results"""
        text_content = []
        
        def extract_text_recursive(obj):
            if isinstance(obj, dict):
                for value in obj.values():
                    extract_text_recursive(value)
            elif isinstance(obj, list):
                for item in obj:
                    extract_text_recursive(item)
            elif isinstance(obj, str):
                text_content.append(obj)
        
        extract_text_recursive(results)
        return text_content