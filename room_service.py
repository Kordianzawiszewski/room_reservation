from datetime import datetime

from sqlalchemy import select, exists
from sqlalchemy.orm import Session

from models import Reservation, Room


def find_available_rooms(db: Session, start: datetime, end: datetime, capacity: int | None = None):
    stmt = select(Room).where(
        ~exists().where(
            Reservation.room_id == Room.id,
            Reservation.start_time < end,
            Reservation.end_time > start
        )
    )

    if capacity is not None:
        stmt = stmt.where(Room.capacity >= capacity)

    return db.scalars(stmt).all()