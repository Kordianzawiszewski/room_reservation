from datetime import datetime

from sqlalchemy import CheckConstraint, Integer, String, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass

class Room(Base):
    __tablename__ = "rooms"

    __table_args__ = (
        CheckConstraint(
            "name IS NOT NULL OR room_number IS NOT NULL",
            name="check_room_has_name_or_number"
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    room_number: Mapped[str | None] = mapped_column(String(20), nullable=True)
    capacity: Mapped[int] = mapped_column(Integer, nullable=False)
    floor: Mapped[int] = mapped_column(Integer, nullable=False)

    reservations: Mapped[list["Reservation"]] = relationship(back_populates="room")

class Reservation(Base):
    __tablename__ = "reservations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    room_id: Mapped[int] = mapped_column(ForeignKey("rooms.id"), nullable=False)
    start_time: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    end_time: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    google_event_id: Mapped[str | None] = mapped_column(String(1024), nullable=True)

    room: Mapped["Room"] = relationship(back_populates="reservations")
    user: Mapped["User"] = relationship(back_populates="reservations")

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(100), nullable=False)
    role: Mapped[str] = mapped_column(String(20), nullable=False, default="user")
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    reservations: Mapped[list["Reservation"]] = relationship(back_populates="user")
    google_calendar_connection: Mapped["GoogleCalendarConnection | None"] = relationship(back_populates="user", uselist=False)
    google_oauth_state: Mapped["GoogleOAuthState | None"] = relationship(back_populates="user", uselist=False)
    password_reset_tokens: Mapped[list["PasswordResetToken"]] = relationship(back_populates="user", cascade="all, delete-orphan")

class PasswordResetToken(Base):
    __tablename__ = "password_reset_tokens"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    token_hash: Mapped[str] = mapped_column(String(100), nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    used: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    user: Mapped["User"] = relationship(back_populates="password_reset_tokens")

class GoogleCalendarConnection(Base):
    __tablename__ = "google_calendar_connections"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, unique=True)
    access_token: Mapped[str] = mapped_column(String(1024), nullable=False)
    refresh_token: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    token_expiry: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    user: Mapped["User"] = relationship(back_populates="google_calendar_connection")

class GoogleOAuthState(Base):
    __tablename__ = "google_oauth_states"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    state: Mapped[str] = mapped_column(String(1024), nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, unique=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    code_verifier: Mapped[str] = mapped_column(String(128), nullable=False)

    user: Mapped["User"] = relationship(back_populates="google_oauth_state")
