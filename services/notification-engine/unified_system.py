#!/usr/bin/env python3
"""
Unified Multi-Tenant Notification System
Handles notifications for multiple companies and routes to correct sockets
"""

import json
import logging
import os
import psycopg2
import psycopg2.extensions
from typing import Callable, Dict, Any, Optional, List
from datetime import datetime
import threading
import time
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(level=getattr(logging, os.getenv('LOG_LEVEL', 'INFO')))
logger = logging.getLogger(__name__)


class UnifiedNotificationSystem:
    """
    Unified notification system that handles multiple companies
    and routes notifications to the correct backend instances
    """
    
    def __init__(self):
        """Initialize the unified notification system."""
        self.connection_params = self._load_db_config_from_env()
        self.connection = None
        self.running = False
        self.listen_thread = None
        self.backend_connections = {}  # Store backend socket connections
        
    def _load_db_config_from_env(self) -> Dict[str, Any]:
        """Load database configuration from environment variables."""
        return {
            'host': os.getenv('DB_HOST', 'localhost'),
            'port': os.getenv('DB_PORT', '5432'),
            'database': os.getenv('DB_NAME', 'notify_postgres'),
            'user': os.getenv('DB_USER', 'postgres'),
            'password': os.getenv('DB_PASSWORD', '')
        }
    
    def register_backend(self, company_code: str, socketio_instance):
        """
        Register a backend instance for a company.
        
        Args:
            company_code: Company code (COMP_A, COMP_B, COMP_C)
            socketio_instance: Flask-SocketIO instance for that company
        """
        self.backend_connections[company_code] = socketio_instance
        logger.info(f"Registered backend for {company_code}")
    
    def unregister_backend(self, company_code: str):
        """Unregister a backend instance."""
        if company_code in self.backend_connections:
            del self.backend_connections[company_code]
            logger.info(f"Unregistered backend for {company_code}")
    
    def start_listening(self):
        """Start listening for notifications from all company schemas."""
        if self.running:
            logger.warning("Notification system is already running")
            return
        
        self.running = True
        self.listen_thread = threading.Thread(target=self._listen_loop, daemon=True)
        self.listen_thread.start()
        logger.info("Unified notification system started")
    
    def stop_listening(self):
        """Stop listening for notifications."""
        self.running = False
        if self.listen_thread:
            self.listen_thread.join(timeout=5)
        logger.info("Unified notification system stopped")
    
    def _listen_loop(self):
        """Main listening loop for notifications."""
        try:
            self.connection = psycopg2.connect(**self.connection_params)
            self.connection.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
            cursor = self.connection.cursor()
            
            # Listen to notification channels
            cursor.execute("LISTEN interaction_changes;")
            cursor.execute("LISTEN status_changes;")
            
            logger.info("🔔 Unified notification system listening for notifications...")
            
            while self.running:
                if self.connection.poll() == psycopg2.extensions.POLL_OK:
                    self.connection.poll()
                    while self.connection.notifies:
                        notify = self.connection.notifies.pop(0)
                        self._handle_notification(notify)
                
                time.sleep(0.1)
                
        except Exception as e:
            logger.error(f"❌ Notification listener error: {e}")
            if self.running:
                time.sleep(5)
                self._listen_loop()  # Restart on error
        finally:
            if self.connection:
                self.connection.close()
    
    def _handle_notification(self, notify):
        """Handle incoming notifications and route to correct backend."""
        try:
            data = json.loads(notify.payload)
            company_code = data.get('company')
            
            if not company_code:
                logger.warning("Notification without company code received")
                return
            
            # Route to the correct backend
            if company_code in self.backend_connections:
                backend = self.backend_connections[company_code]
                
                if notify.channel == 'interaction_changes':
                    backend.emit('new_engagement', data)
                    logger.info(f"📡 Routed new_engagement to {company_code}")
                elif notify.channel == 'status_changes':
                    backend.emit('status_update', data)
                    logger.info(f"📡 Routed status_update to {company_code}")
            else:
                logger.warning(f"No backend registered for company {company_code}")
                
        except json.JSONDecodeError:
            logger.error(f"❌ Invalid JSON in notification: {notify.payload}")
        except Exception as e:
            logger.error(f"❌ Error handling notification: {e}")


