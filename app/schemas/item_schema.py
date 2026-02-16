from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional


class ItemBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: str = Field(..., min_length=1, max_length=500)
    price: float = Field(..., gt=0)
    quantity: int = Field(default=0, ge=0)


class ItemCreate(ItemBase):
    student_id: int = Field(..., gt=0, description="ID of the student who owns this item")


class ItemUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, min_length=1, max_length=500)
    price: Optional[float] = Field(None, gt=0)
    quantity: Optional[int] = Field(None, ge=0)
    student_id: Optional[int] = Field(None, gt=0)


class ItemOut(ItemBase):
    id: int
    student_id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


