from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import get_db
from models import Transaction
from schemas import TransactionCreate, TransactionOut
from routers.auth import get_current_user

router = APIRouter(prefix="/transactions", tags=["Transactions"])

@router.post("/", response_model=TransactionOut)
def create(
    t: TransactionCreate,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    new_t = Transaction(**t.dict(), user_id=user.id)
    db.add(new_t)
    db.commit()
    db.refresh(new_t)
    return new_t

@router.get("/", response_model=List[TransactionOut])
def get_all(
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    return db.query(Transaction).filter(
        Transaction.user_id == user.id
    ).all()

@router.put("/{id}", response_model=TransactionOut)
def update(
    id: int,
    t: TransactionCreate,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    existing = db.query(Transaction).filter(
        Transaction.id == id,
        Transaction.user_id == user.id
    ).first()
    if not existing:
        raise HTTPException(status_code=404, detail="Transaction not found")
    for key, value in t.dict().items():
        setattr(existing, key, value)
    db.commit()
    db.refresh(existing)
    return existing

@router.delete("/{id}")
def delete(
    id: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    t = db.query(Transaction).filter(
        Transaction.id == id,
        Transaction.user_id == user.id
    ).first()
    if not t:
        raise HTTPException(status_code=404, detail="Transaction not found")
    db.delete(t)
    db.commit()
    return {"message": "Deleted successfully"}