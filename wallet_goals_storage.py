import json
from wallet_state import wallet_state
from wallet_history import add_transaction

GOALS_FILE = "goals.json"


def get_goals():

    try:

        with open(

            GOALS_FILE,

            "r"

        ) as file:

            return json.load(file)

    except:

        return []


def save_goals(goals):

    with open(

        GOALS_FILE,

        "w"

    ) as file:

        json.dump(

            goals,

            file,

            indent=4

        )


def create_goal(

    name,
    target

):

    goals = get_goals()

    goal = {

        "name": name,

        "target": target,

        "saved": 0

    }

    goals.append(goal)

    save_goals(goals)

    return goal

def add_to_goal(index, amount):

    goals = get_goals()

    if index < 0 or index >= len(goals):

        return {
            "success": False,
            "error": "Goal not found"
        }

    goal = goals[index]

    if amount <= 0:

        return {
            "success": False,
            "error": "Invalid amount"
        }

    if goal["saved"] >= goal["target"]:

        return {
            "success": False,
            "error": "Goal already completed"
        }

    remaining = goal["target"] - goal["saved"]

    amount_to_add = min(amount, remaining)

    if wallet_state["available_balance"] < amount_to_add:

        return {
            "success": False,
            "error": "Not enough available balance"
        }

    wallet_state["available_balance"] -= amount_to_add

    goal["saved"] += amount_to_add

    save_goals(goals)

    add_transaction(
        "goal_deposit",
        amount_to_add,
        f"Added to {goal['name']}"
    )

    if goal["saved"] == goal["target"]:

        add_transaction(
            "goal_completed",
            goal["target"],
            f"Goal completed: {goal['name']}"
        )

        return {
            "success": True,
            "message": "🎉 Goal completed!",
            "goal": goal
        }

    return {
        "success": True,
        "goal": goal
    }
