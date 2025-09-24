#!/usr/bin/env python3
"""
Quick Data Generator - Generates sample data instantly
"""

import random
import json
import time
import sys
import os
from datetime import datetime, timedelta

# Add notification-engine directory to path
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'notification-engine'))
from notification_system import InteractionManager
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def quick_generate():
    """Quickly generate sample data for testing."""
    print("🚀 Quick Data Generator")
    print("=" * 30)
    
    manager = InteractionManager()
    
    # Sample data
    channels = ['whatsapp', 'twitter', 'facebook', 'email']
    users = {
        'whatsapp': ['+1234567890', '+1987654321', '+1555123456'],
        'twitter': ['@john_doe', '@jane_smith', '@tech_guru'],
        'facebook': ['john.doe.123', 'jane.smith.456'],
        'email': ['john@example.com', 'jane@company.com']
    }
    
    messages = {
        'whatsapp': [
            "Hi, I need help with my order",
            "When will my package arrive?",
            "I have a billing question",
            "Can you help me with setup?",
            "I'm having login issues"
        ],
        'twitter': [
            "Great service! Highly recommend",
            "Having issues with the app",
            "Love the new update!",
            "Need help with verification",
            "Thanks for quick response"
        ],
        'facebook': [
            "Love your products!",
            "Need assistance with order",
            "Great customer service",
            "Having trouble with checkout",
            "Can you help me find something?"
        ],
        'email': [
            "Subject: Order Inquiry - Need assistance",
            "Subject: Account Issue - Cannot access",
            "Subject: Billing Question - Please explain",
            "Subject: Product Support - Need help",
            "Subject: Return Request - Would like to return"
        ]
    }
    
    print("🔄 Generating 20 sample interactions...")
    
    for i in range(20):
        channel = random.choice(channels)
        user = random.choice(users[channel])
        message = random.choice(messages[channel])
        
        interaction_data = {
            'channel': channel,
            'channel_interaction_id': f'{channel}_{int(time.time())}_{i}',
            'user_identifier': user,
            'status': random.choice(['new', 'in_progress', 'resolved']),
            'original_created_at': datetime.now() - timedelta(minutes=random.randint(1, 120)),
            'entity_id': f'client_{random.randint(100, 999)}',
            'reference_id': f'agent_{random.randint(100, 999)}',
            'last_reply_id': f'reply_{random.randint(1000, 9999)}',
            'last_reply_created_at': datetime.now() - timedelta(minutes=random.randint(1, 60)),
            'last_reply_direction': random.choice(['inbound', 'outbound']),
            'frontend_json': json.dumps({
                'message_type': 'text',
                'sender_name': user.split('@')[0] if '@' in user else user,
                'platform': channel
            }),
            'text': message,
            'sort_key': int(time.time() * 1000) + i
        }
        
        try:
            interaction_id = manager.create_interaction(interaction_data)
            print(f"✅ {i+1}/20 - {channel} - {user} - ID: {interaction_id}")
            time.sleep(0.1)
        except Exception as e:
            print(f"❌ Error {i+1}: {e}")
    
    print("\n🎉 Sample data generated successfully!")
    print("📱 Check your React app at http://localhost:3000")

if __name__ == "__main__":
    quick_generate()
