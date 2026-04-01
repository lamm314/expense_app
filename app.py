from flask import Flask, render_template, request, redirect
from services.supabase_client import supabase
from datetime import datetime

app = Flask(__name__)

@app.route("/")
def index():
    data = supabase.table("transactions").select("*").execute()
    transactions = data.data or []

    total = sum(t["amount"] for t in transactions)

    return render_template("index.html", transactions=transactions, total=total)

@app.route("/add", methods=["POST"])
def add():
    supabase.table("transactions").insert({
        "amount": float(request.form["amount"]),
        "category": request.form.get("category", "General"),
        "note": request.form["note"],
        "date": datetime.now().isoformat()
    }).execute()

    return redirect("/")