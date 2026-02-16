# src/models/student.py
from sqlalchemy import String, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import TYPE_CHECKING

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.item import Item


class Student(Base):
    __tablename__ = "students"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True,  # explicit is fine, but optional
    )
    name: Mapped[str] = mapped_column(
        String(100),          # 100 is usually enough for names
        nullable=False,
        index=False,          # no need for extra index unless you search by name often
    )
    age: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )
    grade: Mapped[str] = mapped_column(
        String(20),           # e.g. "A+", "B-", "Excellent", etc.
        nullable=False,
    )
    # Relationship: One student can have many items
    items: Mapped[list["Item"]] = relationship("Item", back_populates="student", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Student(id={self.id}, name={self.name!r}, age={self.age}, grade={self.grade!r})>"