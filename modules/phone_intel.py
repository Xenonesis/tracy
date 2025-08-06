"""
Phone Intelligence Module
Analyzes phone numbers for carrier, location, and other intelligence
"""

import asyncio
import aiohttp
import phonenumbers
from phonenumbers import geocoder, carrier, timezone
from typing import Dict, List, Any
from config import Config


class PhoneIntelligence:
    """Phone number intelligence analyzer"""
    
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
    
    async def analyze_phone(self, phone: str) -> Dict[str, Any]:
        """Comprehensive phone number analysis"""
        results = {
            'phone_number': phone,
            'basic_info': {},
            'carrier_info': {},
            'location_info': {},
            'timezone_info': {},
            'validation': {},
            'osint_sources': {},
            'risk_assessment': {}
        }
        
        try:
            # Parse phone number
            parsed_phone = phonenumbers.parse(phone, None)
            
            # Basic validation and info
            results['validation'] = {
                'is_valid': phonenumbers.is_valid_number(parsed_phone),
                'is_possible': phonenumbers.is_possible_number(parsed_phone),
                'number_type': self._get_number_type(parsed_phone),
                'formatted_e164': phonenumbers.format_number(parsed_phone, phonenumbers.PhoneNumberFormat.E164),
                'formatted_international': phonenumbers.format_number(parsed_phone, phonenumbers.PhoneNumberFormat.INTERNATIONAL),
                'formatted_national': phonenumbers.format_number(parsed_phone, phonenumbers.PhoneNumberFormat.NATIONAL)
            }
            
            # Basic info
            results['basic_info'] = {
                'country_code': parsed_phone.country_code,
                'national_number': parsed_phone.national_number,
                'region_code': phonenumbers.region_code_for_number(parsed_phone)
            }
            
            # Carrier information
            carrier_name = carrier.name_for_number(parsed_phone, 'en')
            results['carrier_info'] = {
                'carrier_name': carrier_name if carrier_name else 'Unknown',
                'note': 'Carrier info may be limited for some regions'
            }
            
            # Location information
            location = geocoder.description_for_number(parsed_phone, 'en')
            results['location_info'] = {
                'location': location if location else 'Unknown',
                'country': phonenumbers.region_code_for_number(parsed_phone),
                'note': 'Location is approximate and based on area code'
            }
            
            # Timezone information
            timezones = timezone.time_zones_for_number(parsed_phone)
            results['timezone_info'] = {
                'timezones': list(timezones) if timezones else [],
                'note': 'Multiple timezones possible for large regions'
            }
            
            # OSINT sources
            results['osint_sources'] = await self._get_osint_sources(phone, parsed_phone)
            
            # Risk assessment
            results['risk_assessment'] = self._assess_risk(parsed_phone, results)
            
        except phonenumbers.NumberParseException as e:
            results['error'] = f'Phone parsing error: {str(e)}'
            results['validation']['is_valid'] = False
        
        return results
    
    def _get_number_type(self, parsed_phone) -> str:
        """Get the type of phone number"""
        number_type = phonenumbers.number_type(parsed_phone)
        
        type_mapping = {
            phonenumbers.PhoneNumberType.FIXED_LINE: 'Fixed Line',
            phonenumbers.PhoneNumberType.MOBILE: 'Mobile',
            phonenumbers.PhoneNumberType.FIXED_LINE_OR_MOBILE: 'Fixed Line or Mobile',
            phonenumbers.PhoneNumberType.TOLL_FREE: 'Toll Free',
            phonenumbers.PhoneNumberType.PREMIUM_RATE: 'Premium Rate',
            phonenumbers.PhoneNumberType.SHARED_COST: 'Shared Cost',
            phonenumbers.PhoneNumberType.VOIP: 'VoIP',
            phonenumbers.PhoneNumberType.PERSONAL_NUMBER: 'Personal Number',
            phonenumbers.PhoneNumberType.PAGER: 'Pager',
            phonenumbers.PhoneNumberType.UAN: 'Universal Access Number',
            phonenumbers.PhoneNumberType.VOICEMAIL: 'Voicemail',
            phonenumbers.PhoneNumberType.UNKNOWN: 'Unknown'
        }
        
        return type_mapping.get(number_type, 'Unknown')
    
    async def _get_osint_sources(self, phone: str, parsed_phone) -> Dict[str, Any]:
        """Get OSINT sources for phone number investigation"""
        sources = {
            'truecaller': {
                'url': f'https://truecaller.com/search/us/{phone}',
                'description': 'Caller ID and spam detection',
                'note': 'Requires manual search or API access'
            },
            'whitepages': {
                'url': f'https://whitepages.com/phone/{phone}',
                'description': 'Phone directory and reverse lookup',
                'note': 'May require subscription for full details'
            },
            'spokeo': {
                'url': f'https://spokeo.com/phone-search/{phone}',
                'description': 'People search and background info',
                'note': 'Paid service'
            },
            'beenverified': {
                'url': f'https://beenverified.com/phone/{phone}',
                'description': 'Background check service',
                'note': 'Paid service'
            },
            'social_media_searches': [
                f'Facebook: Search for phone number in account recovery',
                f'WhatsApp: Add to contacts and check profile',
                f'Telegram: Search by phone number',
                f'Signal: Check if number is registered'
            ],
            'spam_databases': [
                'Should I Answer',
                'Truecaller Spam List',
                'Hiya Spam Database',
                'RoboKiller Database'
            ]
        }
        
        # Add country-specific sources
        country_code = phonenumbers.region_code_for_number(parsed_phone)
        if country_code:
            sources['country_specific'] = self._get_country_specific_sources(country_code, phone)
        
        return sources
    
    def _get_country_specific_sources(self, country_code: str, phone: str) -> Dict[str, Any]:
        """Get country-specific OSINT sources"""
        country_sources = {
            'US': {
                'fastpeoplesearch': f'https://fastpeoplesearch.com/phone/{phone}',
                'intelius': f'https://intelius.com/phone-search/{phone}',
                'peoplefinder': f'https://peoplefinder.com/phone/{phone}',
                'zabasearch': 'https://zabasearch.com'
            },
            'GB': {
                'bt_phonebook': 'https://thephonebook.bt.com',
                'uk_phonebook': 'https://ukphonebook.com',
                '192': 'https://192.com'
            },
            'CA': {
                'canada411': 'https://canada411.ca',
                'whitepages_ca': 'https://whitepages.ca'
            },
            'AU': {
                'whitepages_au': 'https://whitepages.com.au',
                'yellowpages_au': 'https://yellowpages.com.au'
            }
        }
        
        return country_sources.get(country_code, {})
    
    def _assess_risk(self, parsed_phone, results: Dict[str, Any]) -> Dict[str, Any]:
        """Assess risk factors for the phone number"""
        risk_factors = []
        risk_score = 0
        
        # Check number type
        number_type = results['validation']['number_type']
        if number_type in ['VoIP', 'Unknown']:
            risk_factors.append('VoIP or unknown number type')
            risk_score += 2
        elif number_type == 'Premium Rate':
            risk_factors.append('Premium rate number')
            risk_score += 3
        
        # Check if number is valid
        if not results['validation']['is_valid']:
            risk_factors.append('Invalid phone number')
            risk_score += 5
        
        # Check carrier info
        if results['carrier_info']['carrier_name'] == 'Unknown':
            risk_factors.append('Unknown carrier')
            risk_score += 1
        
        # Check location info
        if results['location_info']['location'] == 'Unknown':
            risk_factors.append('Unknown location')
            risk_score += 1
        
        # Determine risk level
        if risk_score == 0:
            risk_level = 'Low'
        elif risk_score <= 3:
            risk_level = 'Medium'
        elif risk_score <= 6:
            risk_level = 'High'
        else:
            risk_level = 'Very High'
        
        return {
            'risk_score': risk_score,
            'risk_level': risk_level,
            'risk_factors': risk_factors,
            'recommendations': self._get_risk_recommendations(risk_level, risk_factors)
        }
    
    def _get_risk_recommendations(self, risk_level: str, risk_factors: List[str]) -> List[str]:
        """Get recommendations based on risk assessment"""
        recommendations = []
        
        if 'VoIP or unknown number type' in risk_factors:
            recommendations.append('Verify identity through alternative means')
            recommendations.append('Be cautious of potential spoofing')
        
        if 'Invalid phone number' in risk_factors:
            recommendations.append('Double-check number format and validity')
            recommendations.append('May be a fake or spoofed number')
        
        if 'Unknown carrier' in risk_factors:
            recommendations.append('Research carrier information manually')
            recommendations.append('Check with telecom databases')
        
        if risk_level in ['High', 'Very High']:
            recommendations.append('Exercise extreme caution')
            recommendations.append('Consider blocking or reporting number')
        
        return recommendations
    
    async def bulk_analyze(self, phone_numbers: List[str]) -> Dict[str, Any]:
        """Analyze multiple phone numbers"""
        results = {
            'total_numbers': len(phone_numbers),
            'analysis_results': {},
            'summary': {
                'valid_numbers': 0,
                'invalid_numbers': 0,
                'high_risk_numbers': 0,
                'countries': set(),
                'carriers': set()
            }
        }
        
        # Analyze each number
        for phone in phone_numbers:
            analysis = await self.analyze_phone(phone)
            results['analysis_results'][phone] = analysis
            
            # Update summary
            if analysis.get('validation', {}).get('is_valid'):
                results['summary']['valid_numbers'] += 1
                
                # Add country
                country = analysis.get('basic_info', {}).get('region_code')
                if country:
                    results['summary']['countries'].add(country)
                
                # Add carrier
                carrier_name = analysis.get('carrier_info', {}).get('carrier_name')
                if carrier_name and carrier_name != 'Unknown':
                    results['summary']['carriers'].add(carrier_name)
                
                # Check risk
                risk_level = analysis.get('risk_assessment', {}).get('risk_level')
                if risk_level in ['High', 'Very High']:
                    results['summary']['high_risk_numbers'] += 1
            else:
                results['summary']['invalid_numbers'] += 1
        
        # Convert sets to lists for JSON serialization
        results['summary']['countries'] = list(results['summary']['countries'])
        results['summary']['carriers'] = list(results['summary']['carriers'])
        
        return results
    
    async def close(self):
        """Close the session and release resources."""
        if self.session and not self.session.closed:
            await self.session.close()
        self.session = None
