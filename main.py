from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import engine, Base
from routers import auth, transactions, chat

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Expense Tracker API", version="2.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(transactions.router)
app.include_router(chat.router)

@app.get("/")
def root():
    return {"message": "Expense Tracker API v2 Running!"}