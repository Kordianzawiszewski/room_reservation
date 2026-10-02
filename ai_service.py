import json
import os
from datetime import datetime

import httpx
from dotenv import load_dotenv

from schemas import RoomSearchIntent

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

def generate_room_search(query: str) -> RoomSearchIntent:
    if OPENROUTER_API_KEY is None:
        raise RuntimeError("OPENROUTER_API_KEY is not configured")

    response = httpx.post(
        url="https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        },
        timeout=10,
        json={
            "model": "openrouter/free",
            "messages": [
                {
                    "role": "system",
                    "content": f"""
                        You extract room search parameters from the user's query.
                    
                        Today's date is {datetime.now().date().isoformat()}
                        
                        Rules:
                        - Resolve relative dates such as "today", "tomorrow", "next Monday" using today's date.
                        - Return full ISO 8601 datetimes for start_time and end_time.
                        - Do not invent missing values.
                        - If capacity is not provided, return null.
                        - Return only data matching the provided schema.
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
                    "schema": {
                        "type": "object",
                        "properties": {
                            "start_time": {
                                "type": "string",
                                "description": "date and time of start room booking",
                            },
                            "end_time": {
                                "type": "string",
                                "description": "date and time of end room booking",
                            },
                            "capacity": {
                                "type": ["integer", "null"],
                                "description": "capacity (number of people) of the room, or null if not provided",
                            },
                        },
                        "required": [
                            "start_time",
                            "end_time",
                            "capacity"
                        ],
                        "additionalProperties": False,
                    },
                }
            },
            "provider": {
                "require_parameters": True
            }
        }
    )

    print(response.status_code)
    print(response.text)
    response.raise_for_status()

    data = response.json()
    parsed = json.loads(data["choices"][0]["message"]["content"])

    intent = RoomSearchIntent.model_validate(parsed)

    return intent