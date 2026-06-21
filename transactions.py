from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, ROOT_DIR)

from database import get_db
from models import Transaction
from schemas import TransactionCreate, TransactionOut
from routers.auth import get_current_user
from analytics.engine import get_smart_alerts

router = APIRouter(prefix="/transactions", tags=["Transactions"])


def get_current_balance(user_id: int, db: Session) -> float:
    transactions = db.query(Transaction).filter(
        Transaction.user_id == user_id
    ).all()
    income = sum(t.amount for t in transactions if t.type.value == "income")
    expense = sum(t.amount for t in transactions if t.type.value == "expense")
    return round(income - expense, 2)


@router.post("/", response_model=TransactionOut)
def create(
    t: TransactionCreate,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    # Balance check — only for expense transactions
    if t.type.value == "expense":
        current_balance = get_current_balance(user.id, db)
        if t.amount > current_balance:
            raise HTTPException(
                status_code=400,
                detail=f"Insufficient balance. Your current balance is ${current_balance:.2f} but you are trying to add an expense of ${t.amount:.2f}. Expense cannot exceed available funds."
            )

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

    # Balance check for update — if changing to expense or updating expense amount
    if t.type.value == "expense":
        # Get balance excluding current transaction
        all_transactions = db.query(Transaction).filter(
            Transaction.user_id == user.id,
            Transaction.id != id
        ).all()
        income = sum(tx.amount for tx in all_transactions if tx.type.value == "income")
        expense = sum(tx.amount for tx in all_transactions if tx.type.value == "expense")
        balance_without_current = round(income - expense, 2)
        if t.amount > balance_without_current:
            raise HTTPException(
                status_code=400,
                detail=f"Insufficient balance. Available balance is ${balance_without_current:.2f} but expense is ${t.amount:.2f}."
            )

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


@router.get("/alerts")
def get_alerts(
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    transactions = db.query(Transaction).filter(
        Transaction.user_id == user.id
    ).all()
    return get_smart_alerts(transactions)