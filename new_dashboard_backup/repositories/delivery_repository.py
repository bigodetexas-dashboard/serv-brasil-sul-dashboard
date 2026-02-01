"""
Delivery Queue Repository
Manages asynchronous item delivery queue with retry logic
"""

from repositories.base_repository import BaseRepository
from typing import List, Dict, Optional
from datetime import datetime


class DeliveryQueueRepository(BaseRepository):
    """Repository for managing delivery queue operations"""

    def add_to_queue(
        self,
        discord_id: str,
        item_name: str,
        item_code: str,
        quantity: int = 1,
        coordinates: Optional[str] = None,
        purchase_id: Optional[int] = None,
        priority: int = 0,
    ) -> int:
        """
        Add an item to the delivery queue

        Args:
            discord_id: User's Discord ID
            item_name: Display name of item
            item_code: DayZ class name
            quantity: Number of items
            coordinates: Spawn coordinates "X Y Z"
            purchase_id: Link to transaction
            priority: Higher = process first

        Returns:
            Delivery queue ID
        """
        query = """
            SELECT queue_delivery(?, ?, ?, ?, ?, ?)
        """
        result = self.execute_query(
            query, (discord_id, item_name, item_code, quantity, coordinates, purchase_id)
        )

        if result and len(result) > 0:
            return result[0]["queue_delivery"]
        return None

    def get_pending_deliveries(self, limit: int = 10) -> List[Dict]:
        """
        Get deliveries ready to process

        Args:
            limit: Maximum number to fetch

        Returns:
            List of pending deliveries
        """
        query = """
            SELECT * FROM v_deliveries_ready
            LIMIT ?
        """
        return self.execute_query(query, (limit,))

    def start_processing(self, delivery_id: int) -> bool:
        """
        Mark delivery as processing

        Args:
            delivery_id: ID of delivery

        Returns:
            True if successful
        """
        query = "SELECT start_delivery_processing(?)"
        result = self.execute_query(query, (delivery_id,))
        return bool(result)

    def mark_delivered(self, delivery_id: int) -> bool:
        """
        Mark delivery as successfully delivered

        Args:
            delivery_id: ID of delivery

        Returns:
            True if successful
        """
        query = "SELECT mark_delivery_success(?)"
        result = self.execute_query(query, (delivery_id,))
        return bool(result)

    def mark_failed(self, delivery_id: int, error_message: str) -> bool:
        """
        Mark delivery as failed (will retry if attempts remain)

        Args:
            delivery_id: ID of delivery
            error_message: Error description

        Returns:
            True if successful
        """
        query = "SELECT mark_delivery_failed(?, ?)"
        result = self.execute_query(query, (delivery_id, error_message))
        return bool(result)

    def get_user_deliveries(
        self, discord_id: str, limit: int = 50, status: Optional[str] = None
    ) -> List[Dict]:
        """
        Get delivery history for a user

        Args:
            discord_id: User's Discord ID
            limit: Maximum results
            status: Filter by status (pending, delivered, failed)

        Returns:
            List of deliveries
        """
        if status:
            query = """
                SELECT * FROM v_user_delivery_history
                WHERE discord_id = ? AND status = ?
                ORDER BY created_at DESC
                LIMIT ?
            """
            return self.execute_query(query, (discord_id, status, limit))
        else:
            query = """
                SELECT * FROM v_user_delivery_history
                WHERE discord_id = ?
                ORDER BY created_at DESC
                LIMIT ?
            """
            return self.execute_query(query, (discord_id, limit))

    def get_delivery_stats(self, discord_id: Optional[str] = None) -> Dict:
        """
        Get delivery statistics

        Args:
            discord_id: Optional user filter

        Returns:
            Stats dictionary
        """
        if discord_id:
            query = """
                SELECT
                    COUNT(*) as total,
                    COUNT(*) FILTER (WHERE status = 'delivered') as delivered,
                    COUNT(*) FILTER (WHERE status = 'pending') as pending,
                    COUNT(*) FILTER (WHERE status = 'failed') as failed,
                    AVG(EXTRACT(EPOCH FROM (processed_at - created_at))) as avg_delivery_time_seconds
                FROM delivery_queue
                WHERE discord_id = ?
            """
            result = self.execute_query(query, (discord_id,))
        else:
            query = """
                SELECT
                    COUNT(*) as total,
                    COUNT(*) FILTER (WHERE status = 'delivered') as delivered,
                    COUNT(*) FILTER (WHERE status = 'pending') as pending,
                    COUNT(*) FILTER (WHERE status = 'failed') as failed,
                    AVG(EXTRACT(EPOCH FROM (processed_at - created_at))) as avg_delivery_time_seconds
                FROM delivery_queue
            """
            result = self.execute_query(query)

        if result and len(result) > 0:
            return result[0]
        return {
            "total": 0,
            "delivered": 0,
            "pending": 0,
            "failed": 0,
            "avg_delivery_time_seconds": 0,
        }

    def cleanup_old_deliveries(self, days: int = 30) -> int:
        """
        Delete old delivered/failed deliveries

        Args:
            days: Keep deliveries from last N days

        Returns:
            Number of deleted records
        """
        query = """
            DELETE FROM delivery_queue
            WHERE status IN ('delivered', 'failed')
              AND processed_at < CURRENT_TIMESTAMP - INTERVAL '? days'
        """
        self.execute_query(query, (days,))
        # Note: execute_query doesn't return rowcount, would need modification
        return 0  # Placeholder
