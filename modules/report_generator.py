"""
Report Generator Module
Generates various types of investigation reports
"""

import json
import os
from datetime import datetime
from typing import Dict, Any
from jinja2 import Template


class ReportGenerator:
    """Investigation report generator"""
    
    def __init__(self):
        self.templates = self._load_templates()
    
    def _load_templates(self) -> Dict[str, str]:
        """Load report templates"""
        return {
            'html': self._get_html_template(),
            'markdown': self._get_markdown_template(),
            'text': self._get_text_template()
        }
    
    def generate(self, investigation_results: Dict[str, Any], format_type: str = 'html') -> str:
        """Generate investigation report"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if format_type == 'html':
            return self._generate_html_report(investigation_results, timestamp)
        elif format_type == 'markdown':
            return self._generate_markdown_report(investigation_results, timestamp)
        elif format_type == 'text':
            return self._generate_text_report(investigation_results, timestamp)
        elif format_type == 'json':
            return self._generate_json_report(investigation_results, timestamp)
        else:
            raise ValueError(f"Unsupported format: {format_type}")
    
    def _generate_html_report(self, results: Dict[str, Any], timestamp: str) -> str:
        """Generate HTML report"""
        template = Template(self.templates['html'])
        
        # Prepare data for template
        template_data = {
            'timestamp': timestamp,
            'generation_time': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'target_info': results.get('target_info', {}),
            'social_media': results.get('social_media', {}),
            'breaches': results.get('breaches', {}),
            'professional': results.get('professional', {}),
            'phone_intel': results.get('phone_intel', {}),
            'search_results': results.get('search_results', {}),
            'correlations': results.get('correlations', {}),
            'summary': self._generate_summary(results)
        }
        
        html_content = template.render(**template_data)
        filename = f"tracy_report_{timestamp}.html"
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return filename
    
    def _generate_markdown_report(self, results: Dict[str, Any], timestamp: str) -> str:
        """Generate Markdown report"""
        template = Template(self.templates['markdown'])
        
        template_data = {
            'timestamp': timestamp,
            'generation_time': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'target_info': results.get('target_info', {}),
            'summary': self._generate_summary(results),
            'results': results
        }
        
        md_content = template.render(**template_data)
        filename = f"tracy_report_{timestamp}.md"
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(md_content)
        
        return filename
    
    def _generate_text_report(self, results: Dict[str, Any], timestamp: str) -> str:
        """Generate plain text report"""
        template = Template(self.templates['text'])
        
        template_data = {
            'timestamp': timestamp,
            'generation_time': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'target_info': results.get('target_info', {}),
            'summary': self._generate_summary(results)
        }
        
        text_content = template.render(**template_data)
        filename = f"tracy_report_{timestamp}.txt"
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(text_content)
        
        return filename
    
    def _generate_json_report(self, results: Dict[str, Any], timestamp: str) -> str:
        """Generate JSON report"""
        filename = f"tracy_report_{timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, default=str)
        
        return filename
    
    def _generate_summary(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate investigation summary"""
        summary = {
            'target_email': results.get('target_info', {}).get('email'),
            'target_phone': results.get('target_info', {}).get('phone'),
            'platforms_searched': 0,
            'breaches_found': 0,
            'social_media_presence': 0,
            'professional_presence': 0,
            'correlations_found': 0,
            'risk_level': 'Unknown'
        }
        
        # Count platforms searched
        platforms = []
        if results.get('social_media'):
            platforms.extend(results['social_media'].keys())
        if results.get('professional'):
            platforms.extend(results['professional'].keys())
        summary['platforms_searched'] = len(set(platforms))
        
        # Count breaches
        breaches = results.get('breaches', {}).get('breaches', [])
        summary['breaches_found'] = len(breaches)
        
        # Count social media presence
        social_media = results.get('social_media', {})
        summary['social_media_presence'] = len([p for p in social_media.values() if p])
        
        # Count professional presence
        professional = results.get('professional', {})
        summary['professional_presence'] = len([p for p in professional.values() if p])
        
        # Count correlations
        correlations = results.get('correlations', {})
        if correlations:
            summary['correlations_found'] = len(correlations.get('cross_platform_matches', {}).get('username_matches', {}))
        
        # Determine risk level
        if summary['breaches_found'] > 5:
            summary['risk_level'] = 'High'
        elif summary['breaches_found'] > 0:
            summary['risk_level'] = 'Medium'
        else:
            summary['risk_level'] = 'Low'
        
        return summary
    
    def _get_html_template(self) -> str:
        """Get HTML report template"""
        return '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Tracy OSINT Investigation Report</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background-color: #f5f5f5; }
        .container { max-width: 1200px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .header { text-align: center; border-bottom: 2px solid #333; padding-bottom: 20px; margin-bottom: 30px; }
        .section { margin-bottom: 30px; }
        .section h2 { color: #333; border-left: 4px solid #007bff; padding-left: 10px; }
        .target-info { background: #e3f2fd; padding: 15px; border-radius: 5px; margin-bottom: 20px; }
        .summary-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin-bottom: 20px; }
        .summary-card { background: #f8f9fa; padding: 15px; border-radius: 5px; text-align: center; border-left: 4px solid #28a745; }
        .summary-card h3 { margin: 0 0 10px 0; color: #333; }
        .summary-card .number { font-size: 2em; font-weight: bold; color: #007bff; }
        .platform-results { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; }
        .platform-card { background: #fff; border: 1px solid #ddd; border-radius: 5px; padding: 15px; }
        .platform-card h3 { margin-top: 0; color: #007bff; }
        .breach-item { background: #fff3cd; border: 1px solid #ffeaa7; padding: 10px; margin: 10px 0; border-radius: 5px; }
        .breach-item.high-risk { background: #f8d7da; border-color: #f5c6cb; }
        .correlation-item { background: #d1ecf1; border: 1px solid #bee5eb; padding: 10px; margin: 10px 0; border-radius: 5px; }
        .risk-low { color: #28a745; }
        .risk-medium { color: #ffc107; }
        .risk-high { color: #dc3545; }
        .footer { text-align: center; margin-top: 30px; padding-top: 20px; border-top: 1px solid #ddd; color: #666; }
        pre { background: #f8f9fa; padding: 10px; border-radius: 5px; overflow-x: auto; }
        .json-data { max-height: 300px; overflow-y: auto; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔍 Tracy OSINT Investigation Report</h1>
            <p>Generated on {{ generation_time }}</p>
        </div>
        
        <div class="section">
            <h2>🎯 Target Information</h2>
            <div class="target-info">
                {% if target_info.email %}
                <p><strong>📧 Email:</strong> {{ target_info.email }}</p>
                {% endif %}
                {% if target_info.phone %}
                <p><strong>📱 Phone:</strong> {{ target_info.phone }}</p>
                {% endif %}
            </div>
        </div>
        
        <div class="section">
            <h2>📊 Investigation Summary</h2>
            <div class="summary-grid">
                <div class="summary-card">
                    <h3>Platforms Searched</h3>
                    <div class="number">{{ summary.platforms_searched }}</div>
                </div>
                <div class="summary-card">
                    <h3>Breaches Found</h3>
                    <div class="number risk-{{ 'high' if summary.breaches_found > 5 else 'medium' if summary.breaches_found > 0 else 'low' }}">{{ summary.breaches_found }}</div>
                </div>
                <div class="summary-card">
                    <h3>Social Media</h3>
                    <div class="number">{{ summary.social_media_presence }}</div>
                </div>
                <div class="summary-card">
                    <h3>Professional</h3>
                    <div class="number">{{ summary.professional_presence }}</div>
                </div>
            </div>
        </div>
        
        {% if breaches.breaches %}
        <div class="section">
            <h2>🚨 Data Breaches</h2>
            {% for breach in breaches.breaches %}
            <div class="breach-item {{ 'high-risk' if breach.is_sensitive else '' }}">
                <h4>{{ breach.name or 'Unknown Breach' }}</h4>
                <p><strong>Date:</strong> {{ breach.breach_date or 'Unknown' }}</p>
                <p><strong>Domain:</strong> {{ breach.domain or 'Unknown' }}</p>
                {% if breach.data_classes %}
                <p><strong>Compromised Data:</strong> {{ breach.data_classes | join(', ') }}</p>
                {% endif %}
                {% if breach.description %}
                <p><strong>Description:</strong> {{ breach.description }}</p>
                {% endif %}
            </div>
            {% endfor %}
        </div>
        {% endif %}
        
        {% if social_media %}
        <div class="section">
            <h2>📱 Social Media Presence</h2>
            <div class="platform-results">
                {% for platform, data in social_media.items() %}
                <div class="platform-card">
                    <h3>{{ platform.title() }}</h3>
                    {% if data.potential_profiles %}
                    <p><strong>Potential Profiles:</strong></p>
                    <ul>
                        {% for profile in data.potential_profiles %}
                        <li><a href="{{ profile }}" target="_blank">{{ profile }}</a></li>
                        {% endfor %}
                    </ul>
                    {% endif %}
                    {% if data.note %}
                    <p><em>{{ data.note }}</em></p>
                    {% endif %}
                </div>
                {% endfor %}
            </div>
        </div>
        {% endif %}
        
        {% if professional %}
        <div class="section">
            <h2>💼 Professional Presence</h2>
            <div class="platform-results">
                {% for platform, data in professional.items() %}
                <div class="platform-card">
                    <h3>{{ platform.title() }}</h3>
                    {% if data.potential_profiles %}
                    <p><strong>Potential Profiles:</strong></p>
                    <ul>
                        {% for profile in data.potential_profiles %}
                        <li><a href="{{ profile }}" target="_blank">{{ profile }}</a></li>
                        {% endfor %}
                    </ul>
                    {% endif %}
                    {% if data.verified_profiles %}
                    <p><strong>Verified Profiles:</strong></p>
                    <ul>
                        {% for profile in data.verified_profiles %}
                        <li><a href="{{ profile.url }}" target="_blank">{{ profile.url }}</a> - {{ profile.status }}</li>
                        {% endfor %}
                    </ul>
                    {% endif %}
                </div>
                {% endfor %}
            </div>
        </div>
        {% endif %}
        
        {% if correlations.summary %}
        <div class="section">
            <h2>🔗 Data Correlations</h2>
            <div class="correlation-item">
                <h4>Correlation Summary</h4>
                <p><strong>Confidence Level:</strong> <span class="risk-{{ correlations.summary.confidence_level.lower() }}">{{ correlations.summary.confidence_level }}</span></p>
                <p><strong>Cross-platform Matches:</strong> {{ correlations.summary.cross_platform_matches }}</p>
                <p><strong>Total Usernames Found:</strong> {{ correlations.summary.total_usernames_found }}</p>
                {% if correlations.summary.key_findings %}
                <p><strong>Key Findings:</strong></p>
                <ul>
                    {% for finding in correlations.summary.key_findings %}
                    <li>{{ finding }}</li>
                    {% endfor %}
                </ul>
                {% endif %}
            </div>
        </div>
        {% endif %}
        
        <div class="footer">
            <p>Report generated by Tracy OSINT Tool</p>
            <p><em>This report contains information gathered from publicly available sources only.</em></p>
        </div>
    </div>
</body>
</html>
        '''
    
    def _get_markdown_template(self) -> str:
        """Get Markdown report template"""
        return '''
# 🔍 Tracy OSINT Investigation Report

**Generated:** {{ generation_time }}

## 🎯 Target Information

{% if target_info.email -%}
- **📧 Email:** {{ target_info.email }}
{% endif -%}
{% if target_info.phone -%}
- **📱 Phone:** {{ target_info.phone }}
{% endif %}

## 📊 Investigation Summary

- **Platforms Searched:** {{ summary.platforms_searched }}
- **Breaches Found:** {{ summary.breaches_found }}
- **Social Media Presence:** {{ summary.social_media_presence }}
- **Professional Presence:** {{ summary.professional_presence }}
- **Risk Level:** {{ summary.risk_level }}

{% if results.breaches.breaches -%}
## 🚨 Data Breaches

{% for breach in results.breaches.breaches -%}
### {{ breach.name or 'Unknown Breach' }}

- **Date:** {{ breach.breach_date or 'Unknown' }}
- **Domain:** {{ breach.domain or 'Unknown' }}
{% if breach.data_classes -%}
- **Compromised Data:** {{ breach.data_classes | join(', ') }}
{% endif -%}
{% if breach.description -%}
- **Description:** {{ breach.description }}
{% endif %}

{% endfor -%}
{% endif %}

---

*Report generated by Tracy OSINT Tool*
*This report contains information gathered from publicly available sources only.*
        '''
    
    def _get_text_template(self) -> str:
        """Get plain text report template"""
        return '''
TRACY OSINT INVESTIGATION REPORT
===============================

Generated: {{ generation_time }}

TARGET INFORMATION
-----------------
{% if target_info.email -%}
Email: {{ target_info.email }}
{% endif -%}
{% if target_info.phone -%}
Phone: {{ target_info.phone }}
{% endif %}

INVESTIGATION SUMMARY
--------------------
Platforms Searched: {{ summary.platforms_searched }}
Breaches Found: {{ summary.breaches_found }}
Social Media Presence: {{ summary.social_media_presence }}
Professional Presence: {{ summary.professional_presence }}
Risk Level: {{ summary.risk_level }}

---
Report generated by Tracy OSINT Tool
This report contains information gathered from publicly available sources only.
        '''