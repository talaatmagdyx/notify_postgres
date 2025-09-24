#!/usr/bin/env python3
"""
Multi-Tenant Data Generator Script for PostgreSQL Notification System
Generates realistic test data for multiple companies with separate schemas
Enhanced with Faker for more realistic data generation
"""

import random
import json
import time
import sys
import os
import uuid
from datetime import datetime, timedelta
from faker import Faker
from faker.providers import internet, phone_number, company, lorem, date_time, person

# Add notification-engine directory to path
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'notification-engine'))
from unified_system import MultiTenantInteractionManager
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Faker with multiple locales for more diverse data
fake = Faker(['en_US', 'en_GB', 'en_CA', 'en_AU'])

class MultiTenantDataGenerator:
    def __init__(self):
        self.interaction_manager = MultiTenantInteractionManager()
        self.companies = {
            'COMP_A': {
                'name': 'TechFlow Solutions',
                'schema': 'company_a',
                'frontend_port': 3001,
                'backend_port': 5001,
                'primary_color': '#25D366',
                'channels': ['whatsapp', 'email'],
                'industry': 'Technology',
                'company_domain': 'techflow.com',
                'support_team': ['support', 'help', 'assistance', 'customer-service'],
                'product_categories': ['software', 'api', 'integration', 'dashboard', 'analytics']
            },
            'COMP_B': {
                'name': 'SocialMedia Pro',
                'schema': 'company_b',
                'frontend_port': 3002,
                'backend_port': 5002,
                'primary_color': '#1DA1F2',
                'channels': ['twitter', 'facebook'],
                'industry': 'Social Media Marketing',
                'company_domain': 'socialmediapro.com',
                'support_team': ['support', 'help', 'team', 'community'],
                'product_categories': ['campaigns', 'analytics', 'engagement', 'content', 'scheduling']
            },
            'COMP_C': {
                'name': 'OmniChannel Corp',
                'schema': 'company_c',
                'frontend_port': 3003,
                'backend_port': 5003,
                'primary_color': '#4267B2',
                'channels': ['whatsapp', 'twitter', 'facebook', 'email'],
                'industry': 'E-commerce',
                'company_domain': 'omnichannel.com',
                'support_team': ['support', 'help', 'service', 'care', 'assistance'],
                'product_categories': ['orders', 'shipping', 'returns', 'products', 'billing']
            }
        }
        
        self.statuses = ['new', 'in_progress', 'resolved', 'closed']
        self.directions = ['inbound', 'outbound']
        self.closing_reasons = ['resolved', 'duplicate', 'no_response', 'spam', 'escalated']
        
        # Enhanced message templates using Faker
        self.message_templates = {
            'whatsapp': [
                "Hi! I need help with {product}",
                "When will my {product} arrive?",
                "I have a question about {product}",
                "Can you help me with my {product}?",
                "I'm having trouble with {product}",
                "Is {product} available?",
                "How do I use {product}?",
                "I need support for {product}",
                "Can you explain {product} features?",
                "I want to return {product}"
            ],
            'twitter': [
                "@{company} thanks for the great {product}!",
                "Having issues with {product}",
                "Love the new {product} features!",
                "Need help with my {product} subscription",
                "When is the next {product} update coming?",
                "@{company} {product} is amazing!",
                "Can't figure out how to use {product}",
                "@{company} please help with {product}",
                "Is {product} compatible with my system?",
                "@{company} {product} not working properly"
            ],
            'facebook': [
                "Great {product} customer service!",
                "I have a complaint about {product}",
                "Can someone help me with {product}?",
                "Love your {product}!",
                "Need assistance with my {product} order",
                "How do I get started with {product}?",
                "Is {product} right for me?",
                "Having trouble with {product} setup",
                "Can you recommend {product} alternatives?",
                "Need help upgrading {product}"
            ],
            'email': [
                "Subject: {product} Inquiry",
                "Subject: {product} Technical Support Request",
                "Subject: {product} Billing Question",
                "Subject: {product} Feature Request",
                "Subject: {product} Account Issue",
                "Subject: {product} Integration Help",
                "Subject: {product} Pricing Information",
                "Subject: {product} Training Request",
                "Subject: {product} Bug Report",
                "Subject: {product} Customization"
            ]
        }

    def generate_interaction(self, company_code, channel):
        """Generate a single interaction for a specific company and channel using Faker"""
        company = self.companies[company_code]
        
        # Generate realistic user identifier based on channel
        if channel == 'whatsapp':
            user_identifier = fake.phone_number()
        elif channel == 'twitter':
            username = fake.user_name()
            user_identifier = f"@{username}"
        elif channel == 'facebook':
            user_identifier = fake.profile()['username']
        elif channel == 'email':
            user_identifier = fake.email()
        else:
            user_identifier = fake.user_name()
        
        # Generate realistic timestamps with proper distribution
        now = datetime.now()
        # More recent interactions are more likely
        hours_ago = random.choices(
            range(0, 168),  # 0-168 hours (1 week)
            weights=[10, 9, 8, 7, 6, 5, 4, 3, 2, 1] + [1] * 158,  # Recent bias
            k=1
        )[0]
        
        created_at = now - timedelta(hours=hours_ago)
        updated_at = created_at + timedelta(minutes=random.randint(0, 120))
        original_created_at = created_at - timedelta(minutes=random.randint(0, 30))
        
        # Generate realistic product/service name
        product = random.choice(company['product_categories'])
        
        # Generate realistic message text
        message_template = random.choice(self.message_templates[channel])
        message_text = message_template.format(
            product=product,
            company=company['name'].replace(' ', '').lower()
        )
        
        # Add some random lorem text for longer messages (30% chance)
        if random.random() < 0.3:
            additional_text = fake.text(max_nb_chars=200)
            message_text += f"\n\n{additional_text}"
        
        # Generate realistic status distribution
        status_weights = {'new': 0.4, 'in_progress': 0.3, 'resolved': 0.2, 'closed': 0.1}
        status = random.choices(list(status_weights.keys()), weights=list(status_weights.values()))[0]
        
        # Generate realistic boolean flags based on status
        is_replied = status in ['in_progress', 'resolved', 'closed'] and random.random() < 0.8
        is_delayed = random.random() < 0.15  # 15% chance of delay
        is_spam = random.random() < 0.05     # 5% chance of spam
        is_reopened = status == 'closed' and random.random() < 0.1  # 10% chance if closed
        
        # Generate realistic closing reason
        closing_reason = None
        if status == 'closed':
            closing_reason = random.choice(self.closing_reasons)
        
        # Generate realistic frontend JSON with more detailed metadata
        frontend_json = {
            'company': company_code,
            'theme': company['primary_color'],
            'industry': company['industry'],
            'metadata': {
                'source': 'generated',
                'priority': random.choices(['low', 'medium', 'high'], weights=[0.5, 0.3, 0.2])[0],
                'tags': random.sample(['urgent', 'billing', 'technical', 'general', 'feature-request', 'bug-report'], 
                                    random.randint(1, 3)),
                'customer_tier': random.choices(['basic', 'premium', 'enterprise'], weights=[0.6, 0.3, 0.1])[0],
                'language': fake.language_code(),
                'timezone': fake.timezone(),
                'device_type': random.choice(['mobile', 'desktop', 'tablet']),
                'browser': fake.user_agent(),
                'location': {
                    'country': fake.country_code(),
                    'city': fake.city(),
                    'region': fake.state()
                }
            }
        }
        
        # Generate interaction data
        interaction_data = {
            'channel': channel,
            'channel_interaction_id': f"{channel}_{fake.random_int(min=100000, max=999999)}",
            'user_identifier': user_identifier,
            'status': status,
            'created_at': created_at.isoformat(),
            'updated_at': updated_at.isoformat(),
            'original_created_at': original_created_at.isoformat(),
            'engagement_id': str(uuid.uuid4()),
            'entity_id': f"entity_{fake.random_int(min=1000, max=9999)}",
            'reference_id': f"ref_{fake.random_int(min=1000, max=9999)}",
            'is_replied': is_replied,
            'is_delayed': is_delayed,
            'is_spam': is_spam,
            'is_reopened': is_reopened,
            'channel_closing_reason': closing_reason,
            'last_reply_id': f"reply_{fake.random_int(min=1000, max=9999)}",
            'last_reply_created_at': updated_at.isoformat(),
            'last_reply_direction': random.choice(self.directions),
            'frontend_json': json.dumps(frontend_json),
            'text': message_text,
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
        """Generate realistic analytics data for a company using Faker"""
        company = self.companies[company_code]
        schema_name = company['schema']
        
        try:
            conn = self.interaction_manager.get_connection()
            cursor = conn.cursor()
            
            for day in range(num_days):
                date = datetime.now() - timedelta(days=day)
                
                # Generate realistic daily metrics with proper distributions
                base_volume = random.randint(20, 100)  # Base daily volume
                
                # Weekday vs weekend patterns
                if date.weekday() < 5:  # Weekday
                    volume_multiplier = random.uniform(1.2, 1.8)
                else:  # Weekend
                    volume_multiplier = random.uniform(0.6, 1.0)
                
                adjusted_volume = int(base_volume * volume_multiplier)
                
                # Generate realistic metrics
                metrics = [
                    ('total_engagements', adjusted_volume),
                    ('new_engagements', int(adjusted_volume * random.uniform(0.2, 0.4))),
                    ('resolved_engagements', int(adjusted_volume * random.uniform(0.3, 0.6))),
                    ('avg_response_time', random.randint(5, 120)),  # minutes
                    ('customer_satisfaction', random.randint(75, 98)),
                    ('first_response_time', random.randint(2, 60)),  # minutes
                    ('resolution_time', random.randint(30, 480)),  # minutes
                    ('escalation_rate', random.uniform(0.05, 0.25)),
                    ('reopen_rate', random.uniform(0.02, 0.15)),
                    ('spam_rate', random.uniform(0.01, 0.08))
                ]
                
                for metric_name, metric_value in metrics:
                    for channel in company['channels']:
                        # Add some channel-specific variation
                        channel_multiplier = random.uniform(0.8, 1.2)
                        final_value = metric_value * channel_multiplier
                        
                        cursor.execute(f"""
                            INSERT INTO {schema_name}.analytics 
                            (metric_name, metric_value, metric_date, channel)
                            VALUES (%s, %s, %s, %s)
                        """, (metric_name, final_value, date.date(), channel))
            
            conn.commit()
            cursor.close()
            conn.close()
            
            print(f"📊 Generated realistic analytics data for {company['name']}")
            
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
    print("2. Generate data for TechFlow Solutions only")
    print("3. Generate data for SocialMedia Pro only")
    print("4. Generate data for OmniChannel Corp only")
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