# Global instance
unified_notifier = UnifiedNotificationSystem()


class MultiTenantInteractionManager:
    """
    Multi-tenant interaction manager that handles different company schemas
    """
    
    def __init__(self, company_code: str = None):
        """
        Initialize the multi-tenant interaction manager.
        
        Args:
            company_code: Company code (COMP_A, COMP_B, COMP_C)
        """
        self.company_code = company_code or os.getenv('COMPANY_CODE', 'COMP_A')
        self.connection_params = self._load_db_config_from_env()
        self.schema_name = self._get_schema_name()
        
    def _load_db_config_from_env(self) -> Dict[str, Any]:
        """Load database configuration from environment variables."""
        return {
            'host': os.getenv('DB_HOST', 'localhost'),
            'port': os.getenv('DB_PORT', '5432'),
            'database': os.getenv('DB_NAME', 'notify_postgres'),
            'user': os.getenv('DB_USER', 'postgres'),
            'password': os.getenv('DB_PASSWORD', '')
        }
    
    def _get_schema_name(self) -> str:
        """Get the schema name for the company."""
        schema_mapping = {
            'COMP_A': 'company_a',
            'COMP_B': 'company_b',
            'COMP_C': 'company_c'
        }
        return schema_mapping.get(self.company_code, 'company_a')
    
    def get_connection(self):
        """Get a database connection."""
        return psycopg2.connect(**self.connection_params)
    
    def get_all_interactions(self) -> list:
        """
        Get all interactions for the company.
        
        Returns:
            List of interaction dictionaries
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            query = f"""
                SELECT id, channel, channel_interaction_id, user_identifier, 
                       status, created_at, updated_at, original_created_at,
                       engagement_id, entity_id, reference_id, is_replied,
                       is_delayed, is_spam, is_reopened, channel_closing_reason,
                       last_reply_id, last_reply_created_at, last_reply_direction,
                       frontend_json, text, sort_key, company_id
                FROM {self.schema_name}.eng_interactions
                ORDER BY created_at DESC
            """
            
            cursor.execute(query)
            columns = [desc[0] for desc in cursor.description]
            interactions = []
            
            for row in cursor.fetchall():
                interaction = dict(zip(columns, row))
                # Convert datetime objects to strings
                for key, value in interaction.items():
                    if isinstance(value, datetime):
                        interaction[key] = value.isoformat()
                interactions.append(interaction)
            
            return interactions
            
        except Exception as e:
            logger.error(f"Failed to get interactions: {e}")
            raise
        finally:
            cursor.close()
            conn.close()
    
    def create_interaction(self, interaction_data: Dict[str, Any]) -> int:
        """
        Create a new interaction in the company's schema.
        
        Args:
            interaction_data: Dictionary containing interaction data
            
        Returns:
            The ID of the created interaction
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # Prepare the insert query
            columns = list(interaction_data.keys())
            values = list(interaction_data.values())
            placeholders = ', '.join(['%s'] * len(values))
            
            query = f"""
                INSERT INTO {self.schema_name}.eng_interactions ({', '.join(columns)})
                VALUES ({placeholders})
                RETURNING id
            """
            
            cursor.execute(query, values)
            interaction_id = cursor.fetchone()[0]
            conn.commit()
            
            logger.info(f"Created interaction with ID: {interaction_id} in {self.schema_name}")
            return interaction_id
            
        except Exception as e:
            conn.rollback()
            logger.error(f"Failed to create interaction: {e}")
            raise
        finally:
            cursor.close()
            conn.close()
    
    def update_interaction_status(self, interaction_id: int, new_status: str) -> bool:
        """
        Update the status of an interaction.
        
        Args:
            interaction_id: The ID of the interaction to update
            new_status: The new status
            
        Returns:
            True if update was successful, False otherwise
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            query = f"""
                UPDATE {self.schema_name}.eng_interactions 
                SET status = %s, updated_at = CURRENT_TIMESTAMP
                WHERE id = %s
            """
            
            cursor.execute(query, (new_status, interaction_id))
            rows_affected = cursor.rowcount
            conn.commit()
            
            if rows_affected > 0:
                logger.info(f"Updated interaction {interaction_id} status to {new_status} in {self.schema_name}")
                return True
            else:
                logger.warning(f"No interaction found with ID: {interaction_id} in {self.schema_name}")
                return False
                
        except Exception as e:
            conn.rollback()
            logger.error(f"Failed to update interaction status: {e}")
            raise
        finally:
            cursor.close()
            conn.close()
    
    def get_interaction_by_id(self, interaction_id: int) -> Optional[Dict[str, Any]]:
        """
        Get a specific interaction by ID.
        
        Args:
            interaction_id: The ID of the interaction
            
        Returns:
            Interaction dictionary or None if not found
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            query = f"""
                SELECT id, channel, channel_interaction_id, user_identifier, 
                       status, created_at, updated_at, original_created_at,
                       engagement_id, entity_id, reference_id, is_replied,
                       is_delayed, is_spam, is_reopened, channel_closing_reason,
                       last_reply_id, last_reply_created_at, last_reply_direction,
                       frontend_json, text, sort_key, company_id
                FROM {self.schema_name}.eng_interactions
                WHERE id = %s
            """
            
            cursor.execute(query, (interaction_id,))
            row = cursor.fetchone()
            
            if row:
                columns = [desc[0] for desc in cursor.description]
                interaction = dict(zip(columns, row))
                # Convert datetime objects to strings
                for key, value in interaction.items():
                    if isinstance(value, datetime):
                        interaction[key] = value.isoformat()
                return interaction
            else:
                return None
                
        except Exception as e:
            logger.error(f"Failed to get interaction: {e}")
            raise
        finally:
            cursor.close()
            conn.close()
    
    def delete_interaction(self, interaction_id: int) -> bool:
        """
        Delete an interaction.
        
        Args:
            interaction_id: The ID of the interaction to delete
            
        Returns:
            True if deletion was successful, False otherwise
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            query = f"""
                DELETE FROM {self.schema_name}.eng_interactions 
                WHERE id = %s
            """
            
            cursor.execute(query, (interaction_id,))
            rows_affected = cursor.rowcount
            conn.commit()
            
            if rows_affected > 0:
                logger.info(f"Deleted interaction {interaction_id} from {self.schema_name}")
                return True
            else:
                logger.warning(f"No interaction found with ID: {interaction_id} in {self.schema_name}")
                return False
                
        except Exception as e:
            conn.rollback()
            logger.error(f"Failed to delete interaction: {e}")
            raise
        finally:
            cursor.close()
            conn.close()
    
    def get_company_stats(self) -> Dict[str, Any]:
        """
        Get company statistics.
        
        Returns:
            Dictionary containing company statistics
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # Get total interactions
            cursor.execute(f"SELECT COUNT(*) FROM {self.schema_name}.eng_interactions")
            total_interactions = cursor.fetchone()[0]
            
            # Get interactions by status
            cursor.execute(f"""
                SELECT status, COUNT(*) 
                FROM {self.schema_name}.eng_interactions 
                GROUP BY status
            """)
            status_counts = dict(cursor.fetchall())
            
            # Get interactions by channel
            cursor.execute(f"""
                SELECT channel, COUNT(*) 
                FROM {self.schema_name}.eng_interactions 
                GROUP BY channel
            """)
            channel_counts = dict(cursor.fetchall())
            
            return {
                'total_interactions': total_interactions,
                'status_counts': status_counts,
                'channel_counts': channel_counts,
                'company_code': self.company_code,
                'schema_name': self.schema_name
            }
            
        except Exception as e:
            logger.error(f"Failed to get company stats: {e}")
            raise
        finally:
            cursor.close()
            conn.close()
