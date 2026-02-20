from enum import Enum
from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime
from typing import Optional

class TransactionType(str, Enum):
    INCOME = "income"
    EXPENSE = "expense"

class TransactionBase(BaseModel):
    amount: float
    category: str
    description: Optional[str] = None
    type: TransactionType

class TransactionCreate(TransactionBase):
    pass

class Transaction(TransactionBase):
    id: int
    created_at: datetime
    owner_id: int

    # Для Pydantic v2 (актуальный стандарт)
    model_config = ConfigDict(from_attributes=True)
    
class UserCreate(BaseModel):
    username: str
    password: str = Field(..., max_length=72)
    
class UserOut(BaseModel):
    id: int
    username: str

    model_config = ConfigDict(from_attributes=True)
    

# 3. Схема для выдачи токена (билет в систему)
class Token(BaseModel):
    access_token: str
    token_type: str