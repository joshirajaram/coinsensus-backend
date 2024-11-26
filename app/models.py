# All models

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel

class User(BaseModel):
    id: int
    public_key: str
    username: str
    password: str
    name: str = 'John Doe'
    signup_ts: Optional[datetime] = None
    friends: List[int] = []

class Transaction(BaseModel):
    id: str
    sender: str
    sender_private_key: str
    receiver: str
    amount: int
    timestamp: float