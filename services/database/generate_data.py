#!/usr/bin/env python3
"""
Data Generator Script for PostgreSQL Notification System
Generates realistic test data for eng_interactions table
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

class DataGenerator:
    def __init__(self):
        self.manager = InteractionManager()
        
        # Sample data for realistic generation
        self.channels = ['whatsapp', 'twitter', 'facebook', 'email']
        self.statuses = ['new', 'in_progress', 'waiting_for_response', 'resolved', 'closed']
        self.directions = ['inbound', 'outbound']
        
        # Sample user identifiers
        self.whatsapp_users = ['+1234567890', '+1987654321', '+1555123456', '+1444987654', '+1333456789']
        self.twitter_users = ['@john_doe', '@jane_smith', '@tech_guru', '@business_pro', '@startup_founder']
        self.facebook_users = ['john.doe.123', 'jane.smith.456', 'tech.enthusiast', 'business.owner']
        self.email_users = ['john@example.com', 'jane@company.com', 'support@business.com', 'info@startup.com']
        
        # Sample messages
        self.whatsapp_messages = [
            "Hi, I need help with my order",
            "When will my package arrive?",
            "I have a question about billing",
            "Can you help me with account setup?",
            "I'm having trouble logging in",
            "What are your business hours?",
            "I need to update my address",
            "Can I cancel my subscription?",
            "I want to return an item",
            "How do I track my order?"
        ]
        
        self.twitter_messages = [
            "Great service! Highly recommend",
            "Having issues with the app",
            "When will this feature be available?",
            "Love the new update!",
            "Need help with account verification",
            "This is amazing!",
            "Can you fix this bug?",
            "Thanks for the quick response",
            "Still waiting for my refund",
            "How do I contact support?"
        ]
        
        self.facebook_messages = [
            "Love your products!",
            "Need assistance with my order",
            "When will you have new items?",
            "Great customer service",
            "Having trouble with checkout",
            "Can you help me find something?",
            "Love the new collection",
            "Need to speak to a manager",
            "This is exactly what I needed",
            "How do I leave a review?"
        ]
        
        self.email_messages = [
            "Subject: Order Inquiry - Need assistance with my recent purchase",
            "Subject: Account Issue - Cannot access my account",
            "Subject: Billing Question - Please explain these charges",
            "Subject: Product Support - Need help with setup",
            "Subject: Return Request - Would like to return item",
            "Subject: Feature Request - Suggestion for improvement",
            "Subject: Complaint - Poor service experience",
            "Subject: Compliment - Excellent customer service",
            "Subject: Technical Support - App not working properly",
            "Subject: General Inquiry - Business hours and contact info"
        ]

    def generate_interaction(self, channel=None):
        """Generate a single interaction with realistic data."""
        if channel is None:
            channel = random.choice(self.channels)
        
        # Get channel-specific data
        if channel == 'whatsapp':
            user_identifier = random.choice(self.whatsapp_users)
            text = random.choice(self.whatsapp_messages)
        elif channel == 'twitter':
            user_identifier = random.choice(self.twitter_users)
            text = random.choice(self.twitter_messages)
        elif channel == 'facebook':
            user_identifier = random.choice(self.facebook_users)
            text = random.choice(self.facebook_messages)
        else:  # email
            user_identifier = random.choice(self.email_users)
            text = random.choice(self.email_messages)
        
        # Generate timestamps
        now = datetime.now()
        original_created_at = now - timedelta(minutes=random.randint(1, 60))
        
        # Generate frontend JSON
        frontend_json = {
            'message_type': 'text',
            'sender_name': user_identifier.split('@')[0] if '@' in user_identifier else user_identifier,
            'channel_metadata': {
                'platform': channel,
                'message_id': f'{channel}_{random.randint(1000, 9999)}',
                'timestamp': original_created_at.isoformat()
            }
        }
        
        interaction_data = {
            'channel': channel,
            'channel_interaction_id': f'{channel}_{int(time.time())}_{random.randint(100, 999)}',
            'user_identifier': user_identifier,
            'status': random.choice(self.statuses),
            'original_created_at': original_created_at,
            'entity_id': f'client_{random.randint(100, 999)}',
            'reference_id': f'agent_{random.randint(100, 999)}',
            'last_reply_id': f'reply_{random.randint(1000, 9999)}',
            'last_reply_created_at': original_created_at,
            'last_reply_direction': random.choice(self.directions),
            'frontend_json': json.dumps(frontend_json),
            'text': text,
            'sort_key': int(time.time() * 1000)
        }
        
        return interaction_data

    def generate_batch(self, count=10, channel=None):
        """Generate multiple interactions."""
        print(f"🔄 Generating {count} interactions...")
        
        for i in range(count):
            try:
                interaction_data = self.generate_interaction(channel)
                interaction_id = self.manager.create_interaction(interaction_data)
                print(f"✅ Created interaction {i+1}/{count} - ID: {interaction_id} - {interaction_data['channel']} - {interaction_data['user_identifier']}")
                
                # Small delay to avoid overwhelming the database
                time.sleep(0.1)
                
            except Exception as e:
                print(f"❌ Error creating interaction {i+1}: {e}")
        
        print(f"🎉 Generated {count} interactions successfully!")

    def generate_realistic_scenario(self):
        """Generate a realistic customer service scenario."""
        print("🎭 Generating realistic customer service scenario...")
        
        # Generate interactions over the last hour
        interactions = []
        
        # WhatsApp interactions (most common)
        for _ in range(8):
            interaction_data = self.generate_interaction('whatsapp')
            interaction_data['status'] = random.choice(['new', 'in_progress', 'resolved'])
            interactions.append(interaction_data)
        
        # Twitter interactions
        for _ in range(5):
            interaction_data = self.generate_interaction('twitter')
            interaction_data['status'] = random.choice(['new', 'in_progress', 'waiting_for_response'])
            interactions.append(interaction_data)
        
        # Facebook interactions
        for _ in range(4):
            interaction_data = self.generate_interaction('facebook')
            interaction_data['status'] = random.choice(['new', 'in_progress', 'resolved'])
            interactions.append(interaction_data)
        
        # Email interactions
        for _ in range(3):
            interaction_data = self.generate_interaction('email')
            interaction_data['status'] = random.choice(['new', 'waiting_for_response', 'resolved'])
            interactions.append(interaction_data)
        
        # Create all interactions
        for i, interaction_data in enumerate(interactions):
            try:
                interaction_id = self.manager.create_interaction(interaction_data)
                print(f"✅ Created scenario interaction {i+1}/{len(interactions)} - ID: {interaction_id} - {interaction_data['channel']} - {interaction_data['status']}")
                time.sleep(0.1)
            except Exception as e:
                print(f"❌ Error creating scenario interaction {i+1}: {e}")
        
        print("🎉 Realistic scenario generated successfully!")

def main():
    print("🚀 PostgreSQL Data Generator")
    print("=" * 40)
    
    generator = DataGenerator()
    
    while True:
        print("\n📊 Data Generation Options:")
        print("1. Generate random interactions (10)")
        print("2. Generate random interactions (50)")
        print("3. Generate realistic scenario (20 interactions)")
        print("4. Generate WhatsApp only (15)")
        print("5. Generate Twitter only (10)")
        print("6. Generate Facebook only (8)")
        print("7. Generate Email only (5)")
        print("8. Exit")
        
        choice = input("\nSelect option (1-8): ").strip()
        
        if choice == '1':
            generator.generate_batch(10)
        elif choice == '2':
            generator.generate_batch(50)
        elif choice == '3':
            generator.generate_realistic_scenario()
        elif choice == '4':
            generator.generate_batch(15, 'whatsapp')
        elif choice == '5':
            generator.generate_batch(10, 'twitter')
        elif choice == '6':
            generator.generate_batch(8, 'facebook')
        elif choice == '7':
            generator.generate_batch(5, 'email')
        elif choice == '8':
            print("👋 Goodbye!")
            break
        else:
            print("❌ Invalid option. Please try again.")

if __name__ == "__main__":
    main()
