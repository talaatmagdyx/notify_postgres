"""
PostgreSQL Notification System for eng_interactions table
This module provides a comprehensive notification system using PostgreSQL LISTEN/NOTIFY
"""

import asyncio
import json
import logging
import os
import psycopg2
import psycopg2.extensions
from typing import Callable, Dict, Any, Optional
from datetime import datetime
import threading
import time
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(level=getattr(logging, os.getenv('LOG_LEVEL', 'INFO')))
logger = logging.getLogger(__name__)


class PostgreSQLNotifier:
    """
    A PostgreSQL notification listener that handles real-time notifications
    from the eng_interactions table changes.
    """
    
    def __init__(self, connection_params: Optional[Dict[str, Any]] = None):
        """
        Initialize the notifier with database connection parameters.
        
        Args:
            connection_params: Optional dictionary containing database connection parameters.
                              If None, will load from environment variables.
        """
        if connection_params is None:
            self.connection_params = self._load_db_config_from_env()
        else:
            self.connection_params = connection_params
        
        self.connection = None
        self.listeners = {}
        self.running = False
        self.listen_thread = None
    
    def _load_db_config_from_env(self) -> Dict[str, Any]:
        """Load database configuration from environment variables."""
        return {
            'host': os.getenv('DB_HOST', 'localhost'),
            'port': int(os.getenv('DB_PORT', 5432)),
            'database': os.getenv('DB_NAME', 'notify_postgres'),
            'user': os.getenv('DB_USER', 'postgres'),
            'password': os.getenv('DB_PASSWORD', 'password')
        }
        
    def connect(self):
        """Establish connection to PostgreSQL database."""
        try:
            self.connection = psycopg2.connect(**self.connection_params)
            self.connection.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
            logger.info("Connected to PostgreSQL database")
        except Exception as e:
            logger.error(f"Failed to connect to database: {e}")
            raise
    
    def disconnect(self):
        """Close the database connection."""
        if self.connection:
            self.connection.close()
            logger.info("Disconnected from PostgreSQL database")
    
    def add_listener(self, channel: str, callback: Callable[[Dict[str, Any]], None]):
        """
        Add a listener for a specific notification channel.
        
        Args:
            channel: The notification channel name
            callback: Function to call when notification is received
        """
        self.listeners[channel] = callback
        logger.info(f"Added listener for channel: {channel}")
    
    def remove_listener(self, channel: str):
        """Remove a listener for a specific channel."""
        if channel in self.listeners:
            del self.listeners[channel]
            logger.info(f"Removed listener for channel: {channel}")
    
    def start_listening(self):
        """Start listening for notifications in a separate thread."""
        if self.running:
            logger.warning("Already listening for notifications")
            return
        
        if not self.connection:
            self.connect()
        
        self.running = True
        self.listen_thread = threading.Thread(target=self._listen_loop, daemon=True)
        self.listen_thread.start()
        logger.info("Started listening for notifications")
    
    def stop_listening(self):
        """Stop listening for notifications."""
        self.running = False
        if self.listen_thread:
            self.listen_thread.join()
        logger.info("Stopped listening for notifications")
    
    def _listen_loop(self):
        """Main listening loop that runs in a separate thread."""
        cursor = self.connection.cursor()
        
        # Listen to all channels that have listeners
        for channel in self.listeners.keys():
            cursor.execute(f"LISTEN {channel};")
            logger.info(f"Listening to channel: {channel}")
        
        try:
            while self.running:
                # Check for notifications with a timeout
                if self.connection.poll() == psycopg2.extensions.POLL_OK:
                    self.connection.poll()
                    
                    while self.connection.notifies:
                        notify = self.connection.notifies.pop(0)
                        self._handle_notification(notify)
                else:
                    time.sleep(0.1)  # Small delay to prevent busy waiting
                    
        except Exception as e:
            logger.error(f"Error in listen loop: {e}")
        finally:
            cursor.close()
    
    def _handle_notification(self, notify):
        """Handle incoming notification."""
        try:
            # Parse the notification payload
            payload = json.loads(notify.payload)
            channel = notify.channel
            
            logger.info(f"Received notification on channel '{channel}': {payload}")
            
            # Call the appropriate callback
            if channel in self.listeners:
                self.listeners[channel](payload)
            else:
                logger.warning(f"No listener registered for channel: {channel}")
                
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse notification payload: {e}")
        except Exception as e:
            logger.error(f"Error handling notification: {e}")


