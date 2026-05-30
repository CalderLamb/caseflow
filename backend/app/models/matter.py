import uuid
from datetime import datetime, date
from typing import Optional
from sqlalchemy import String, Text, Date, DateTime, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class Client(Base):
    __tablename__ = "clients"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[Optional[str]] = mapped_column(String(255))
    phone: Mapped[Optional[str]] = mapped_column(String(50))
    address: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    matters: Mapped[list["Matter"]] = relationship("Matter", back_populates="client")


class Matter(Base):
    __tablename__ = "matters"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    client_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("clients.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(500), nullable=False)
    type: Mapped[str] = mapped_column(String(100), nullable=False, default="personal_injury")
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="active")
    court: Mapped[Optional[str]] = mapped_column(String(255))
    case_number: Mapped[Optional[str]] = mapped_column(String(100))
    opened_date: Mapped[Optional[date]] = mapped_column(Date)
    sol_date: Mapped[Optional[date]] = mapped_column(Date)
    drive_folder_id: Mapped[Optional[str]] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    client: Mapped["Client"] = relationship("Client", back_populates="matters")
    case_items: Mapped[list["CaseItem"]] = relationship("CaseItem", back_populates="matter")
    documents: Mapped[list["Document"]] = relationship("Document", back_populates="matter")
    deadlines: Mapped[list["Deadline"]] = relationship("Deadline", back_populates="matter")
