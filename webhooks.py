from uuid import uuid4

import httpx

def send_reservation_created_webhook(reservation_id, user_id):
    payload = {
        "event_id": str(uuid4()),
        "event_type": "reservation.created",
        "reservation_id": reservation_id,
        "user_id": user_id
    }

    response = httpx.post(
        "http://n8n:5678/webhook/room-booking-test",
        json=payload,
        timeout=5.0
    )

    response.raise_for_status()

