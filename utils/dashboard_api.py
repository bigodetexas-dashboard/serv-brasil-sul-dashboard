import os
import aiohttp
import logging

DASHBOARD_Url = "http://127.0.0.1:5001/api/events/emit"
SECRET_KEY = os.getenv("SECRET_KEY")


async def send_dashboard_event(event_type: str, content: str, related_id: int = None):
    """
    Sends an event to the Dashboard API via HTTP POST.
    """
    if not SECRET_KEY:
        logging.warning("SECRET_KEY not set. Cannot send dashboard event.")
        return False

    headers = {"X-Bot-Secret": SECRET_KEY, "Content-Type": "application/json"}

    payload = {"type": event_type, "content": content, "related_id": related_id}

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                DASHBOARD_Url, json=payload, headers=headers
            ) as response:
                if response.status == 200:
                    return True
                else:
                    logging.error(
                        f"Dashboard API Error: {response.status} - {await response.text()}"
                    )
                    return False
    except Exception as e:
        logging.error(f"Failed to connect to Dashboard API: {e}")
        return False
