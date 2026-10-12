from uuid import uuid4

import httpx

def send_reservation_created_webhook(reservation_id, user_id, email, room_name, start_time, end_time):
    payload = {
        "event_id": str(uuid4()),
        "event_type": "reservation.created",
        "reservation_id": reservation_id,
        "user_id": user_id,
        "email": email,
        "room_name": room_name,
        "start_time": start_time.isoformat(),
        "end_time": end_time.isoformat(),
    }

    response = httpx.post(
        "http://n8n:5678/webhook/room-booking-test",
        json=payload,
        timeout=5.0
    )

    response.raise_for_status()

def send_reset_password_link_webhook(email, token):
    payload = {
        "event_id": str(uuid4()),
        "event_type": "password.reset.requested",
        "email": email,
        "token": token
    }

    response = httpx.post(
        "http://n8n:5678/webhook/room-booking-test",
        json=payload,
        timeout=5.0
    )

    response.raise_for_status()