class InteractionManager:
    """
    Manager class for handling eng_interactions table operations
    and notifications.
    """
    
    def __init__(self, connection_params: Optional[Dict[str, Any]] = None):
        """
        Initialize the interaction manager.
        
        Args:
            connection_params: Optional database connection parameters.
                              If None, will load from environment variables.
        """
        if connection_params is None:
            self.connection_params = self._load_db_config_from_env()
        else:
            self.connection_params = connection_params
        
        self.notifier = PostgreSQLNotifier(self.connection_params)
        self._setup_notification_handlers()
    
    def _load_db_config_from_env(self) -> Dict[str, Any]:
        """Load database configuration from environment variables."""
        return {
            'host': os.getenv('DB_HOST', 'localhost'),
            'port': int(os.getenv('DB_PORT', 5432)),
            'database': os.getenv('DB_NAME', 'notify_postgres'),
            'user': os.getenv('DB_USER', 'postgres'),
            'password': os.getenv('DB_PASSWORD', 'password')
        }
    
    def _setup_notification_handlers(self):
        """Setup default notification handlers."""
        self.notifier.add_listener('interaction_changes', self._handle_interaction_change)
        self.notifier.add_listener('status_changes', self._handle_status_change)
    
    def _handle_interaction_change(self, payload: Dict[str, Any]):
        """Handle interaction change notifications."""
        operation = payload.get('operation')
        interaction_id = payload.get('interaction_id')
        channel = payload.get('channel')
        user_identifier = payload.get('user_identifier')
        
        logger.info(f"Interaction {operation}: ID={interaction_id}, Channel={channel}, User={user_identifier}")
        
        # Here you can add custom logic for handling interaction changes
        # For example, updating a dashboard, sending alerts, etc.
    
    def _handle_status_change(self, payload: Dict[str, Any]):
        """Handle status change notifications."""
        interaction_id = payload.get('interaction_id')
        old_status = payload.get('old_status')
        new_status = payload.get('new_status')
        channel = payload.get('channel')
        
        logger.info(f"Status change: ID={interaction_id}, {old_status} -> {new_status} on {channel}")
        
        # Here you can add custom logic for handling status changes
        # For example, triggering workflows, sending notifications to agents, etc.
    
    def start_notifications(self):
        """Start listening for notifications."""
        self.notifier.start_listening()
    
    def stop_notifications(self):
        """Stop listening for notifications."""
        self.notifier.stop_listening()
    
    def create_interaction(self, interaction_data: Dict[str, Any]) -> int:
        """
        Create a new interaction in the database.
        
        Args:
            interaction_data: Dictionary containing interaction data
            
        Returns:
            The ID of the created interaction
        """
        conn = psycopg2.connect(**self.connection_params)
        cursor = conn.cursor()
        
        try:
            # Prepare the insert query
            columns = list(interaction_data.keys())
            values = list(interaction_data.values())
            placeholders = ', '.join(['%s'] * len(values))
            
            query = f"""
                INSERT INTO eng_interactions ({', '.join(columns)})
                VALUES ({placeholders})
                RETURNING id
            """
            
            cursor.execute(query, values)
            interaction_id = cursor.fetchone()[0]
            conn.commit()
            
            logger.info(f"Created interaction with ID: {interaction_id}")
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
        conn = psycopg2.connect(**self.connection_params)
        cursor = conn.cursor()
        
        try:
            query = """
                UPDATE eng_interactions 
                SET status = %s, updated_at = CURRENT_TIMESTAMP
                WHERE id = %s
            """
            
            cursor.execute(query, (new_status, interaction_id))
            rows_affected = cursor.rowcount
            conn.commit()
            
            if rows_affected > 0:
                logger.info(f"Updated interaction {interaction_id} status to {new_status}")
                return True
            else:
                logger.warning(f"No interaction found with ID: {interaction_id}")
                return False
                
        except Exception as e:
            conn.rollback()
            logger.error(f"Failed to update interaction status: {e}")
            raise
        finally:
            cursor.close()
            conn.close()
    
    def get_interaction(self, interaction_id: int) -> Optional[Dict[str, Any]]:
        """
        Get an interaction by ID.
        
        Args:
            interaction_id: The ID of the interaction
            
        Returns:
            Dictionary containing interaction data or None if not found
        """
        conn = psycopg2.connect(**self.connection_params)
        cursor = conn.cursor()
        
        try:
            query = "SELECT * FROM eng_interactions WHERE id = %s"
            cursor.execute(query, (interaction_id,))
            
            row = cursor.fetchone()
            if row:
                columns = [desc[0] for desc in cursor.description]
                return dict(zip(columns, row))
            return None
            
        except Exception as e:
            logger.error(f"Failed to get interaction: {e}")
            raise
        finally:
            cursor.close()
            conn.close()
    
    def get_interactions_by_channel(self, channel: str, limit: int = 100) -> list:
        """
        Get interactions by channel.
        
        Args:
            channel: The channel name
            limit: Maximum number of interactions to return
            
        Returns:
            List of interaction dictionaries
        """
        conn = psycopg2.connect(**self.connection_params)
        cursor = conn.cursor()
        
        try:
            query = """
                SELECT * FROM eng_interactions 
                WHERE channel = %s 
                ORDER BY created_at DESC 
                LIMIT %s
            """
            cursor.execute(query, (channel, limit))
            
            columns = [desc[0] for desc in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]
            
        except Exception as e:
            logger.error(f"Failed to get interactions by channel: {e}")
            raise
        finally:
            cursor.close()
            conn.close()
