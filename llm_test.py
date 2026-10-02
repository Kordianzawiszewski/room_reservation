import json
import os
from datetime import datetime

import httpx
from dotenv import load_dotenv

from schemas import RoomSearchIntent

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

response = httpx.post(
  url="https://openrouter.ai/api/v1/chat/completions",
  headers={
    "Authorization": f"Bearer {OPENROUTER_API_KEY}",
  },
  json={
    "model": "openrouter/free",
    "messages": [
      {
        "role": "system",
        "content": f"Today's date is {datetime.now().date().isoformat()}"
      },
      {
        "role": "user",
        "content": "Find me a room tomorrow from 12 to 15 for 8 people."
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
              "type": "integer",
              "description": "capacity (number of people) of the room",
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

data = response.json()
parsed = json.loads(data["choices"][0]["message"]["content"])

intent = RoomSearchIntent.model_validate(parsed)

print(intent)
print(type(intent.start_time))
print(type(intent.capacity))