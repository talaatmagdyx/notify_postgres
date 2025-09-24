#!/usr/bin/env python3
"""
Multi-Tenant Data Generator Script for PostgreSQL Notification System
Generates realistic test data for multiple companies with separate schemas
"""

import random
import json
import time
import sys
import os
import uuid
from datetime import datetime, timedelta

# Add notification-engine directory to path
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'notification-engine'))
from unified_system import MultiTenantInteractionManager
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class MultiTenantDataGenerator:
    def __init__(self):
        self.interaction_manager = MultiTenantInteractionManager()
        self.companies = {
            'COMP_A': {
                'name': 'Company Alpha',
                'schema': 'company_a',
                'frontend_port': 3001,
                'backend_port': 5001,
                'primary_color': '#25D366',
                'channels': ['whatsapp', 'email'],
                'user_prefixes': ['alpha', 'alpha_corp', 'alpha_support']
            },
            'COMP_B': {
                'name': 'Company Beta',
                'schema': 'company_b',
                'frontend_port': 3002,
                'backend_port': 5002,
                'primary_color': '#1DA1F2',
                'channels': ['twitter', 'facebook'],
                'user_prefixes': ['beta', 'beta_corp', 'beta_support']
            },
            'COMP_C': {
                'name': 'Company Gamma',
                'schema': 'company_c',
                'frontend_port': 3003,
                'backend_port': 5003,
                'primary_color': '#4267B2',
                'channels': ['whatsapp', 'twitter', 'facebook', 'email'],
                'user_prefixes': ['gamma', 'gamma_corp', 'gamma_support']
            }
        }
        
        self.statuses = ['new', 'in_progress', 'resolved', 'closed']
        self.directions = ['inbound', 'outbound']
        self.closing_reasons = ['resolved', 'duplicate', 'no_response', 'spam', 'escalated']
        
        # Sample texts for different channels
        self.sample_texts = {
            'whatsapp': [
                "Hi, I need help with my order",
                "When will my package arrive?",
                "I have a question about billing",
                "Can you help me with my account?",
                "I'm having trouble logging in"
            ],
            'twitter': [
                "@company thanks for the great service!",
                "Having issues with your product",
                "Love the new features!",
                "Need help with my subscription",
                "When is the next update coming?"
            ],
            'facebook': [
                "Great customer service!",
                "I have a complaint about...",
                "Can someone help me?",
                "Love your products!",
                "Need assistance with my order"
            ],
            'email': [
                "Subject: Order Inquiry",
                "Subject: Technical Support Request",
                "Subject: Billing Question",
                "Subject: Feature Request",
                "Subject: Account Issue"
            ]
        }

    def generate_interaction(self, company_code, channel):
        """Generate a single interaction for a specific company and channel"""
        company = self.companies[company_code]
        
        # Generate user identifier based on channel
        if channel == 'whatsapp':
            user_identifier = f"+1{random.randint(1000000000, 9999999999)}"
        elif channel == 'twitter':
            user_identifier = f"@{random.choice(company['user_prefixes'])}_{random.randint(100, 999)}"
        elif channel == 'facebook':
            user_identifier = f"{random.choice(company['user_prefixes'])}.{random.randint(100, 999)}"
        elif channel == 'email':
            user_identifier = f"{random.choice(company['user_prefixes'])}_{random.randint(100, 999)}@{company['name'].lower().replace(' ', '')}.com"
        else:
            user_identifier = f"user_{random.randint(1000, 9999)}"
        
        # Generate timestamps
        now = datetime.now()
        created_at = now - timedelta(hours=random.randint(0, 72))
        updated_at = created_at + timedelta(minutes=random.randint(0, 60))
        original_created_at = created_at - timedelta(minutes=random.randint(0, 30))
        
        # Generate interaction data
        interaction_data = {
            'channel': channel,
            'channel_interaction_id': f"{channel}_{random.randint(100000, 999999)}",
            'user_identifier': user_identifier,
            'status': random.choice(self.statuses),
            'created_at': created_at.isoformat(),
            'updated_at': updated_at.isoformat(),
            'original_created_at': original_created_at.isoformat(),
            'engagement_id': str(uuid.uuid4()),
            'entity_id': f"entity_{random.randint(1000, 9999)}",
            'reference_id': f"ref_{random.randint(1000, 9999)}",
            'is_replied': random.choice([True, False]),
            'is_delayed': random.choice([True, False]),
            'is_spam': random.choice([True, False]),
            'is_reopened': random.choice([True, False]),
            'channel_closing_reason': random.choice(self.closing_reasons) if random.random() < 0.3 else None,
            'last_reply_id': f"reply_{random.randint(1000, 9999)}",
            'last_reply_created_at': updated_at.isoformat(),
            'last_reply_direction': random.choice(self.directions),
            'frontend_json': json.dumps({
                'company': company_code,
                'theme': company['primary_color'],
                'metadata': {
                    'source': 'generated',
                    'priority': random.choice(['low', 'medium', 'high']),
                    'tags': random.sample(['urgent', 'billing', 'technical', 'general'], random.randint(1, 3))
                }
            }),
            'text': random.choice(self.sample_texts[channel]),
            'sort_key': int(time.time() * 1000) + random.randint(0, 999),
            'company_id': company_code
        }
        
        return interaction_data

    def generate_company_data(self, company_code, num_interactions=20):
        """Generate data for a specific company"""
        company = self.companies[company_code]
        print(f"🏢 Generating {num_interactions} interactions for {company['name']} ({company_code})")
        
        interactions = []
        for i in range(num_interactions):
            channel = random.choice(company['channels'])
            interaction = self.generate_interaction(company_code, channel)
            interactions.append(interaction)
            
            print(f"✅ {i+1}/{num_interactions} - {channel} - {interaction['user_identifier']}")
        
        return interactions

    def insert_company_data(self, company_code, interactions):
        """Insert generated data into the company's schema"""
        company = self.companies[company_code]
        schema_name = company['schema']
        
        try:
            conn = self.interaction_manager.get_connection()
            cursor = conn.cursor()
            
            for interaction in interactions:
                # Insert into company-specific schema
                insert_query = f"""
                    INSERT INTO {schema_name}.eng_interactions (
                        channel, channel_interaction_id, user_identifier, status,
                        created_at, updated_at, original_created_at, engagement_id,
                        entity_id, reference_id, is_replied, is_delayed, is_spam,
                        is_reopened, channel_closing_reason, last_reply_id,
                        last_reply_created_at, last_reply_direction, frontend_json,
                        text, sort_key, company_id
                    ) VALUES (
                        %(channel)s, %(channel_interaction_id)s, %(user_identifier)s, %(status)s,
                        %(created_at)s, %(updated_at)s, %(original_created_at)s, %(engagement_id)s,
                        %(entity_id)s, %(reference_id)s, %(is_replied)s, %(is_delayed)s, %(is_spam)s,
                        %(is_reopened)s, %(channel_closing_reason)s, %(last_reply_id)s,
                        %(last_reply_created_at)s, %(last_reply_direction)s, %(frontend_json)s,
                        %(text)s, %(sort_key)s, %(company_id)s
                    )
                """
                
                cursor.execute(insert_query, interaction)
            
            conn.commit()
            cursor.close()
            conn.close()
            
            print(f"🎉 Successfully inserted {len(interactions)} interactions into {schema_name}")
            
        except Exception as e:
            print(f"❌ Error inserting data for {company_code}: {e}")

    def generate_analytics_data(self, company_code, num_days=30):
        """Generate analytics data for a company"""
        company = self.companies[company_code]
        schema_name = company['schema']
        
        try:
            conn = self.interaction_manager.get_connection()
            cursor = conn.cursor()
            
            for day in range(num_days):
                date = datetime.now() - timedelta(days=day)
                
                # Generate daily metrics
                metrics = [
                    ('total_engagements', random.randint(50, 200)),
                    ('new_engagements', random.randint(10, 50)),
                    ('resolved_engagements', random.randint(20, 80)),
                    ('avg_response_time', random.randint(5, 60)),
                    ('customer_satisfaction', random.randint(70, 95))
                ]
                
                for metric_name, metric_value in metrics:
                    for channel in company['channels']:
                        cursor.execute(f"""
                            INSERT INTO {schema_name}.analytics 
                            (metric_name, metric_value, metric_date, channel)
                            VALUES (%s, %s, %s, %s)
                        """, (metric_name, metric_value, date.date(), channel))
            
            conn.commit()
            cursor.close()
            conn.close()
            
            print(f"📊 Generated analytics data for {company['name']}")
            
        except Exception as e:
            print(f"❌ Error generating analytics for {company_code}: {e}")

    def generate_all_companies_data(self, interactions_per_company=20):
        """Generate data for all companies"""
        print("🚀 Multi-Tenant Data Generator")
        print("=" * 50)
        
        for company_code in self.companies.keys():
            print(f"\n🏢 Processing {self.companies[company_code]['name']}")
            print("-" * 30)
            
            # Generate interactions
            interactions = self.generate_company_data(company_code, interactions_per_company)
            
            # Insert data
            self.insert_company_data(company_code, interactions)
            
            # Generate analytics
            self.generate_analytics_data(company_code)
            
            print(f"✅ Completed {self.companies[company_code]['name']}")
        
        print("\n🎉 All companies data generated successfully!")
        print("\n📱 Access Points:")
        for company_code, company in self.companies.items():
            print(f"  {company['name']}: http://localhost:{company['frontend_port']}")

