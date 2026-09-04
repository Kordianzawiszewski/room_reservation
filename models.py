from datetime import datetime

from sqlalchemy import CheckConstraint, Integer, String, ForeignKey, DateTime
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
    reserved_by: Mapped[str] = mapped_column(String(100), nullable=False)

    room: Mapped["Room"] = relationship(back_populates="reservations")
