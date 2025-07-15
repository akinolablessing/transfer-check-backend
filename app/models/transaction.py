from sqlalchemy import Column, Integer, String, BigInteger, DateTime, ForeignKey, Numeric
from sqlalchemy.orm import relationship
from app.db.data_base import Base

class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    reference_id = Column(String(100), nullable=False)
    amount = Column(Numeric(precision=12, scale=2), nullable=False)
    receiver_bank_name = Column(String(100), nullable=False)
    date = Column(DateTime)


    agent_id = Column(Integer, ForeignKey("agents.id"))
    agent = relationship("Agent", back_populates="transactions")
