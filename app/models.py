from sqlalchemy import Column, Integer, String, Float, DateTime, func, Enum as SQLEnum, ForeignKey

from sqlalchemy.orm import relationship

from .database import Base

from .schemas import TransactionType


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    
    transactions = relationship("Transaction", back_populates="owner")
    
class Transaction(Base):
    __tablename__ = "transactions"
    id = Column(Integer, primary_key=True, index=True)
    amount = Column(Float, nullable=False)
    category = Column(String, index=True)
    description = Column(String, nullable=True)
    type = Column(SQLEnum(TransactionType), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    
    # Связь с пользователем
    owner_id = Column(Integer, ForeignKey("users.id"))
    owner = relationship("User", back_populates="transactions")