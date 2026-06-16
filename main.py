import sys
import time
from pathlib import Path
from wallet_qr import generate_payment_qr
from pydantic import BaseModel
from razorpay_config import client
import hmac
import hashlib
import os
# =========================
# ADD ROOT PROJECT PATH
# =========================

ROOT_DIR = Path(
    __file__
).resolve().parent.parent

sys.path.append(
    str(ROOT_DIR)
)
from auth.auth_service import (

    register_user,
    login_user

)
from database.db import (
    initialize_database
)

from fastapi import FastAPI

from fastapi.middleware.cors import (
    CORSMiddleware
)

from fastapi.responses import (
    StreamingResponse
)

from pydantic import BaseModel

from wallet_controller import (

    handle_deposit,
    handle_lock,
    handle_unlock

)

from wallet_context import build_wallet_context

from wallet_goals import (
    goals
)

from wallet_analytics import (
    analytics_summary
)

from wallet_history import (
    view_history
)

from wallet_ai_analysis import (
    build_wallet_analysis
)

from wallet_ollama import (
    stream_pepper_ai
)
from fastapi import Depends

from auth.auth_guard import (
    verify_token
)
from wallet_goals_storage import (

    create_goal,
    get_goals,
    add_to_goal

)

from wallet_controller import (
    handle_deposit,
    handle_lock,
    handle_unlock
)

from database.wallet_db import load_wallet_state

from wallet_controller import (
    handle_deposit,
    handle_lock,
    handle_unlock,
    handle_expense
)

from wallet_reports import (
    monthly_report
)

from wallet_advisor import (
    get_financial_advice
)

from wallet_budgets import (
    set_budget,
    get_budgets
)

from wallet_budget_analysis import (
    budget_status
)
# =========================
# INITIALIZE DATABASE
# =========================

initialize_database()

# =========================
# FASTAPI
# =========================

app = FastAPI()

# =========================
# CORS
# =========================

app.add_middleware(

    CORSMiddleware,

    allow_origins=["*"],

    allow_credentials=True,

    allow_methods=["*"],

    allow_headers=["*"]

)

# =========================
# ROOT
# =========================

@app.get("/")

def root():

    return {

        "message":

        "Pepper Wallet Server Running"

    }

# =========================
# GET WALLET
# =========================

@app.get("/wallet")
def get_wallet():

    wallet = load_wallet_state()

    return {
        "wallet": wallet,
        "goals": get_goals(),
        "analytics": analytics_summary()
    }

# =========================
# REQUEST MODELS
# =========================

class AmountRequest(BaseModel):

    amount: float


class AIRequest(BaseModel):

    message: str

    wallet: dict | None = None


class GoalRequest(BaseModel):

    name: str

    target: float


class GoalAddRequest(BaseModel):

    index: int

    amount: float

class AuthRequest(BaseModel):

    username: str

    password: str

class QRRequest(BaseModel):

    amount: float

class PaymentRequest(BaseModel):

    amount: float
    
class VerifyPaymentRequest(BaseModel):
    razorpay_order_id: str
    razorpay_payment_id: str
    razorpay_signature: str
    
class ExpenseRequest(BaseModel):

    amount: float
    category: str = "Other"
    note: str = ""
    
class ExpenseRequest(BaseModel):

    amount: float
    category: str = "Other"
    note: str = ""
    
class BudgetRequest(BaseModel):

    category: str

    amount: float
# =========================
# DEPOSIT API
# =========================

@app.post("/deposit")

def deposit_money_api(

    request: AmountRequest,

    user=Depends(
        verify_token
    )

):

    result = handle_deposit(

        request.amount

    )

    return result

# =========================
# LOCK API
# =========================

@app.post("/lock")

def lock_money_api(

    request: AmountRequest,

    user=Depends(
        verify_token
    )

):

    result = handle_lock(

        request.amount

    )

    return result

# =========================
# UNLOCK API
# =========================

@app.post("/unlock")

def unlock_money_api(

    request: AmountRequest,

    user=Depends(
        verify_token
    )

):

    result = handle_unlock(

        request.amount

    )

    return result

# =========================
# HISTORY API
# =========================
@app.get("/history")

def get_history( ):

    return {

        "history":

        view_history()

    }

# =========================
# AI ANALYSIS API
# =========================

@app.get("/analysis")

def get_analysis(

    user=Depends(
        verify_token
    )

):

    return {

        "analysis":

        build_wallet_analysis()

    }

