from flask import Flask, render_template, request, redirect
from services.supabase_client import supabase
from datetime import datetime, timedelta

app = Flask(__name__)

@app.route("/")
def index():
    data = supabase.table("transactions").select("*").execute()
    transactions = data.data or []

    # Tổng tiền
    total = sum(t["amount"] for t in transactions)

    # ===== Chart 7 ngày =====
    last7 = {}
    for i in range(7):
        day = (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")
        last7[day] = 0

    for t in transactions:
        date = t.get("date", "")[:10]
        if date in last7:
            last7[date] += t["amount"]

    chart_labels = list(last7.keys())[::-1]
    chart_values = list(last7.values())[::-1]

    # ===== Category =====
    category_map = {}
    for t in transactions:
        cat = t.get("category", "Other")
        category_map[cat] = category_map.get(cat, 0) + t["amount"]

    cat_labels = list(category_map.keys())
    cat_values = list(category_map.values())

    return render_template(
        "index.html",
        transactions=transactions,
        total=total,
        chart_labels=chart_labels,
        chart_values=chart_values,
        cat_labels=cat_labels,
        cat_values=cat_values
    )

@app.route("/add", methods=["POST"])
def add():
    supabase.table("transactions").insert({
        "amount": float(request.form["amount"]),
        "category": request.form.get("category", "General"),
        "note": request.form["note"],
        "date": datetime.now().isoformat()
    }).execute()

    return redirect("/")

if __name__ == "__main__":
    app.run()