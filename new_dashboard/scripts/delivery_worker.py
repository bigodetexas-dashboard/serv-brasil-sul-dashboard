"""
Delivery Worker - Background Processor
Continuously processes delivery queue and attempts FTP uploads
"""

import os
import sys
import time
from datetime import datetime
from dotenv import load_dotenv

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from repositories.delivery_repository import DeliveryQueueRepository
from utils.ftp_helpers import upload_spawn_request

# Load environment
load_dotenv()

# Configuration
POLL_INTERVAL = int(os.getenv("DELIVERY_WORKER_INTERVAL", "10"))  # seconds
BATCH_SIZE = int(os.getenv("DELIVERY_BATCH_SIZE", "10"))  # items per batch


def process_delivery(delivery: dict, repo: DeliveryQueueRepository) -> bool:
    """
    Process a single delivery

    Args:
        delivery: Delivery record from database
        repo: Repository instance

    Returns:
        True if successful, False otherwise
    """
    delivery_id = delivery["id"]
    item_code = delivery["item_code"]
    coordinates = delivery["coordinates"]

    print(f"[WORKER] Processing delivery #{delivery_id}: {item_code} to {coordinates}")

    try:
        # Mark as processing
        repo.start_processing(delivery_id)

        # Attempt FTP upload
        success = upload_spawn_request(item_code, coordinates)

        if success:
            # Mark as delivered
            repo.mark_delivered(delivery_id)
            print(f"[WORKER] ✅ Delivery #{delivery_id} successful")
            return True
        else:
            # Mark as failed (will retry if attempts remain)
            error_msg = "FTP upload failed"
            repo.mark_failed(delivery_id, error_msg)
            print(f"[WORKER] ❌ Delivery #{delivery_id} failed: {error_msg}")
            return False

    except Exception as e:
        # Mark as failed with error
        error_msg = f"Exception: {str(e)}"
        repo.mark_failed(delivery_id, error_msg)
        print(f"[WORKER] ❌ Delivery #{delivery_id} exception: {e}")
        return False


def worker_loop():
    """Main worker loop"""
    print("=" * 60)
    print("🚁 DELIVERY WORKER STARTED")
    print(f"Poll Interval: {POLL_INTERVAL}s")
    print(f"Batch Size: {BATCH_SIZE}")
    print("=" * 60)

    repo = DeliveryQueueRepository()

    while True:
        try:
            # Get pending deliveries
            deliveries = repo.get_pending_deliveries(limit=BATCH_SIZE)

            if deliveries:
                print(
                    f"\n[{datetime.now().strftime('%H:%M:%S')}] Found {len(deliveries)} pending deliveries"
                )

                success_count = 0
                fail_count = 0

                for delivery in deliveries:
                    if process_delivery(delivery, repo):
                        success_count += 1
                    else:
                        fail_count += 1

                    # Small delay between deliveries to avoid overwhelming FTP
                    time.sleep(1)

                print(f"[WORKER] Batch complete: {success_count} success, {fail_count} failed")
            else:
                # No deliveries, just show heartbeat
                print(f"[{datetime.now().strftime('%H:%M:%S')}] No pending deliveries")

            # Wait before next poll
            time.sleep(POLL_INTERVAL)

        except KeyboardInterrupt:
            print("\n[WORKER] Shutting down gracefully...")
            break
        except Exception as e:
            print(f"[WORKER] Error in main loop: {e}")
            # Continue running even if there's an error
            time.sleep(POLL_INTERVAL)


if __name__ == "__main__":
    # Check if DATABASE_URL is set
    if not os.getenv("DATABASE_URL"):
        print("❌ ERROR: DATABASE_URL not set in environment")
        print("This worker requires PostgreSQL to run")
        sys.exit(1)

    worker_loop()
