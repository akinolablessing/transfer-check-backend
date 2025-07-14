from sqlalchemy import Column, Integer, String, BigInteger, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.db.data_base import Base

class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    sender_name = Column(String(100), nullable=False)
    reference_id = Column(String(100), nullable=False, unique=True)
    amount = Column(BigInteger, nullable=False)
    receiver_bank_name = Column(String(100), nullable=False)
    sender_bank_name = Column(String(100), nullable=False)
    date = Column(DateTime, nullable=False)


    agent_id = Column(Integer, ForeignKey("agents.id"))
    agent = relationship("Agent", back_populates="transactions")
