from datetime import date, time, datetime, timedelta

from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy import select, delete, exists

from db import get_db
from models import Room, Reservation
from schemas import RoomCreate, RoomUpdate, ReservationCreate
from sqlalchemy.orm import Session

app = FastAPI()

@app.get("/rooms")
def get_rooms(db: Session = Depends(get_db)):
    stmt = select(Room)

    return db.scalars(stmt).all()

@app.get("/rooms/{room_id}")
def get_room(room_id: int, db: Session = Depends(get_db)):
    stmt = select(Room).where(Room.id == room_id)
    room = db.scalars(stmt).one_or_none()

    if room is None:
        raise HTTPException(status_code=404, detail="Room not found")

    return room

@app.post("/rooms")
def create_room(room: RoomCreate, db: Session = Depends(get_db)):
    db_room = Room(
        name=room.name,
        room_number=room.room_number,
        capacity=room.capacity,
        floor=room.floor,
    )

    db.add(db_room)
    db.commit()
    db.refresh(db_room)

    return db_room

@app.delete("/rooms/{room_id}")
def delete_room(room_id: int, db: Session = Depends(get_db)):
    stmt = select(Room).where(Room.id == room_id)
    room = db.scalars(stmt).one_or_none()

    if room is None:
        raise HTTPException(status_code=404, detail="Room not found")

    db.delete(room)
    db.commit()

    return {"message": "Room deleted"}

@app.get("/rooms/available")
def get_available_rooms(start: datetime, end: datetime, db: Session = Depends(get_db)):
    if start >= end:
        raise HTTPException(status_code=400, detail="Start time must be before end time")

    stmt = select(Room).where(
        ~exists().where(
            Reservation.room_id == Room.id,
            Reservation.start_time < end,
            Reservation.end_time > start
        )
    )

    return db.scalars(stmt).all()

@app.patch("/rooms/{room_id}")
def update_room(room_id: int, room_update: RoomUpdate, db: Session = Depends(get_db)):
    stmt = select(Room).where(Room.id == room_id)
    room = db.scalars(stmt).one_or_none()

    if room is None:
        raise HTTPException(status_code=404, detail="Room not found")

    update_data = room_update.model_dump(exclude_unset=True)

    new_name = update_data.get("name", room.name)
    new_room_number = update_data.get("room_number", room.room_number)

    if new_name is None and new_room_number is None:
        raise HTTPException(
            status_code=422,
            detail="Room must have either a name or room number"
        )

    for field, value in update_data.items():
        setattr(room, field, value)

    db.commit()
    db.refresh(room)

    return room

@app.post("/reservations")
def create_reservation(reservation: ReservationCreate, db: Session = Depends(get_db)):
    stmt = select(Room).where(Room.id == reservation.room_id)
    room = db.scalars(stmt).one_or_none()

    if room is None:
        raise HTTPException(status_code=404, detail="Room not found")

    if reservation.start_time >= reservation.end_time:
        raise HTTPException(status_code=400, detail="Start time must be before end time")

    stmt_reservation = select(Reservation).where(
        Reservation.room_id == reservation.room_id,
        Reservation.start_time < reservation.end_time,
        Reservation.end_time > reservation.start_time,
    )

    existing_reservation = db.scalars(stmt_reservation).first()

    if existing_reservation is not None:
        raise HTTPException(status_code=409, detail="Room already reserved in this time range")

    db_reservation = Reservation(
        room_id=reservation.room_id,
        start_time=reservation.start_time,
        end_time=reservation.end_time,
        reserved_by=reservation.reserved_by,
    )

    db.add(db_reservation)
    db.commit()
    db.refresh(db_reservation)

    return db_reservation

@app.get("/rooms/{room_id}/reservations")
def get_room_reservations(room_id: int, date_filter: date | None = None, db: Session = Depends(get_db)):
    room_stmt = select(Room).where(Room.id == room_id)
    room = db.scalars(room_stmt).one_or_none()

    if room is None:
        raise HTTPException(status_code=404, detail="Room not found")

    if date_filter:
        day_start = datetime.combine(date_filter, time.min)
        day_next = day_start + timedelta(days=1)

        reservations_stmt = select(Reservation).where(
            Reservation.room_id == room_id,
            Reservation.start_time < day_next,
            Reservation.end_time > day_start
        )
    else:
        reservations_stmt = select(Reservation).where(Reservation.room_id == room_id)

    return db.scalars(reservations_stmt).all()


















