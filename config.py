import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # API Keys (set these in .env file)
    SHODAN_API_KEY = os.getenv('SHODAN_API_KEY', '')
    TWITTER_BEARER_TOKEN = os.getenv('TWITTER_BEARER_TOKEN', '')
    HAVEIBEENPWNED_API_KEY = os.getenv('HAVEIBEENPWNED_API_KEY', '')
    DEHASHED_API_KEY = os.getenv('DEHASHED_API_KEY', '')
    DEHASHED_USERNAME = os.getenv('DEHASHED_USERNAME', '')
    # Newly added optional keys
    EMAILREP_API_KEY = os.getenv('EMAILREP_API_KEY', '')
    HUNTER_API_KEY = os.getenv('HUNTER_API_KEY', '')
    
    # Search Settings
    MAX_RESULTS_PER_PLATFORM = 50
    REQUEST_TIMEOUT = 30
    RATE_LIMIT_DELAY = 1
    
    # User Agents for web scraping
    USER_AGENTS = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    ]
    
    # Dashboard Settings
    DASH_HOST = '127.0.0.1'
    DASH_PORT = 8050
    DASH_DEBUG = True

    # Feature toggles for integrations
    ENABLE_EMAILREP = os.getenv('ENABLE_EMAILREP', 'true').lower() == 'true'
    ENABLE_HIBP = os.getenv('ENABLE_HIBP', 'true').lower() == 'true'
    ENABLE_HUNTER = os.getenv('ENABLE_HUNTER', 'true').lower() == 'true'
    ENABLE_SOCIALSCAN = os.getenv('ENABLE_SOCIALSCAN', 'true').lower() == 'true'
    ENABLE_DNS_WHOIS = os.getenv('ENABLE_DNS_WHOIS', 'true').lower() == 'true'
    ENABLE_SHERLOCK = os.getenv('ENABLE_SHERLOCK', 'true').lower() == 'true'
