from datetime import datetime
from typing import Dict, Any

import cv2
import numpy as np
from PIL import Image
import pytesseract
import re

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.agent import Agent
from app.models.transaction import Transaction
from app.schema.schemas import TransactionSchema


dummy_transactions = [
    TransactionSchema(
        amount=50000.00,
        receiver_bank_name="GTBank",
        reference_id="000001250712074117444574752341"
    ),
    TransactionSchema(
        amount=5000.00,
        receiver_bank_name="OPay",
        reference_id="250713010100785037713236"
    )
]




def is_background_dark(image, threshold=100):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    mean_brightness = np.mean(gray)
    return mean_brightness < threshold


def normalize_background(contents: bytes):
    np_img = np.frombuffer(contents, np.uint8)
    img = cv2.imdecode(np_img, cv2.IMREAD_COLOR)
    if is_background_dark(img):
        img = cv2.bitwise_not(img)
    return Image.fromarray(img)




def extract_info(text: str) -> Dict[str, Any]:

    info = {
        "sender_name":None,
        "amount": None,
        "transaction_id": None,
        "receiver_bank": None,
        "date": None,
        "time": None,
    }
    amount_match = re.search(r'[₦#N\$]?\s?(\d{1,3}(?:,?\d{3})*\.\d{2})', text)
    if amount_match:
        info["amount"] = amount_match.group(1)

    transaction_id_match = re.search(
        r'(?:Transaction(?:\s+No\.?|\s+ID)|Ref(?:erence)?)\s*[:\-]?\s*([A-Za-z0-9]{10,})',
        text, re.IGNORECASE
    )
    if transaction_id_match:
        info["transaction_id"] = transaction_id_match.group(1)

    date_pattern = r'\b((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{1,2}(?:st|nd|rd|th)?\,?\s+\d{4}|\d{1,2}[/\-]\d{1,2}[/\-]\d{2,4}|\d{4}[/\-]\d{1,2}[/\-]\d{1,2})'
    date_match = re.search(date_pattern, text, re.IGNORECASE)
    if date_match:
        info["date"] = date_match.group(0)

    # Time Pattern: "10:24:09", "07.42AM"
    time_pattern = r'\b(\d{1,2}:\d{2}(?::\d{2})?\s?(?:AM|PM)?)\b'
    time_match = re.search(time_pattern, text, re.IGNORECASE)
    if time_match:
        info["time"] = time_match.group(0)

    banks_pattern = (
        r'\b(GTBank|Guaranty Trust(?: Bank)?|Access(?: Bank)?|UBA|United Bank for Africa|First(?: Bank)?|Zenith|Sterling|'
        r'OPay|Kuda|Moniepoint|Fidelity|Ecobank|Union(?: Bank)?|Keystone|Stanbic(?: IBTC)?|FCMB|First City Monument Bank|'
        r'Jaiz|Heritage|Wema|Globus|Suntrust|Parallex|Providus)\b'
    )
    recipient_section_match = re.search(
        r'(Recipient[\s\S]+?)(?=\n\s*\n|Sender|Narration|Transaction\s+No\.)',
        text, re.IGNORECASE
    )

    search_text_for_bank = text
    if recipient_section_match:
        search_text_for_bank = recipient_section_match.group(1)

    bank_match = re.search(banks_pattern, search_text_for_bank, re.IGNORECASE)
    if bank_match:
        info["receiver_bank"] = bank_match.group(1)

    return info


def unwarp_receipt(file):
    contents = file.read()
    image = normalize_background(contents)
    text = pytesseract.image_to_string(image)
    info = extract_info(text)
    return info


def scan_image(image, user_id, db: Session):
    info = unwarp_receipt(image)
    date = info["date"]
    reference_id = info["transaction_id"]
    amount = info["amount"]
    receiver_bank_name = info["receiver_bank"]
    time = info["time"]

    if not reference_id or not amount or not receiver_bank_name:
        raise HTTPException(status_code=404, detail="All fields are required")

    try:
        amount = float(amount.replace(",", ""))
    except:
        raise HTTPException(404, "❌ Invalid amount format.")

    def clean_date_suffix(date_str):
        return re.sub(r'(\d{1,2})(st|nd|rd|th)', r'\1', date_str)

    full_datetime = None
    if date:
        try:
            date = clean_date_suffix(date)
            if time:
                combined = f"{date} {time}"
                try:
                    full_datetime = datetime.strptime(combined, "%b %d, %Y %H:%M:%S")
                except ValueError:
                    full_datetime = datetime.strptime(combined, "%b %d, %Y %I:%M:%S %p")
            else:
                full_datetime = datetime.strptime(date, "%b %d, %Y")
        except Exception:
            raise HTTPException(404, "❌ Invalid date.")

    for tran in dummy_transactions:
        if tran.reference_id == reference_id and tran.amount == amount:
            existing_txn = db.query(Transaction).filter_by(reference_id=reference_id).first()
            if existing_txn:
                return {"message": "Money available ✅", "already_saved": True}
            else:
                transaction = Transaction(
                    amount=amount,
                    receiver_bank_name=receiver_bank_name,
                    reference_id=reference_id,
                    date=full_datetime,
                    agent_id=user_id,
                )
                db.add(transaction)
                db.commit()
                user = db.query(Agent).filter_by(id=user_id).first()
                user.successful_transactions += 1
                db.commit()
                db.refresh(user)
                return {"message": "Money available ✅", "saved": True}
    user = db.query(Agent).filter_by(id=user_id).first()
    user.unsuccessful_transactions += 1
    db.commit()
    db.refresh(user)
    raise HTTPException(404, "No money available ❌")


def get_successful_transactions(db: Session,user_id):
    user = db.query(Agent).filter_by(id=user_id).first()
    return user.successful_transactions


def get_unsuccessful_transactions(db: Session,user_id):
    user = db.query(Agent).filter_by(id=user_id).first()
    return user.unsuccessful_transactions


def get_transactions(db: Session, user_id):
    user = db.query(Agent).filter_by(id=user_id).first()