# =========================
# STREAM AI CHAT API
# =========================

@app.post("/ai")
def ai_chat(
    request: AIRequest
):

    wallet = load_wallet_state()
    
    context = build_wallet_context()

    prompt = f"""
You are Pepper Wallet AI.

Wallet:
{context["wallet"]}

Goals:
{context["goals"]}

Analytics:
{context["analytics"]}

Monthly Report:
{context["monthly_report"]}

User Question:
{request.message}

Instructions:

1. First answer the user's question directly.
2. Only mention wallet balances if relevant.
3. Do not repeat total_balance, locked_balance, and available_balance unless the user asks about money or balances.
4. Keep answers short and natural.
5. Use wallet data only when it helps answer the question.
"""

    print(prompt)

    return StreamingResponse(

        stream_pepper_ai(
            request.message
        ),

        media_type="text/plain"

    )
# =========================
# REGISTER API
# =========================

@app.post("/register")

def register_api(

    request: AuthRequest

):

    result = register_user(

        request.username,
        request.password

    )

    return result

# =========================
# LOGIN API
# =========================

@app.post("/login")

def login_api(

    request: AuthRequest

):

    result = login_user(

        request.username,
        request.password

    )

    return result

# =========================
# GET GOALS
# =========================

@app.get("/goals")

def get_goals_api():

    return {

        "goals": get_goals()

    }

# =========================
# CREATE GOAL
# =========================

@app.post("/goals")

def create_goal_api(

    request: GoalRequest

):

    return create_goal(

        request.name,

        request.target

    )

# =========================
# ADD TO GOAL
# =========================

@app.post("/goals/add")

def add_to_goal_api(

    request: GoalAddRequest

):

    return add_to_goal(

        request.index,

        request.amount

    )

# =========================
# QR REQUEST
# =========================

class QRRequest(BaseModel):

    amount: float


# =========================
# GENERATE UPI QR
# =========================

@app.post("/qr/generate")

def generate_qr_api(

    request: QRRequest

):

    upi_id = "9176806030@ptsbi"
    name = "THARSHAN S"

    upi_link = (

        f"upi://pay?"
        f"pa={upi_id}"
        f"&pn={name}"
        f"&am={request.amount}"
        f"&cu=INR"

    )

    return {

        "amount": request.amount,

        "upi_id": upi_id,

        "name": name,

        "upi_link": upi_link

    }   
    
@app.post("/api/create-order")
def create_order(request: PaymentRequest):

    if request.amount <= 0:
        return {
            "success": False,
            "message": "Invalid amount"
        }

    order = client.order.create({
        "amount": int(request.amount * 100),
        "currency": "INR",
        "receipt": f"wallet_{int(time.time())}"
    })

    return {
        "order_id": order["id"],
        "amount": order["amount"],
        "currency": order["currency"]
    }
    
@app.post("/payment-success")
def payment_success(
    request: PaymentRequest
):

    result = handle_deposit(
        request.amount
    )

    return result
    
@app.post("/api/verify-payment")
def verify_payment(
    request: VerifyPaymentRequest
):

    generated_signature = hmac.new(
        os.getenv("RAZORPAY_KEY_SECRET").encode(),
        f"{request.razorpay_order_id}|{request.razorpay_payment_id}".encode(),
        hashlib.sha256
    ).hexdigest()

    if generated_signature != request.razorpay_signature:

        return {
            "success": False,
            "message": "Invalid signature"
        }

    handle_deposit(1)

    return {
        "success": True,
        "message": "Payment verified"
    }
    
@app.post("/expense")

def expense_api(

    request: ExpenseRequest,

    user=Depends(
        verify_token
    )

):

    return handle_expense(

        request.amount,
        request.category,
        request.note

    )
    
# =========================
# MONTHLY REPORT
# =========================

@app.get("/monthly-report")

def get_monthly_report():

    return monthly_report()
    
# =========================
# FINANCIAL ADVISOR
# =========================

@app.get("/financial-advice")

def financial_advice():

    return get_financial_advice()
    
@app.post("/budget")

def create_budget(

    request: BudgetRequest

):

    return set_budget(

        request.category,

        request.amount

    )


@app.get("/budgets")

def budgets_api():

    return {

        "budgets": get_budgets()

    }


@app.get("/budget-status")

def budget_status_api():

    return {

        "status": budget_status()

    }
