"""
Interactive Dashboard Module
Provides interactive visualizations of investigation results using Dash
"""

import json
import os
import dash
from dash import dcc, html, Input, Output, dash_table
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import networkx as nx
from datetime import datetime
from typing import Dict, Any

from config import Config


class InteractiveDashboard:
    """Interactive dashboard for visualizing investigation results"""
    
    def __init__(self, investigation_data: Dict[str, Any] = None):
        self.config = Config()
        self.investigation_data = investigation_data or {}
        self.app = None
    
    def create_app(self) -> dash.Dash:
        """Create Dash application"""
        # Create Dash app
        self.app = dash.Dash(
            __name__,
            external_stylesheets=[
                'https://stackpath.bootstrapcdn.com/bootstrap/4.5.2/css/bootstrap.min.css'
            ],
            suppress_callback_exceptions=True
        )
        
        # Set up layout
        self.app.layout = self._create_layout()
        
        # Set up callbacks
        self._setup_callbacks()
        
        return self.app
    
    def _create_layout(self) -> html.Div:
        """Create dashboard layout"""
        return html.Div([
            # Store data in hidden div
            dcc.Store(id='investigation-data', data=self.investigation_data),
            
            # Navigation bar
            html.Nav([
                html.Div([
                    html.H2("🔍 Tracy OSINT Dashboard", className="text-white"),
                    html.P("Interactive Digital Footprint Analysis", className="text-white-50")
                ], className="container"),
            ], className="navbar navbar-dark bg-dark mb-4"),
            
            # Main content
            html.Div([
                # Summary cards
                html.Div([
                    html.Div([
                        html.Div([
                            html.H4("Platforms Searched", className="text-white"),
                            html.H3(id="platforms-count", className="text-white"),
                        ], className="card-body"),
                    ], className="card bg-primary"),
                ], className="col-md-3 mb-4"),
                
                html.Div([
                    html.Div([
                        html.Div([
                            html.H4("Breaches Found", className="text-white"),
                            html.H3(id="breaches-count", className="text-white"),
                        ], className="card-body"),
                    ], className="card bg-danger"),
                ], className="col-md-3 mb-4"),
                
                html.Div([
                    html.Div([
                        html.Div([
                            html.H4("Social Media", className="text-white"),
                            html.H3(id="social-media-count", className="text-white"),
                        ], className="card-body"),
                    ], className="card bg-info"),
                ], className="col-md-3 mb-4"),
                
                html.Div([
                    html.Div([
                        html.Div([
                            html.H4("Professional", className="text-white"),
                            html.H3(id="professional-count", className="text-white"),
                        ], className="card-body"),
                    ], className="card bg-success"),
                ], className="col-md-3 mb-4"),
            ], className="row mb-4"),
            
            # Controls row
            html.Div([
                html.Div([
                    html.Label("Enter Email", className="form-label"),
                    dcc.Input(id="email-input", type="text", inputMode="email", placeholder="name@example.com",
                              className="form-control", debounce=True, value="")
                ], className="col-md-4 mb-3"),
                html.Div([
                    html.Label("Run Investigation", className="form-label d-block"),
                    html.Button("Search", id="run-search", n_clicks=0, className="btn btn-primary"),
                    html.Span(id="search-status", className="ms-3 text-muted")
                ], className="col-md-4 mb-3"),
                dcc.Store(id="run-token", data=None)
            ], className="row mb-4"),
            
            # Tabs
            dcc.Tabs(id="dashboard-tabs", value='summary-tab', children=[
                dcc.Tab(label='Summary', value='summary-tab', children=[
                    html.Div([
                        html.Div([
                            html.H3("Investigation Summary", className="mb-4"),
                            html.Div(id="summary-content"),
                        ], className="col-12"),
                    ], className="row"),
                ]),
                
                dcc.Tab(label='Data Breaches', value='breaches-tab', children=[
                    html.Div([
                        html.Div([
                            html.H3("Data Breaches", className="mb-4"),
                            html.Div(id="breaches-content"),
                        ], className="col-12"),
                    ], className="row"),
                ]),
                
                dcc.Tab(label='Social Media', value='social-tab', children=[
                    html.Div([
                        html.Div([
                            html.H3("Social Media Presence", className="mb-4"),
                            html.Div(id="social-content"),
                        ], className="col-12"),
                    ], className="row"),
                ]),
                
                dcc.Tab(label='Professional', value='professional-tab', children=[
                    html.Div([
                        html.Div([
                            html.H3("Professional Presence", className="mb-4"),
                            html.Div(id="professional-content"),
                        ], className="col-12"),
                    ], className="row"),
                ]),
                
                dcc.Tab(label='Correlations', value='correlations-tab', children=[
                    html.Div([
                        html.Div([
                            html.H3("Data Correlations", className="mb-4"),
                            html.Div(id="correlations-content"),
                        ], className="col-12"),
                    ], className="row"),
                ]),
                
                dcc.Tab(label='Network Graph', value='network-tab', children=[
                    html.Div([
                        html.Div([
                            html.H3("Network Visualization", className="mb-4"),
                            dcc.Graph(id="network-graph"),
                        ], className="col-12"),
                    ], className="row"),
                ]),
                
                dcc.Tab(label='Raw Data', value='raw-tab', children=[
                    html.Div([
                        html.Div([
                            html.H3("Raw Investigation Data", className="mb-4"),
                            html.Div(id="raw-data-content"),
                        ], className="col-12"),
                    ], className="row"),
                ]),
            ]),
            
            # Footer
            html.Footer([
                html.Div([
                    html.P("Tracy OSINT Dashboard", className="text-muted"),
                    html.P(id="timestamp-display", className="text-muted"),
                ], className="container"),
            ], className="footer mt-5 py-3 bg-light"),
        ], className="container-fluid")
    
    def _setup_callbacks(self):
        """Set up Dash callbacks"""
        if not self.app:
            return
        
        @self.app.callback(
            [Output('platforms-count', 'children'),
             Output('breaches-count', 'children'),
             Output('social-media-count', 'children'),
             Output('professional-count', 'children'),
             Output('timestamp-display', 'children')],
            [Input('investigation-data', 'data')]
        )
        def update_summary_cards(data):
            if not data:
                return "0", "0", "0", "0", "No data loaded"
            
            # Count platforms
            platforms = set()
            if data.get('social_media'):
                platforms.update(data['social_media'].keys())
            if data.get('professional'):
                platforms.update(data['professional'].keys())
            platforms_count = len(platforms)
            
            # Count breaches
            breaches_count = len(data.get('breaches', {}).get('breaches', []))
            
            # Count social media
            social_count = len([p for p in data.get('social_media', {}).values() if p])
            
            # Count professional
            professional_count = len([p for p in data.get('professional', {}).values() if p])
            
            # Timestamp
            timestamp = data.get('timestamp', 'Unknown')
            
            return (
                str(platforms_count),
                str(breaches_count),
                str(social_count),
                str(professional_count),
                f"Data generated: {timestamp}"
            )
        
        @self.app.callback(
            Output('investigation-data', 'data'),
            [Input('run-search', 'n_clicks')],
            [dash.dependencies.State('email-input', 'value'),
             dash.dependencies.State('investigation-data', 'data')]
        )
        def run_investigation(n_clicks, email_value, current_data):
            # Normalize and validate
            email_value = (email_value or "").strip()
            if not n_clicks or not email_value:
                return current_data
            # Basic client-side email sanity check to reduce invalid calls
            if "@" not in email_value or "." not in email_value.split("@")[-1]:
                return {'error': 'Invalid email format', 'target_info': {'email': email_value}, 'timestamp': datetime.now().isoformat()}
            try:
                import asyncio
                from tracy import Tracy
                t = Tracy()
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                results = loop.run_until_complete(t.investigate(email=email_value))
                loop.run_until_complete(asyncio.sleep(0))  # allow pending tasks to settle
                # Ensure aiohttp sessions are closed in modules using Tracy
                try:
                    loop.run_until_complete(asyncio.sleep(0))
                finally:
                    loop.close()
                t.results = results
                t.save_results()
                return results
            except Exception as e:
                return {
                    'error': f'Investigation failed: {e}',
                    'target_info': {'email': email_value},
                    'timestamp': datetime.now().isoformat()
                }
        
        @self.app.callback(
            Output('search-status', 'children'),
            [Input('investigation-data', 'data')]
        )
        def update_search_status(data):
            if not data:
                return ""
            if 'error' in data:
                return f"❌ {data.get('error')}"
            ti = data.get('target_info', {})
            if ti.get('email'):
                return f"✅ Loaded results for {ti.get('email')}"
            return ""
        
        @self.app.callback(
            Output('summary-content', 'children'),
            [Input('investigation-data', 'data')]
        )
        def update_summary_content(data):
            if not data:
                return html.P("No investigation data available.")
            
            target_info = data.get('target_info', {})
            correlations = data.get('correlations', {})
            
            return html.Div([
                html.H4("Target Information", className="mb-3"),
                html.Ul([
                    html.Li(f"📧 Email: {target_info.get('email', 'Not provided')}"),
                    html.Li(f"📱 Phone: {target_info.get('phone', 'Not provided')}")
                ], className="list-group mb-4"),
                
                html.H4("Investigation Overview", className="mb-3"),
                html.Ul([
                    html.Li(f"Platforms searched: {len(set().union(data.get('social_media', {}).keys(), data.get('professional', {}).keys()))}"),
                    html.Li(f"Breaches found: {len(data.get('breaches', {}).get('breaches', []))}"),
                    html.Li(f"Social media profiles: {len([p for p in data.get('social_media', {}).values() if p])}"),
                    html.Li(f"Professional profiles: {len([p for p in data.get('professional', {}).values() if p])}"),
                    html.Li(f"Correlations found: {len(correlations.get('cross_platform_matches', {}).get('username_matches', {})) if correlations else 0}")
                ], className="list-group mb-4"),
            ])
        
        @self.app.callback(
            Output('breaches-content', 'children'),
            [Input('investigation-data', 'data')]
        )
        def update_breaches_content(data):
            if not data or not data.get('breaches', {}).get('breaches'):
                return html.P("No data breaches found.")
            
            breaches = data['breaches']['breaches']
            
            # Create breach table
            breach_data = []
            for breach in breaches:
                breach_data.append({
                    'Name': breach.get('name', 'Unknown'),
                    'Date': breach.get('breach_date', 'Unknown'),
                    'Domain': breach.get('domain', 'Unknown'),
                    'Compromised Data': ', '.join(breach.get('data_classes', [])),
                    'Description': breach.get('description', 'No description available')[:100] + '...' if breach.get('description') else 'No description'
                })
            
            df = pd.DataFrame(breach_data)
            
            return html.Div([
                html.H4(f"Found {len(breaches)} Data Breaches", className="mb-3"),
                dash_table.DataTable(
                    data=df.to_dict('records'),
                    columns=[{"name": i, "id": i} for i in df.columns],
                    page_size=10,
                    style_table={'overflowX': 'auto'},
                    style_cell={
                        'textAlign': 'left',
                        'padding': '10px'
                    },
                    style_header={
                        'backgroundColor': 'rgb(230, 230, 230)',
                        'fontWeight': 'bold'
                    }
                )
            ])
        
        @self.app.callback(
            Output('social-content', 'children'),
            [Input('investigation-data', 'data')]
        )
        def update_social_content(data):
            if not data or not data.get('social_media'):
                return html.P("No social media data found.")
            
            social_data = data['social_media']
            
            cards = []
            for platform, info in social_data.items():
                if info:
                    cards.append(
                        html.Div([
                            html.H5(platform.title(), className="card-title"),
                            html.P(f"Potential profiles: {len(info.get('potential_profiles', []))}", className="card-text"),
                            html.Ul([
                                html.Li(html.A(profile, href=profile, target="_blank"))
                                for profile in info.get('potential_profiles', [])[:5]
                            ], className="list-unstyled"),
                        ], className="card mb-3")
                    )
            
            if not cards:
                return html.P("No social media profiles found.")
            
            return html.Div([
                html.H4(f"Social Media Analysis", className="mb-3"),
                html.Div(cards, className="row")
            ])
        
        @self.app.callback(
            Output('professional-content', 'children'),
            [Input('investigation-data', 'data')]
        )
        def update_professional_content(data):
            if not data or not data.get('professional'):
                return html.P("No professional data found.")
            
            professional_data = data['professional']
            
            cards = []
            for platform, info in professional_data.items():
                if info:
                    cards.append(
                        html.Div([
                            html.H5(platform.title(), className="card-title"),
                            html.P(f"Potential profiles: {len(info.get('potential_profiles', []))}", className="card-text"),
                            html.P(f"Verified profiles: {len(info.get('verified_profiles', []))}", className="card-text"),
                        ], className="card mb-3")
                    )
            
            if not cards:
                return html.P("No professional profiles found.")
            
            return html.Div([
                html.H4(f"Professional Presence", className="mb-3"),
                html.Div(cards, className="row")
            ])
        
        @self.app.callback(
            Output('correlations-content', 'children'),
            [Input('investigation-data', 'data')]
        )
        def update_correlations_content(data):
            if not data or not data.get('correlations'):
                return html.P("No correlations found.")
            
            correlations = data['correlations']
            summary = correlations.get('summary', {})
            
            return html.Div([
                html.H4("Data Correlations", className="mb-3"),
                html.Ul([
                    html.Li(f"Confidence Level: {summary.get('confidence_level', 'Unknown')}"),
                    html.Li(f"Cross-platform Matches: {summary.get('cross_platform_matches', 'Unknown')}"),
                    html.Li(f"Total Usernames Found: {summary.get('total_usernames_found', 'Unknown')}")
                ], className="list-group mb-4"),
                
                html.H5("Key Findings", className="mb-3"),
                html.Ul([
                    html.Li(finding) for finding in summary.get('key_findings', [])
                ], className="list-group"),
            ])
        
        @self.app.callback(
            Output('network-graph', 'figure'),
            [Input('investigation-data', 'data')]
        )
        def update_network_graph(data):
            if not data:
                return go.Figure()
            
            # Create network graph
            G = nx.Graph()
            
            # Add target node
            target_email = data.get('target_info', {}).get('email', 'target')
            target_phone = data.get('target_info', {}).get('phone', '')
            target_label = f"Target\n{target_email}"
            if target_phone:
                target_label += f"\n{target_phone}"
            
            G.add_node('target', label=target_label, size=20, color='red')
            
            # Add social media nodes
            if data.get('social_media'):
                for platform, info in data['social_media'].items():
                    if info and info.get('potential_profiles'):
                        node_id = f"social_{platform}"
                        G.add_node(node_id, label=platform.title(), size=15, color='blue')
                        G.add_edge('target', node_id)
            
            # Add professional nodes
            if data.get('professional'):
                for platform, info in data['professional'].items():
                    if info:
                        node_id = f"professional_{platform}"
                        G.add_node(node_id, label=platform.title(), size=15, color='green')
                        G.add_edge('target', node_id)
            
            # Add breach nodes
            if data.get('breaches', {}).get('breaches'):
                for i, breach in enumerate(data['breaches']['breaches'][:5]):  # Limit to first 5
                    node_id = f"breach_{i}"
                    G.add_node(node_id, label=breach.get('name', 'Unknown Breach'), size=10, color='orange')
                    G.add_edge('target', node_id)
            
            # Create plotly figure
            pos = nx.spring_layout(G)
            
            # Extract node positions
            node_x = [pos[node][0] for node in G.nodes()]
            node_y = [pos[node][1] for node in G.nodes()]
            
            # Extract node attributes
            node_labels = [G.nodes[node]['label'] for node in G.nodes()]
            node_sizes = [G.nodes[node]['size'] * 5 for node in G.nodes()]
            node_colors = [G.nodes[node]['color'] for node in G.nodes()]
            
            # Create edges
            edge_x = []
            edge_y = []
            for edge in G.edges():
                x0, y0 = pos[edge[0]]
                x1, y1 = pos[edge[1]]
                edge_x.extend([x0, x1, None])
                edge_y.extend([y0, y1, None])
            
            # Create figure
            fig = go.Figure()
            
            # Add edges
            fig.add_trace(go.Scatter(
                x=edge_x, y=edge_y,
                line=dict(width=2, color='#888'),
                hoverinfo='none',
                mode='lines'
            ))
            
            # Add nodes
            fig.add_trace(go.Scatter(
                x=node_x, y=node_y,
                mode='markers+text',
                text=node_labels,
                textposition="middle center",
                hoverinfo='text',
                marker=dict(
                    size=node_sizes,
                    color=node_colors,
                    line=dict(width=2, color='black')
                )
            ))
            
            fig.update_layout(
                title="Investigation Network Graph",
                title_x=0.5,
                showlegend=False,
                hovermode='closest',
                margin=dict(b=20, l=5, r=5, t=40),
                annotations=[dict(
                    text="Network visualization of investigation findings",
                    showarrow=False,
                    xref="paper", yref="paper",
                    x=0.005, y=-0.002
                )],
                xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)
            )
            
            return fig
        
        @self.app.callback(
            Output('raw-data-content', 'children'),
            [Input('investigation-data', 'data')]
        )
        def update_raw_data_content(data):
            if not data:
                return html.P("No data available.")
            
            # Format JSON for display
            formatted_json = json.dumps(data, indent=2, default=str)
            
            return html.Div([
                html.H4("Raw Investigation Data", className="mb-3"),
                html.Pre(formatted_json, className="bg-light p-3 rounded")
            ])
    
    def run(self, host: str = None, port: int = None, debug: bool = None):
        """Run the dashboard"""
        if not self.app:
            self.create_app()
        
        # Use config values if not provided
        host = host or self.config.DASH_HOST
        port = port or self.config.DASH_PORT
        debug = debug if debug is not None else self.config.DASH_DEBUG
        
        print(f"📊 Starting dashboard at http://{host}:{port}")
        # Dash 3.x uses app.run instead of app.run_server
        self.app.run(host=host, port=port, debug=debug)
    
    def load_investigation_data(self, filepath: str) -> bool:
        """Load investigation data from JSON file"""
        try:
            with open(filepath, 'r') as f:
                self.investigation_data = json.load(f)
            return True
        except Exception as e:
            print(f"❌ Error loading investigation data: {e}")
            return False
    
    def set_investigation_data(self, data: Dict[str, Any]):
        """Set investigation data directly"""
        self.investigation_data = data
