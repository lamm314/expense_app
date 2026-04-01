from flask import Flask, render_template, request, redirect
from services.supabase_client import supabase
from datetime import datetime

app = Flask(__name__)

@app.route("/")
def index():
    try:
        response = supabase.table("transactions").select("*").execute()
        transactions = response.data or []

        # ===== Chart default data (avoid undefined error) =====
        chart_labels = []
        chart_values = []
        cat_labels = []
        cat_values = []

        # ===== Build chart data safely =====
        try:
            from datetime import timedelta

            last7 = {}
            for i in range(7):
                day = (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")
                last7[day] = 0

            for t in transactions:
                date = str(t.get("date", ""))[:10]
                if date in last7:
                    last7[date] += t.get("amount", 0)

            chart_labels = list(last7.keys())[::-1]
            chart_values = list(last7.values())[::-1]

            category_map = {}
            for t in transactions:
                cat = t.get("category", "Other")
                category_map[cat] = category_map.get(cat, 0) + t.get("amount", 0)

            cat_labels = list(category_map.keys())
            cat_values = list(category_map.values())

        except Exception as e:
            print("ERROR CHART:", e)

    except Exception as e:
        print("ERROR FETCH:", e)
        transactions = []

    total = sum(t.get("amount", 0) for t in transactions)

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
    try:
        supabase.table("transactions").insert({
            "amount": float(request.form.get("amount", 0)),
            "category": request.form.get("category", "General"),
            "note": request.form.get("note", ""),
            "date": datetime.now().isoformat()
        }).execute()
    except Exception as e:
        print("ERROR INSERT:", e)

    return redirect("/")


if __name__ == "__main__":
    app.run()