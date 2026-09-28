from datetime import datetime

from pydantic import BaseModel, model_validator, Field


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

    model_config = {
        "from_attributes": True
    }

class UserCreate(BaseModel):
    email: str
    password: str

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

class LoginRequest(BaseModel):
    email: str
    password: str

class ReservationWebhook(BaseModel):
    event_id: str
    event_type: str
    reservation_id: int
    user_id: int

class N8nTestRequest(BaseModel):
    reservation_id: int
    user_id: int






