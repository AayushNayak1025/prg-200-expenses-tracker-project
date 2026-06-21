import pandas as pd


def get_summary(transactions: list) -> dict:
    if not transactions:
        return {
            "total_income": 0,
            "total_expense": 0,
            "balance": 0,
            "by_category": {}
        }

    df = pd.DataFrame([{
        "amount": t.amount,
        "type": t.type,
        "category": t.category,
        "date": t.date
    } for t in transactions])

    income = df[df["type"] == "income"]["amount"].sum()
    expense = df[df["type"] == "expense"]["amount"].sum()
    by_category = (
        df[df["type"] == "expense"]
        .groupby("category")["amount"]
        .sum()
        .to_dict()
    )

    return {
        "total_income": round(float(income), 2),
        "total_expense": round(float(expense), 2),
        "balance": round(float(income - expense), 2),
        "by_category": by_category
    }


def detect_anomalies(transactions: list) -> list:
    if not transactions:
        return []
    df = pd.DataFrame([{
        "amount": t.amount,
        "category": t.category,
        "title": t.title
    } for t in transactions])
    mean = df["amount"].mean()
    std = df["amount"].std()
    if pd.isna(std) or std == 0:
        return []
    anomalies = df[df["amount"] > mean + 2 * std]
    return anomalies.to_dict(orient="records")


def build_financial_context(transactions: list) -> str:
    if not transactions:
        return "No transactions recorded yet."

    summary = get_summary(transactions)
    anomalies = detect_anomalies(transactions)

    lines = [
        f"Total Income: ${summary['total_income']}",
        f"Total Expenses: ${summary['total_expense']}",
        f"Current Balance: ${summary['balance']}",
        "Expenses by Category:"
    ]
    for cat, amt in summary["by_category"].items():
        lines.append(f"  - {cat}: ${round(amt, 2)}")

    if anomalies:
        lines.append("Unusual High Transactions:")
        for a in anomalies:
            lines.append(f"  - {a['title']}: ${a['amount']} ({a['category']})")

    return "\n".join(lines)


def get_smart_alerts(transactions: list) -> list:
    alerts = []
    if not transactions:
        return alerts

    df = pd.DataFrame([{
        "amount": t.amount,
        "type": t.type.value if hasattr(t.type, "value") else t.type,
        "category": t.category,
        "title": t.title
    } for t in transactions])

    income = df[df["type"] == "income"]["amount"].sum()
    expense = df[df["type"] == "expense"]["amount"].sum()
    balance = income - expense

    # Alert 1 — Low balance
    if balance < 100 and income > 0:
        alerts.append({
            "type": "danger",
            "icon": "🔴",
            "title": "Low Balance Warning",
            "message": f"Your balance is only ${round(balance, 2)}. Consider reducing expenses immediately."
        })

    # Alert 2 — Expenses exceed income
    if expense > income and income > 0:
        alerts.append({
            "type": "danger",
            "icon": "💸",
            "title": "Overspending Alert",
            "message": f"Your expenses (${round(expense, 2)}) exceed your income (${round(income, 2)}) by ${round(expense - income, 2)}!"
        })

    # Alert 3 — Expenses more than 80% of income
    if income > 0 and expense > 0 and expense <= income and (expense / income) > 0.8:
        alerts.append({
            "type": "warning",
            "icon": "⚠️",
            "title": "Spending Too Much",
            "message": f"You have spent {round((expense/income)*100)}% of your income. Try to keep it below 80%."
        })

    # Alert 4 —