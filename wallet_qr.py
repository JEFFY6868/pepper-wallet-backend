import uuid
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent

sys.path.append(str(ROOT_DIR))

from wallet_state import wallet_state
from wallet_history import add_transaction
# =========================
# GENERATE QR
# =========================

def generate_payment_qr(amount):

    upi_id = "9176806030@ptsbi"
    name = "Jeffy"

    upi_link = (
        f"upi://pay?"
        f"pa={upi_id}"
        f"&pn={name}"
        f"&am={amount}"
        f"&cu=INR"
    )

    return {
        "upi_link": upi_link
    }

# =========================
# RECEIVE MONEY
# =========================

def receive_money(amount):

    if amount <= 0:

        return {
            "success": False,
            "error": "Invalid amount"
        }

    wallet_state["total_balance"] += amount

    wallet_state["available_balance"] += amount

    add_transaction(
        "receive",
        amount,
        "Money received via QR"
    )

    return {

        "success": True,

        "message": f"Received ₹{amount}",

        "wallet": wallet_state

    }
