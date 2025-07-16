from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.db.data_base import Base
from app.models.transaction import Transaction

class Agent(Base):
    __tablename__ = "agents"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    phone = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    successful_transactions = Column(Integer, default=0)
    unsuccessful_transactions = Column(Integer, default=0)
    transactions = relationship("Transaction", back_populates="agent", cascade="all, delete", lazy="selectin")
