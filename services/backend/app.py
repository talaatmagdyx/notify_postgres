#!/usr/bin/env python3
"""
Flask API Backend for PostgreSQL Notification System
Provides REST API and WebSocket for real-time notifications
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

# Add notification-engine directory to path to import notification_system
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'notification-engine'))
from notification_system import InteractionManager

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# Global variables
interaction_manager = None
notification_thread = None

def setup_interaction_manager():
    """Setup the interaction manager with notification handlers."""
    global interaction_manager
    
    interaction_manager = InteractionManager()
    
    def interaction_handler(payload):
        """Handle interaction change notifications."""
        print(f"🔔 INTERACTION: {payload['operation']} - {payload['channel']}")
        # Emit to all connected clients
        socketio.emit('interaction_change', payload)
    
    def status_handler(payload):
        """Handle status change notifications."""
        print(f"📊 STATUS: {payload['old_status']} -> {payload['new_status']}")
        # Emit to all connected clients
        socketio.emit('status_change', payload)
    
    # Register handlers
    interaction_manager.notifier.add_listener('interaction_changes', interaction_handler)
    interaction_manager.notifier.add_listener('status_changes', status_handler)
    
    # Start listening for notifications
    interaction_manager.start_notifications()
    print("✅ Interaction manager setup complete")

@app.route('/api/engagements', methods=['GET'])
def get_engagements():
    """Get all engagements."""
    try:
        conn = psycopg2.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            port=int(os.getenv('DB_PORT', 5432)),
            database=os.getenv('DB_NAME', 'notify_postgres'),
            user=os.getenv('DB_USER', 'postgres'),
            password=os.getenv('DB_PASSWORD', 'password')
        )
        cursor = conn.cursor()
        
        query = """
            SELECT id, channel, user_identifier, status, created_at, text, engagement_id
            FROM eng_interactions 
            ORDER BY created_at DESC 
        """
        cursor.execute(query)
        
        columns = [desc[0] for desc in cursor.description]
        engagements = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        cursor.close()
        conn.close()
        
        return jsonify(engagements)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/engagements', methods=['POST'])
def create_engagement():
    """Create a new engagement."""
    try:
        data = request.json
        
        # Prepare interaction data
        interaction_data = {
            'channel': data.get('channel', 'whatsapp'),
            'channel_interaction_id': data.get('channel_interaction_id', f'msg_{int(time.time())}'),
            'user_identifier': data.get('user_identifier', '+1234567890'),
            'status': 'new',
            'original_created_at': datetime.now(),
            'entity_id': data.get('entity_id', 'client_001'),
            'reference_id': data.get('reference_id', 'agent_001'),
            'last_reply_id': data.get('last_reply_id', 'reply_001'),
            'last_reply_created_at': datetime.now(),
            'last_reply_direction': 'inbound',
            'frontend_json': json.dumps(data.get('frontend_json', {})),
            'text': data.get('text', 'New message'),
            'sort_key': int(time.time() * 1000)
        }
        
        interaction_id = interaction_manager.create_interaction(interaction_data)
        
        return jsonify({
            'id': interaction_id,
            'message': 'Engagement created successfully'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/engagements/<int:engagement_id>/status', methods=['PUT'])
def update_engagement_status(engagement_id):
    """Update engagement status."""
    try:
        data = request.json
        new_status = data.get('status')
        
        if not new_status:
            return jsonify({'error': 'Status is required'}), 400
        
        success = interaction_manager.update_interaction_status(engagement_id, new_status)
        
        if success:
            return jsonify({'message': 'Status updated successfully'})
        else:
            return jsonify({'error': 'Engagement not found'}), 404
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@socketio.on('connect')
def handle_connect():
    """Handle client connection."""
    print('Client connected')
    emit('connected', {'message': 'Connected to notification system'})

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection."""
    print('Client disconnected')

if __name__ == '__main__':
    print("🚀 Starting Flask API Backend...")
    
    # Setup interaction manager
    setup_interaction_manager()
    
    # Start the Flask app
    socketio.run(app, host='0.0.0.0', port=5001, debug=True, allow_unsafe_werkzeug=True)
