#!/usr/bin/env python3
"""
Simple PostgreSQL Notification Test
This script tests the notification system step by step
"""

import time
import json
from datetime import datetime
from notification_system import InteractionManager
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def main():
    print("🧪 PostgreSQL Notification System - Simple Test")
    print("=" * 50)
    
    # Initialize the notification manager
    print("🔧 Initializing notification manager...")
    manager = InteractionManager()
    
    # Add simple notification handlers
    def interaction_handler(payload):
        print(f"🔔 INTERACTION: {payload['operation']} - {payload['channel']}")
        print(f"   User: {payload['user_identifier']}")
        print(f"   Text: {payload['text'][:30]}...")
        print()
    
    def status_handler(payload):
        print(f"📊 STATUS: {payload['old_status']} → {payload['new_status']}")
        print(f"   ID: {payload['interaction_id']}")
        print()
    
    # Register handlers
    manager.notifier.add_listener('interaction_changes', interaction_handler)
    manager.notifier.add_listener('status_changes', status_handler)
    
    # Start notifications
    print("📡 Starting notification listener...")
    manager.start_notifications()
    
    # Create test interaction
    print("📝 Creating test interaction...")
    interaction_data = {
        'channel': 'whatsapp',
        'channel_interaction_id': 'wa_test_001',
        'user_identifier': '+1234567890',
        'status': 'new',
        'original_created_at': datetime.now(),
        'entity_id': 'client_001',
        'reference_id': 'agent_001',
        'last_reply_id': 'reply_001',
        'last_reply_created_at': datetime.now(),
        'last_reply_direction': 'inbound',
        'frontend_json': json.dumps({'type': 'text'}),
        'text': 'Hello, I need help with my order',
        'sort_key': int(time.time() * 1000)
    }
    
    interaction_id = manager.create_interaction(interaction_data)
    print(f"✅ Created interaction with ID: {interaction_id}")
    
    time.sleep(2)
    
    # Update status
    print("🔄 Updating interaction status...")
    manager.update_interaction_status(interaction_id, 'in_progress')
    
    time.sleep(2)
    
    manager.update_interaction_status(interaction_id, 'resolved')
    
    print("✅ Test completed successfully!")
    print("   You should have seen real-time notifications above")
    
    # Keep running for manual testing
    print("\n⏳ Keeping listener active...")
    print("   Press Ctrl+C to stop")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Stopping...")
    finally:
        manager.stop_notifications()
        print("✅ Stopped")

if __name__ == "__main__":
    main()
