import logging
import os
from datetime import date, time, datetime, timedelta

import google_auth_oauthlib
import httpx
from fastapi import Depends, FastAPI, HTTPException, Header, Request
from googleapiclient.errors import HttpError
from sqlalchemy import select, exists

import webhooks
from db import get_db
from models import Room, Reservation, User, GoogleOAuthState, GoogleCalendarConnection, WebhookEvent
from schemas import RoomCreate, RoomUpdate, ReservationCreate, RoomResponse, ReservationResponse, UserResponse, \
    UserCreate, Token, LoginRequest, ReservationWebhook, N8nTestRequest
from sqlalchemy.orm import Session

from security import hash_password, verify_password, create_access_token, get_current_user, require_admin, \
    verify_webhook_signature
import google_calendar

logger = logging.getLogger(__name__)
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

    calendar_conn_stmt = select(GoogleCalendarConnection).where(GoogleCalendarConnection.user_id == current_user.id)
    connection = db.scalars(calendar_conn_stmt).one_or_none()

    if connection is not None:
        try:
            calendar_service = google_calendar.get_calendar_service(connection, db)

            created_event = google_calendar.create_calendar_event(
                calendar_service,
                f"Reservation: Room {room.name}",
                reservation.start_time,
                reservation.end_time,
            )

            db_reservation.google_event_id = created_event["id"]
            db.commit()

        except HttpError:
            logger.exception("Calendar sync failed")
        except RuntimeError:
            logger.exception("Google Calendar connection requires reconnect")

    try:
        webhooks.send_reservation_created_webhook(db_reservation.id, current_user.id)
    except httpx.HTTPError:
        logger.exception("Webhook sending failed")

    return db_reservation

@app.delete("/reservations/{reservation_id}")
def cancel_reservation(reservation_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    reservation_stmt = select(Reservation).where(Reservation.id == reservation_id)
    existing_reservation = db.scalars(reservation_stmt).one_or_none()

    if existing_reservation is None:
        raise HTTPException(status_code=404, detail="Reservation not found")

    if existing_reservation.user_id != current_user.id and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="You can only cancel your own reservations")

    google_event_id = existing_reservation.google_event_id

    calendar_conn_stmt = select(GoogleCalendarConnection).where(GoogleCalendarConnection.user_id == existing_reservation.user_id)
    connection = db.scalars(calendar_conn_stmt).one_or_none()

    db.delete(existing_reservation)
    db.commit()

    if google_event_id is not None and connection is not None:
        try:
            calendar_service = google_calendar.get_calendar_service(connection, db)

            google_calendar.delete_calendar_event(calendar_service, google_event_id)
        except HttpError:
            logger.exception("Calendar sync failed")
        except RuntimeError:
            logger.exception("Google Calendar connection requires reconnect")

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


@app.get("/integrations/google/connect")
def connect_google_calendar(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    stmt = select(GoogleOAuthState).where(GoogleOAuthState.user_id == current_user.id)
    existing_state = db.scalars(stmt).one_or_none()

    authorization_url, oauth_state, code_verifier = google_calendar.get_google_authorization_url()
    expires_at = datetime.utcnow() + timedelta(minutes=10)

    if existing_state is not None:
        existing_state.state = oauth_state
        existing_state.code_verifier = code_verifier
        existing_state.expires_at = expires_at
    else:
        new_state = GoogleOAuthState(
            state=oauth_state,
            user_id=current_user.id,
            expires_at=expires_at,
            code_verifier=code_verifier
        )

        db.add(new_state)

    db.commit()

    return {
        "authorization_url": authorization_url,
    }

@app.get("/integrations/google/callback")
def google_callback(code: str, state: str, db: Session = Depends(get_db)):
    stmt = select(GoogleOAuthState).where(GoogleOAuthState.state == state)
    existing_state = db.scalars(stmt).one_or_none()

    if existing_state is None:
        raise HTTPException(status_code=400, detail="Invalid OAuth state")

    if existing_state.expires_at < datetime.utcnow():
        db.delete(existing_state)
        db.commit()

        raise HTTPException(status_code=400, detail="OAuth state expired")

    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        'credentials_web.json',
        scopes=google_calendar.SCOPES,
        state=state,
        code_verifier=existing_state.code_verifier
    )

    flow.redirect_uri = "http://localhost:8000/integrations/google/callback"

    flow.fetch_token(code=code)

    credentials = flow.credentials

    conn_stmt = select(GoogleCalendarConnection).where(GoogleCalendarConnection.user_id == existing_state.user_id)
    existing_conn = db.scalars(conn_stmt).one_or_none()

    if existing_conn is not None:
        existing_conn.access_token = credentials.token
        existing_conn.token_expiry = credentials.expiry

        if credentials.refresh_token is not None:
            existing_conn.refresh_token = credentials.refresh_token
    else:
        google_calendar_conn = GoogleCalendarConnection(
            user_id=existing_state.user_id,
            access_token=credentials.token,
            refresh_token=credentials.refresh_token,
            token_expiry=credentials.expiry
        )

        db.add(google_calendar_conn)

    db.delete(existing_state)
    db.commit()

    return {
        "message": "Google Calendar connected"
    }

@app.get("/integrations/google/status")
def get_google_integration_status(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    stmt = select(GoogleCalendarConnection).where(GoogleCalendarConnection.user_id == current_user.id)
    connection = db.scalars(stmt).one_or_none()

    return {
        "connected": connection is not None
    }

@app.delete("/integrations/google")
def disconnect_google(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    stmt = select(GoogleCalendarConnection).where(GoogleCalendarConnection.user_id == current_user.id)
    connection = db.scalars(stmt).one_or_none()

    if connection is not None:
        db.delete(connection)
        db.commit()
    else:
        raise HTTPException(status_code=404, detail="Connection not found")

    return {
        "message": "Connection deleted"
    }

@app.post("/webhooks/reservations")
async def receive_information_webhook(request: Request, webhook: ReservationWebhook, db: Session = Depends(get_db), x_webhook_signature: str = Header(...)):
    raw_body = await request.body()
    secret = os.getenv("WEBHOOK_SECRET")

    if secret is None:
        raise RuntimeError("WEBHOOK_SECRET is not configured")

    if not verify_webhook_signature(raw_body, secret, x_webhook_signature):
        raise HTTPException(status_code=401, detail="Invalid webhook signature")

    stmt = select(WebhookEvent).where(WebhookEvent.event_id == webhook.event_id)
    existing_webhook_event = db.scalars(stmt).one_or_none()

    if existing_webhook_event is not None:
        return {
            "received": True,
            "duplicate": True
        }

    new_webhook_event = WebhookEvent(
        event_id=webhook.event_id,
        event_type=webhook.event_type,
        processed_at=datetime.utcnow(),
    )

    db.add(new_webhook_event)
    db.commit()

    return {
        "received": True,
        "duplicate": False
    }