def main():
    generator = MultiTenantDataGenerator()
    
    print("🏢 Multi-Tenant PostgreSQL Data Generator")
    print("=" * 50)
    print("📊 Data Generation Options:")
    print("1. Generate data for all companies (20 interactions each)")
    print("2. Generate data for Company A only")
    print("3. Generate data for Company B only")
    print("4. Generate data for Company C only")
    print("5. Generate large dataset for all companies (50 interactions each)")
    print("6. Exit")
    
    try:
        choice = input("\nSelect option (1-6): ").strip()
        
        if choice == '1':
            generator.generate_all_companies_data(20)
        elif choice == '2':
            interactions = generator.generate_company_data('COMP_A', 20)
            generator.insert_company_data('COMP_A', interactions)
            generator.generate_analytics_data('COMP_A')
        elif choice == '3':
            interactions = generator.generate_company_data('COMP_B', 20)
            generator.insert_company_data('COMP_B', interactions)
            generator.generate_analytics_data('COMP_B')
        elif choice == '4':
            interactions = generator.generate_company_data('COMP_C', 20)
            generator.insert_company_data('COMP_C', interactions)
            generator.generate_analytics_data('COMP_C')
        elif choice == '5':
            generator.generate_all_companies_data(50)
        elif choice == '6':
            print("👋 Goodbye!")
        else:
            print("❌ Invalid option. Please run the script again.")
            
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()
