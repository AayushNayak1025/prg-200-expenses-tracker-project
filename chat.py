from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
import sys
import os

# This correctly points to the analytics folder
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
ANALYTICS_DIR = os.path.join(ROOT_DIR, 'analytics')

sys.path.insert(0, ROOT_DIR)
sys.path.insert(0, BASE_DIR)
sys.path.insert(0, ANALYTICS_DIR)

from database import get_db
from models import Transaction, ChatHistory
from schemas import ChatRequest
from routers.auth import get_current_user
from cohere_service import ask_cohere, get_embedding
from analytics.engine import build_financial_context

router = APIRouter(prefix="/chat", tags=["AI Chat"])

@router.post("/")
def chat(
    req: ChatRequest,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    transactions = db.query(Transaction).filter(
        Transaction.user_id == user.id
    ).all()

    context = build_financial_context(transactions)
    ai_response = ask_cohere(req.message, context)

    db.add(ChatHistory(user_id=user.id, role="user", message=req.message))
    db.add(ChatHistory(user_id=user.id, role="assistant", message=ai_response))
    db.commit()

    return {"response": ai_response, "context_used": context}

@router.get("/history")
def get_history(
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    history = db.query(ChatHistory).filter(
        ChatHistory.user_id == user.id
    ).order_by(ChatHistory.created_at).all()
    return [
        {"role": h.role, "message": h.message, "time": str(h.created_at)}
        for h in history
    ]