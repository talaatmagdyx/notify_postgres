#!/usr/bin/env python3
"""
Unified Multi-Tenant Flask API Backend
Uses unified notification system to handle multiple companies
"""

import os
import json
import threading
import time
from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_socketio import SocketIO, emit
import psycopg2
from dotenv import load_dotenv
import sys

# Add notification-engine directory to path
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'notification-engine'))
from unified_system import MultiTenantInteractionManager, unified_notifier
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class UnifiedBackend:
    def __init__(self, company_code, port):
        self.company_code = company_code
        self.port = port
        self.app = Flask(__name__)
        self.socketio = SocketIO(
            self.app, 
            cors_allowed_origins="*",
            logger=True,
            engineio_logger=True,
            async_mode='threading'
        )
        CORS(self.app)
        
        # Initialize interaction manager for this company
        self.interaction_manager = MultiTenantInteractionManager(company_code)
        
        # Register this backend with the unified notification system
        unified_notifier.register_backend(company_code, self.socketio)
        
        # Setup routes
        self.setup_routes()
        
        # Setup SocketIO events
        self.setup_socketio_events()
        
        # Start unified notification system if not already running
        if not unified_notifier.running:
            unified_notifier.start_listening()
    
    def setup_routes(self):
        @self.app.route('/api/engagements', methods=['GET'])
        def get_engagements():
            try:
                engagements = self.interaction_manager.get_all_interactions()
                return jsonify(engagements)
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/engagements', methods=['POST'])
        def create_engagement():
            try:
                data = request.get_json()
                engagement_id = self.interaction_manager.create_interaction(data)
                return jsonify({'id': engagement_id, 'message': 'Engagement created successfully'}), 201
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/engagements/<int:engagement_id>', methods=['PUT'])
        def update_engagement(engagement_id):
            try:
                data = request.get_json()
                self.interaction_manager.update_interaction_status(engagement_id, data.get('status'))
                return jsonify({'message': 'Engagement updated successfully'})
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/company/info', methods=['GET'])
        def get_company_info():
            try:
                conn = self.interaction_manager.get_connection()
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM get_company_config(%s)", (self.company_code,))
                result = cursor.fetchone()
                cursor.close()
                conn.close()
                
                if result:
                    return jsonify({
                        'company_code': result[0],
                        'company_name': result[1],
                        'schema_name': result[2],
                        'frontend_port': result[3],
                        'backend_port': result[4]
                    })
                else:
                    return jsonify({'error': 'Company not found'}), 404
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/analytics', methods=['GET'])
        def get_analytics():
            try:
                conn = self.interaction_manager.get_connection()
                cursor = conn.cursor()
                
                # Get company schema name
                cursor.execute("SELECT schema_name FROM companies WHERE company_code = %s", (self.company_code,))
                schema_result = cursor.fetchone()
                if not schema_result:
                    return jsonify({'error': 'Company schema not found'}), 404
                
                schema_name = schema_result[0]
                
                # Get analytics data
                cursor.execute(f"""
                    SELECT metric_name, metric_value, metric_date, channel 
                    FROM {schema_name}.analytics 
                    ORDER BY metric_date DESC 
                """)
                analytics = cursor.fetchall()
                
                cursor.close()
                conn.close()
                
                return jsonify([{
                    'metric_name': row[0],
                    'metric_value': float(row[1]),
                    'metric_date': row[2].isoformat(),
                    'channel': row[3]
                } for row in analytics])
            except Exception as e:
                return jsonify({'error': str(e)}), 500
        
        @self.app.route('/api/stats', methods=['GET'])
        def get_stats():
            try:
                stats = self.interaction_manager.get_company_stats()
                return jsonify(stats)
            except Exception as e:
                return jsonify({'error': str(e)}), 500
    
    def setup_socketio_events(self):
        """Setup SocketIO event handlers."""
        
        @self.socketio.on('connect')
        def handle_connect():
            print(f"🔌 Client connected to {self.company_code} backend")
            self.socketio.emit('connected', {'company': self.company_code})
        
        @self.socketio.on('disconnect')
        def handle_disconnect():
            print(f"🔌 Client disconnected from {self.company_code} backend")
        
        @self.socketio.on('join_company')
        def handle_join_company(data):
            print(f"🏢 Client joined company: {data.get('company', 'unknown')}")
            self.socketio.emit('joined', {'company': self.company_code})
    
    def run(self):
        print(f"🚀 Starting {self.company_code} Backend on port {self.port}")
        print(f"✅ Interaction manager setup complete")
        print(f"🔗 Registered with unified notification system")
        
        self.socketio.run(
            self.app, 
            host='0.0.0.0', 
            port=self.port, 
            debug=True,
            allow_unsafe_werkzeug=True
        )

def main():
    # Get company code from environment or command line
    company_code = os.getenv('COMPANY_CODE', 'COMP_A')
    
    # Get port from environment or use default
    port = int(os.getenv('BACKEND_PORT', 5001))
    
    print(f"🏢 Unified Multi-Tenant PostgreSQL Notification System")
    print(f"📊 Company: {company_code}")
    print(f"🔌 Port: {port}")
    
    # Create and run backend
    backend = UnifiedBackend(company_code, port)
    backend.run()

if __name__ == '__main__':
    main()
