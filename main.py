from contextlib import asynccontextmanager
from datetime import datetime, timezone
from pathlib import Path
import json
import sqlite3
from typing import Literal

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field, ConfigDict

DB_PATH = Path(__file__).with_name("tickets.db")

CATEGORY_RULES = {
    "Billing": ["invoice", "payment", "charged", "refund", "bill", "subscription", "price", "charge"],
    "Access": ["login", "log in", "password", "locked", "access", "sign in", "2fa", "account"],
    "Technical": ["error", "bug", "crash", "slow", "broken", "not working", "failed", "failure", "server"],
    "General": [],
}
TEAMS = {
    "Billing": "Billing Support",
    "Access": "Identity & Access Support",
    "Technical": "Technical Support",
    "General": "Customer Support",
}

def classify(message: str) -> tuple[str, float]:
    """Transparent keyword baseline. Confidence is a heuristic, not a calibrated probability."""
    text = message.lower()
    scores = {category: sum(1 for word in words if word in text) for category, words in CATEGORY_RULES.items()}
    best = max(("Billing", "Access", "Technical"), key=lambda c: scores[c])
    if scores[best] == 0:
        return "General", 0.35
    if sum(v > 0 for v in scores.values()) > 1 or scores[best] == 1:
        confidence = 0.60
    else:
        confidence = 0.85
    return best, confidence

def choose_priority(message: str) -> str:
    text = message.lower()
    urgent_terms = ["urgent", "critical", "outage", "all users", "security breach", "cannot work", "can't work", "production down"]
    high_terms = ["today", "blocked", "deadline", "lost access", "charged twice"]
    if any(term in text for term in urgent_terms):
        return "High"
    if any(term in text for term in high_terms):
        return "Medium"
    return "Low"

def draft_response(category: str) -> str:
    drafts = {
        "Billing": "Thanks for contacting us about billing. We will review the charge or invoice and follow up with the next steps.",
        "Access": "Thanks for reporting the access issue. Please do not share your password. Our support team will help verify your account and restore access.",
        "Technical": "Thanks for reporting this technical issue. We will investigate the behaviour and follow up with troubleshooting steps.",
        "General": "Thanks for contacting support. A team member will review your request and follow up with you.",
    }
    return drafts[category]

def connect():
    conn = sqlite3.connect(DB_PATH, timeout=10)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with connect() as conn:
        conn.execute("""
        CREATE TABLE IF NOT EXISTS tickets (
            ticket_id TEXT PRIMARY KEY,
            message TEXT NOT NULL,
            category TEXT NOT NULL,
            priority TEXT NOT NULL,
            assigned_team TEXT NOT NULL,
            summary TEXT NOT NULL,
            draft_response TEXT NOT NULL,
            confidence REAL NOT NULL,
            status TEXT NOT NULL DEFAULT 'pending_approval',
            created_at TEXT NOT NULL,
            approved_at TEXT
        )
        """)

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield

app = FastAPI(
    title="Cerevyn Support Ticket Automation",
    description="Classifies support tickets and drafts replies for human review. No messages are sent.",
    version="1.0.0",
    lifespan=lifespan,
)

class TicketIn(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)
    ticket_id: str = Field(min_length=1, max_length=64)
    message: str = Field(min_length=5, max_length=4000)

class TicketOut(BaseModel):
    ticket_id: str
    category: str
    priority: str
    assigned_team: str
    summary: str
    draft_response: str
    confidence: float
    status: str
    created_at: str

@app.get("/")
def root():
    return {"service": "Cerevyn Support Ticket Automation", "docs": "/docs", "health": "/health"}

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/tickets", response_model=TicketOut, status_code=201)
def create_ticket(payload: TicketIn):
    category, confidence = classify(payload.message)
    priority = choose_priority(payload.message)
    words = payload.message.split()
    summary = " ".join(words[:18]) + ("…" if len(words) > 18 else "")
    created_at = datetime.now(timezone.utc).isoformat()
    status = "pending_review" if confidence < 0.7 else "pending_approval"
    try:
        with connect() as conn:
            conn.execute("""
                INSERT INTO tickets
                (ticket_id, message, category, priority, assigned_team, summary,
                 draft_response, confidence, status, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (payload.ticket_id, payload.message, category, priority, TEAMS[category],
                  summary, draft_response(category), confidence, status, created_at))
            row = conn.execute("SELECT * FROM tickets WHERE ticket_id=?", (payload.ticket_id,)).fetchone()
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=409, detail="Duplicate ticket_id. Ticket was not created.")
    return dict(row)

@app.get("/tickets/{ticket_id}")
def get_ticket(ticket_id: str):
    with connect() as conn:
        row = conn.execute("SELECT * FROM tickets WHERE ticket_id=?", (ticket_id,)).fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return dict(row)

@app.get("/tickets")
def list_tickets():
    with connect() as conn:
        rows = conn.execute("SELECT * FROM tickets ORDER BY created_at DESC").fetchall()
    return {"tickets": [dict(row) for row in rows]}

@app.post("/tickets/{ticket_id}/approve")
def approve_ticket(ticket_id: str):
    with connect() as conn:
        row = conn.execute("SELECT * FROM tickets WHERE ticket_id=?", (ticket_id,)).fetchone()
        if row is None:
            raise HTTPException(status_code=404, detail="Ticket not found")
        if row["status"] == "approved":
            return {"ticket_id": ticket_id, "status": "approved", "message": "Already approved"}
        conn.execute(
            "UPDATE tickets SET status='approved', approved_at=? WHERE ticket_id=?",
            (datetime.now(timezone.utc).isoformat(), ticket_id)
        )
    return {"ticket_id": ticket_id, "status": "approved", "message": "Draft approved; no email was sent."}
