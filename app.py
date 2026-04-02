from flask import Flask, render_template, request, redirect
from services.supabase_client import supabase
from datetime import datetime, timedelta
from collections import defaultdict
app = Flask(__name__)

@app.route("/")
def index():
    try:
        res = supabase.table("transactions").select("*").execute()
        transactions = res.data or []
    except Exception as e:
        print("ERROR FETCH:", e)
        transactions = []

    # ===== TÍNH TOÁN =====
    total_income = sum(t["amount"] for t in transactions if t["type"] == "income")
    total_expense = sum(t["amount"] for t in transactions if t["type"] == "expense")
    balance = total_income - total_expense

    # ===== CHART 7 NGÀY =====
    last7 = {}
    for i in range(7):
        day = (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")
        last7[day] = 0

    for t in transactions:
        d = str(t.get("date", ""))[:10]
        if d in last7 and t["type"] == "expense":
            last7[d] += t["amount"]

    chart_labels = list(last7.keys())[::-1]
    chart_values = list(last7.values())[::-1]

    return render_template(
        "index.html",
        transactions=transactions,
        total_income=total_income,
        total_expense=total_expense,
        balance=balance,
        chart_labels=chart_labels,
        chart_values=chart_values
    )
@app.route("/wallets")
def wallets():
    wallets = supabase.table("wallets").select("*").execute().data or []
    return render_template("wallets.html", wallets=wallets)
@app.route("/budgets")
def budgets():
    budgets = supabase.table("budgets").select("*").execute().data or []
    transactions = supabase.table("transactions").select("*").execute().data or []

    spent = defaultdict(float)

    for t in transactions:
        if t["type"] == "expense":
            spent[t["category"]] += t["amount"]

    return render_template("budgets.html", budgets=budgets, spent=spent)
@app.route("/analytics")
def analytics():
    transactions = supabase.table("transactions").select("*").execute().data or []

    category = defaultdict(float)

    for t in transactions:
        if t["type"] == "expense":
            category[t["category"]] += t["amount"]

    labels = list(category.keys())
    values = list(category.values())

    return render_template("analytics.html", labels=labels, values=values)

@app.route("/add", methods=["POST"])
def add():
    try:
        supabase.table("transactions").insert({
            "amount": float(request.form.get("amount", 0)),
            "category": request.form.get("category", "General"),
            "note": request.form.get("note", ""),
            "type": request.form.get("type"),  # income / expense
            "date": datetime.now().isoformat()
        }).execute()
    except Exception as e:
        print("ERROR INSERT:", e)

    return redirect("/")


if __name__ == "__main__":
    app.run()