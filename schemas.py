from datetime import datetime, date, time
from typing import Literal

from pydantic import BaseModel, model_validator, Field, EmailStr


class RoomCreate(BaseModel):
    name: str | None = None
    room_number: str | None = None
    capacity: int = Field(gt=0)
    floor: int = Field(ge=-5, le=100)

    @model_validator(mode="after")
    def validate_name_or_number(self):
        if self.name is None and self.room_number is None:
            raise ValueError("Room must have either a name or room number")
        return self

class RoomUpdate(BaseModel):
    name: str | None = None
    room_number: str | None = None
    capacity: int | None = Field(default=None, gt=0)
    floor: int | None = Field(default=None, ge=-5, le=100)

class ReservationCreate(BaseModel):
   room_id: int = Field(gt=0)
   start_time: datetime
   end_time: datetime

class RoomResponse(BaseModel):
    id: int
    name: str | None = None
    room_number: str | None = None
    capacity: int
    floor: int

    model_config = {
        "from_attributes": True
    }

class ReservationResponse(BaseModel):
    id: int
    room_id: int
    start_time: datetime
    end_time: datetime
    user_id: int
    room: RoomResponse

    model_config = {
        "from_attributes": True
    }

class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8)

class UserResponse(BaseModel):
    id: int
    email: str
    role: str
    is_active: bool

    model_config = {
        "from_attributes": True
    }

class Token(BaseModel):
    access_token: str
    token_type: str

class ForgotPasswordRequest(BaseModel):
    email: EmailStr

class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str = Field(min_length=8)

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class RoomSearchIntent(BaseModel):
    intent: Literal["rooms_search"]
    start_time: datetime = Field(description="Start date and time of the requested room search.")
    end_time: datetime | None = Field(
        description=(
            "End date and time of the requested room search. "
            "If the user provides a time range such as 'from 12 to 13', "
            "this must be 13:00. Return null only if no end time or duration is provided."
        )
    )
    capacity: int | None = Field(default=None, gt=0)

    @model_validator(mode="after")
    def validate_time(self):
        if self.end_time is not None and self.end_time <= self.start_time:
            raise ValueError("End time must be after start time")
        return self

class RoomAvailabilityIntent(BaseModel):
    intent: Literal["room_availability"]
    room_identifier: str
    date: date
    check_time: time | None = Field(default=None, description="Specific time mentioned by the user. If the user asks about 12, return 12:00. Return null only when no specific time is mentioned.")

class AiSearchRequest(BaseModel):
    query: str

class AiRoomResponse(BaseModel):
    intent: Literal["rooms_search", "room_availability"]
    rooms: list[RoomResponse] | None = None
    available: bool | None = None
    free_slots: list[tuple[datetime, datetime]] | None = None
