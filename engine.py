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