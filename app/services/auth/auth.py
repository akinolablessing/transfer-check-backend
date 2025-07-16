from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from email_validator import validate_email, EmailNotValidError
from app.security.hash import hash_password, verify_password
from app.security.jwt_handler import create_access_token
from app.db.data_base import get_db
from app.models.agent import Agent
from app.schema.schemas import AgentCreate, AgentLogin, TransactionSchema
from app.security.otp import generate_otp


def is_valid_email_format(email: str) -> bool:
    try:
        validate_email(email)
        return True
    except EmailNotValidError:
        return False


def register(agent: AgentCreate, db: Session = Depends(get_db)):
    if not agent.name or not agent.name.strip():
        raise HTTPException(status_code=400, detail="Name is required")

    if not agent.email or not agent.email.strip():
        raise HTTPException(status_code=400, detail="Email is required")

    if not is_valid_email_format(agent.email.strip()):
        raise HTTPException(status_code=400, detail="Invalid email format")

    phone = agent.phone.strip() if agent.phone else ""
    if len(phone) != 11 or not phone.isdigit():
        raise HTTPException(status_code=400, detail="Phone is required and must be 11 digits")

    existing_email = db.query(Agent).filter(Agent.email == agent.email.strip()).first()
    existing_phone = db.query(Agent).filter(Agent.phone == phone).first()

    if not agent.password or not agent.password.strip():
        raise HTTPException(status_code=400, detail="Password is required")

    if existing_email:
        raise HTTPException(status_code=400, detail="Email already registered")
    if existing_phone:
        raise HTTPException(status_code=400, detail="Phone number already registered")

    hashed_password = hash_password(agent.password)
    new_agent = Agent(
        name=agent.name.strip(),
        email=agent.email.strip(),
        phone=phone,
        password=hashed_password

    )

    db.add(new_agent)
    db.commit()
    db.refresh(new_agent)

    token = create_access_token(new_agent)
    return {"message": "Agent registered successfully", "access_token": token}




def login(agent: AgentLogin, db: Session = Depends(get_db)):
    db_agent = db.query(Agent).filter(Agent.email == agent.email).first()

    if not db_agent or not verify_password(agent.password, db_agent.password):
        raise HTTPException(status_code=404, detail="Invalid credentials")

    token = create_access_token(db_agent)

    transactions_data = [
        TransactionSchema.model_validate(txn).model_dump() for txn in db_agent.transactions
    ]

    return {
        "transactions": transactions_data,
        "access_token": token,
        "token_type": "bearer",
    }
