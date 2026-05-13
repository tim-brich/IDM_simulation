from pydantic import BaseModel, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime

class UserCreate(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: int
    email: str
    total_xp: int
    current_level: int
    streak_days: int

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

class TaskResponse(BaseModel):
    id: int
    level_id: int
    type: str
    question: str
    image_url: Optional[str] = None
    metadata_json: Optional[Dict[str, Any]] = None

    class Config:
        from_attributes = True

class LevelResponse(BaseModel):
    id: int
    order_index: int
    title: str
    description: Optional[str] = None
    tasks: List[TaskResponse] = []

    class Config:
        from_attributes = True

class AnswerSubmit(BaseModel):
    answer: str

class AnswerResult(BaseModel):
    is_correct: bool
    feedback: Optional[str] = None
    stars: Optional[int] = None
    xp_earned: int
