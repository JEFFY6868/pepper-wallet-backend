import sys
from pathlib import Path
from wallet_qr import generate_payment_qr
from pydantic import BaseModel
from razorpay_config import client
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

from wallet_state import (
    wallet_state
)

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

def get_wallet(

    user=Depends(
        verify_token
    )

):

    return {

        "wallet": wallet_state,

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

def get_history(

    user=Depends(
        verify_token
    )

):

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

    prompt = f"""

Wallet Information:

{wallet_state}

Goals:

{get_goals()}

Transaction History:

{view_history()}

Analytics:

{analytics_summary()}

User Question:

{request.message}

You are Pepper Wallet AI.

Use the wallet, goals, history and analytics
to answer accurately.

Give useful financial insights when appropriate.

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
    
@app.post("/create-order")
def create_order(
    request: PaymentRequest
):

    order = client.order.create({

        "amount": int(
            request.amount * 100
        ),

        "currency": "INR",

        "payment_capture": 1

    })

    return order
    
@app.post("/payment-success")
def payment_success(
    request: PaymentRequest
):

    result = handle_deposit(
        request.amount
    )

    return result
