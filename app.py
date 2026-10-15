
from datetime import date, timedelta
from pathlib import Path
import calendar
import sqlite3

from flask import Flask, render_template, request, redirect, url_for, flash

app = Flask(__name__)
app.secret_key = "change-this-before-deployment"

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "gym.db"


def get_db():
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def add_months(start_date, months=1):
    month_index = start_date.month - 1 + months
    year = start_date.year + month_index // 12
    month = month_index % 12 + 1
    day = min(start_date.day, calendar.monthrange(year, month)[1])
    return date(year, month, day)


def init_db():
    with get_db() as db:
        schema = (BASE_DIR / "schema.sql").read_text(encoding="utf-8")
        db.executescript(schema)


@app.route("/")
def dashboard():
    today = date.today()
    soon = (today + timedelta(days=7)).isoformat()

    with get_db() as db:
        total_members = db.execute(
            "SELECT COUNT(*) FROM members"
        ).fetchone()[0]

        active_members = db.execute(
            "SELECT COUNT(*) FROM members WHERE membership_end >= ?",
            (today.isoformat(),)
        ).fetchone()[0]

        revenue = db.execute(
            """SELECT COALESCE(SUM(amount), 0)
               FROM payments
               WHERE substr(payment_date, 1, 7) = ?""",
            (today.strftime("%Y-%m"),)
        ).fetchone()[0]

        expiring = db.execute(
            """SELECT * FROM members
               WHERE membership_end BETWEEN ? AND ?
               ORDER BY membership_end""",
            (today.isoformat(), soon)
        ).fetchall()

        members = db.execute(
            """SELECT * FROM members
               ORDER BY id DESC LIMIT 10"""
        ).fetchall()

    return render_template(
        "index.html",
        total_members=total_members,
        active_members=active_members,
        revenue=revenue,
        expiring=expiring,
        members=members,
        today=today.isoformat()
    )


@app.route("/members/add", methods=["POST"])
def add_member():
    name = request.form.get("full_name", "").strip()
    phone = request.form.get("phone", "").strip()
    email = request.form.get("email", "").strip()
    address = request.form.get("address", "").strip()
    plan = request.form.get("plan_name", "Monthly").strip()
    start_text = request.form.get("membership_start", "")
    method = request.form.get("payment_method", "Cash")
    amount_text = request.form.get("amount", "").strip()

    if not name or not phone or not start_text:
        flash("Name, phone and start date are required.")
        return redirect(url_for("dashboard"))

    try:
        start = date.fromisoformat(start_text)
        amount = float(amount_text)
        if not amount >= 0 or not amount < float("inf"):
            raise ValueError
        if len(phone) > 30 or len(name) > 120:
            raise ValueError
        if method not in ("Cash", "UPI", "Card", "Bank Transfer"):
            raise ValueError
        if plan not in ("Monthly", "Quarterly", "Half-yearly", "Annual"):
            raise ValueError
    except (ValueError, OverflowError):
        flash("Please enter valid membership and payment details.")
        return redirect(url_for("dashboard"))

    months = {
        "Monthly": 1,
        "Quarterly": 3,
        "Half-yearly": 6,
        "Annual": 12
    }[plan]

    end = add_months(start, months) - timedelta(days=1)
    joining = date.today().isoformat()

    try:
        with get_db() as db:
            cursor = db.execute(
                """INSERT INTO members
                   (full_name, phone, email, address, joining_date,
                    plan_name, monthly_fee, membership_start, membership_end)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    name, phone, email, address, joining,
                    plan, amount / months,
                    start.isoformat(), end.isoformat()
                )
            )
            member_id = cursor.lastrowid

            if amount > 0:
                db.execute(
                    """INSERT INTO payments
                       (member_id, amount, payment_date, payment_method, notes)
                       VALUES (?, ?, ?, ?, ?)""",
                    (
                        member_id, amount, joining, method,
                        "Initial membership payment"
                    )
                )
    except sqlite3.IntegrityError:
        flash("Could not save the member. Please check the details.")
        return redirect(url_for("dashboard"))

    flash(f"{name} was registered successfully.")
    return redirect(url_for("dashboard"))


@app.route("/health")
def health():
    return {"status": "ok"}


if __name__ == "__main__":
    init_db()
    app.run(debug=True)

dues = db.execute("SELECT * FROM members WHERE amount_due > 0 ORDER BY amount_due DESC").fetchall()
total_due = sum(d["amount_due"] for d in dues)
# render_template("index.html", ..., dues=dues, total_due=total_due)

fee = float(request.form["plan_fee"]); paid = float(request.form["amount"])
amount_due = max(fee - paid, 0)   # store this in members.amount_due

