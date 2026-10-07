import json
import os
from datetime import datetime

import httpx
from dotenv import load_dotenv
from pydantic import TypeAdapter

from schemas import RoomSearchIntent, RoomAvailabilityIntent

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

RoomIntent = RoomSearchIntent | RoomAvailabilityIntent
room_intent_adapter = TypeAdapter(RoomIntent)

room_intent_schema = room_intent_adapter.json_schema()

def generate_room_search(query: str) -> RoomIntent:
    if OPENROUTER_API_KEY is None:
        raise RuntimeError("OPENROUTER_API_KEY is not configured")

    response = httpx.post(
        url="https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        },
        timeout=10,
        json={
            "model": "dots-studio/dots-3-note-preview:free",
            "messages": [
                {
                    "role": "system",
                    "content": f"""
                        You extract room search parameters from the user's query.
                        
                        Today's date is {datetime.now().date().isoformat()}.
                        
                        Intent rules:
                        
                        rooms_search:
                        - Use when the user wants to find any room and does not identify a specific room.
                        - If the user gives a time range, use the first time as start_time and the second as end_time.
                        - If no end time or duration is provided, set end_time to null.
                        - If capacity is not provided, set capacity to null.
                        
                        room_availability:
                        - Use when the user identifies one specific room by name or room number.
                        - If the user asks about a specific time, set check_time to that time.
                        - If the user asks for availability for the whole day, set check_time to null.
                        - Never invent a room name or room number.
                        
                        General:
                        - Resolve relative dates such as "today", "tomorrow", or "next Monday" using today's date.
                        - Return full ISO 8601 datetimes for start_time and end_time.
                        - Do not invent missing values.
                        - Return only data matching the provided schema.
                        
                        Examples:
                        - "Find me a room tomorrow from 12 to 15" -> rooms_search
                        - "When is room 1 available tomorrow?" -> room_availability
                    """
                },
                {
                    "role": "user",
                    "content": query
                }
            ],
            "response_format": {
                "type": "json_schema",
                "json_schema": {
                    "name": "room_booking",
                    "strict": True,
                    "schema": room_intent_schema
                }
            },
            "provider": {
                "require_parameters": True
            }
        }
    )

    response.raise_for_status()

    data = response.json()
    parsed = json.loads(data["choices"][0]["message"]["content"])

    print(parsed)
    intent = room_intent_adapter.validate_python(parsed)

    return intent