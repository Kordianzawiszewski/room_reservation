from datetime import datetime

from pydantic import BaseModel, model_validator

class RoomCreate(BaseModel):
    name: str | None = None
    room_number: str | None = None
    capacity: int
    floor: int

    @model_validator(mode="after")
    def validate_name_or_number(self):
        if self.name is None and self.room_number is None:
            raise ValueError("Room must have either a name or room number")
        return self

class RoomUpdate(BaseModel):
    name: str | None = None
    room_number: str | None = None
    capacity: int | None = None
    floor: int | None = None

class ReservationCreate(BaseModel):
   room_id: int
   start_time: datetime
   end_time: datetime
   reserved_by: str