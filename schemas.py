from pydantic import BaseModel, field_validator, EmailStr
from datetime import datetime
from typing import Optional
from enum import Enum
import re


class TransactionType(str, Enum):
    income = "income"
    expense = "expense"


class UserCreate(BaseModel):
    username: str
    email: str
    password: str

    @field_validator("email")
    @classmethod
    def validate_email(cls, v):
        # Email regex pattern
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(pattern, v):
            raise ValueError(
                "Invalid email format. Please use a valid email like user@gmail.com"
            )
        return v.lower()

    @field_validator("username")
    @classmethod
    def validate_username(cls, v):
        if len(v.strip()) < 3:
            raise ValueError("Username must be at least 3 characters")
        return v.strip()

    @field_validator("password")
    @classmethod
    def validate_password(cls, v):
        if len(v) < 6:
            raise ValueError("Password must be at least 6 characters")
        return v


class UserOut(BaseModel):
    id: int
    username: str
    email: str

    class Config:
        from_attributes = True


class TransactionCreate(BaseModel):
    title: str
    amount: float
    type: TransactionType
    category: str
    date: Optional[datetime] = None
    description: Optional[str] = None

    @field_validator("amount")
    @classmethod
    def validate_amount(cls, v):
        if v <= 0:
            raise ValueError("Amount must be greater than zero")
        return v

    @field_validator("title")
    @classmethod
    def validate_title(cls, v):
        if len(v.strip()) < 1:
            raise ValueError("Title cannot be empty")
        return v.strip()


class TransactionOut(TransactionCreate):
    id: int
    user_id: int

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str


class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    response: str
    context_used: str