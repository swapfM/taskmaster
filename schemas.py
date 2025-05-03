from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime


class UserOut(BaseModel):
    id: int
    username: str
    role: str

    class Config:
        from_attributes = True


class TaskCreate(BaseModel):
    title: str
    description: str
    deadline: datetime
    mandatory: bool
    assigned_to: str


class EmployeeSimple(BaseModel):
    user_id: int
    name: str


class SignupRequest(BaseModel):
    username: str
    password: str
    role: str


class UserCreate(BaseModel):
    username: str
    password_hash: str
    role: str


class TaskOut(BaseModel):
    id: int
    title: str
    description: Optional[str]
    created_at: str
    assigned_to: Optional[int]
    mandatory: bool

    class Config:
        from_attributes = True


class Skill(BaseModel):
    id: int
    name: str


class ContactInfo(BaseModel):
    email: EmailStr
    phone: str


class EmployeeCreate(BaseModel):
    bio: str
    skills: List[Skill]
    contactInfo: ContactInfo
