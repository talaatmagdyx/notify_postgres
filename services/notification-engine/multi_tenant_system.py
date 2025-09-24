#!/usr/bin/env python3
"""
Multi-Tenant PostgreSQL Notification System
Supports multiple companies with separate schemas
"""

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
