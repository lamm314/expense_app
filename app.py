from flask import Flask, render_template, request, redirect
from services.supabase_client import supabase
from datetime import datetime, timedelta

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