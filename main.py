from datetime import date, time, datetime, timedelta

import httpx
from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy import select, delete, exists

from db import get_db
from models import Room, Reservation, User
from schemas import RoomCreate, RoomUpdate, ReservationCreate, RoomResponse, ReservationResponse, UserResponse, \
    UserCreate, Token, LoginRequest
from sqlalchemy.orm import Session

from security import hash_password, verify_password, create_access_token, get_current_user, require_admin

app = FastAPI()

@app.get("/rooms", response_model=list[RoomResponse])
def get_rooms(db: Session = Depends(get_db)):
    stmt = select(Room)

    return db.scalars(stmt).all()

@app.get("/rooms/available", response_model=list[RoomResponse])
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

@app.get("/rooms/{room_id}", response_model=RoomResponse)
def get_room(room_id: int, db: Session = Depends(get_db)):
    stmt = select(Room).where(Room.id == room_id)
    room = db.scalars(stmt).one_or_none()

    if room is None:
        raise HTTPException(status_code=404, detail="Room not found")

    return room

@app.post("/rooms", response_model=RoomResponse)
def create_room(room: RoomCreate, current_admin: User = Depends(require_admin) , db: Session = Depends(get_db)):
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
def delete_room(room_id: int, current_user: User = Depends(require_admin),db: Session = Depends(get_db)):
    stmt = select(Room).where(Room.id == room_id)
    room = db.scalars(stmt).one_or_none()

    if room is None:
        raise HTTPException(status_code=404, detail="Room not found")

    db.delete(room)
    db.commit()

    return {"message": "Room deleted"}

@app.patch("/rooms/{room_id}", response_model=RoomResponse)
def update_room(room_id: int, room_update: RoomUpdate, current_user: User = Depends(require_admin), db: Session = Depends(get_db)):
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

@app.post("/reservations", response_model=ReservationResponse)
def create_reservation(reservation: ReservationCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
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
        user_id=current_user.id,
    )

    db.add(db_reservation)
    db.commit()
    db.refresh(db_reservation)

    return db_reservation

@app.delete("/reservations/{reservation_id}")
def cancel_reservation(reservation_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    reservation_stmt = select(Reservation).where(Reservation.id == reservation_id)
    existing_reservation = db.scalars(reservation_stmt).one_or_none()

    if existing_reservation is None:
        raise HTTPException(status_code=404, detail="Reservation not found")

    if existing_reservation.user_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="You can only cancel your own reservations")

    db.delete(existing_reservation)
    db.commit()

    return {
        "message": "Reservation canceled",
    }

@app.get("/rooms/{room_id}/reservations", response_model=list[ReservationResponse])
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

@app.post("/register", response_model=UserResponse)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    stmt = select(User).where(User.email == user.email)
    existing_user = db.scalars(stmt).one_or_none()

    if existing_user is not None:
        raise HTTPException(status_code=409, detail="User with this email already exists")

    hashed_password = hash_password(user.password)

    new_user = User(
        email=user.email,
        password_hash=hashed_password
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user

@app.post("/login", response_model=Token)
def login(login_data: LoginRequest, db: Session = Depends(get_db)):
    stmt = select(User).where(User.email == login_data.email)
    user = db.scalars(stmt).one_or_none()

    if user is None:
        raise HTTPException(status_code=401, detail="Invalid email or password")

    check_password = verify_password(login_data.password, user.password_hash)

    if not check_password:
        raise HTTPException(status_code=401, detail="Invalid email or password")

    token = create_access_token(user.id)

    return {
        "access_token": token,
        "token_type": "bearer",
    }

@app.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user

@app.get("/external")
async def get_external_data():
    async with httpx.AsyncClient() as client:
        response = await client.get("https://httpbin.org/get")

    return response.json()










