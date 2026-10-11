from flask import Flask, render_template, request, redirect, url_for, flash, make_response
import sqlite3
import csv
import io
from datetime import date, datetime
from pathlib import Path

app = Flask(__name__)
app.secret_key = "change-this-secret-key-for-production"
BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "expenses.db"

CATEGORIES = ["Food", "Travel", "Education", "Shopping", "Bills", "Health", "Entertainment", "Other"]


def get_db():
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def init_db():
    with get_db() as connection:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                expense_date TEXT NOT NULL,
                category TEXT NOT NULL,
                description TEXT NOT NULL,
                amount REAL NOT NULL CHECK (amount > 0),
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
        """)


def parse_amount(value):
    try:
        amount = float(value)
        if amount <= 0:
            return None
        return round(amount, 2)
    except (TypeError, ValueError):
        return None


def get_filters():
    category = request.args.get("category", "").strip()
    search = request.args.get("search", "").strip()
    month = request.args.get("month", "").strip()
    return category, search, month


def filtered_expenses(connection, category="", search="", month=""):
    sql = "SELECT * FROM expenses WHERE 1=1"
    params = []
    if category and category in CATEGORIES:
        sql += " AND category = ?"
        params.append(category)
    if search:
        sql += " AND (description LIKE ? OR category LIKE ?)"
        wildcard = f"%{search}%"
        params.extend([wildcard, wildcard])
    if month:
        try:
            datetime.strptime(month, "%Y-%m")
            sql += " AND substr(expense_date, 1, 7) = ?"
            params.append(month)
        except ValueError:
            month = ""
    sql += " ORDER BY expense_date DESC, id DESC"
    return connection.execute(sql, params).fetchall()


@app.route("/")
def index():
    category, search, month = get_filters()
    with get_db() as connection:
        expenses = filtered_expenses(connection, category, search, month)
        total = connection.execute("SELECT COALESCE(SUM(amount), 0) FROM expenses").fetchone()[0]
        count = connection.execute("SELECT COUNT(*) FROM expenses").fetchone()[0]
        average = total / count if count else 0
        current_month = date.today().strftime("%Y-%m")
        month_total = connection.execute(
            "SELECT COALESCE(SUM(amount), 0) FROM expenses WHERE substr(expense_date, 1, 7) = ?",
            (current_month,)
        ).fetchone()[0]
        category_rows = connection.execute("""
            SELECT category, SUM(amount) AS total
            FROM expenses
            WHERE substr(expense_date, 1, 7) = ?
            GROUP BY category
            ORDER BY total DESC
        """, (current_month,)).fetchall()
    max_category = max((row["total"] for row in category_rows), default=0)
    return render_template(
        "index.html",
        expenses=expenses,
        total=total,
        count=count,
        average=average,
        month_total=month_total,
        category_rows=category_rows,
        max_category=max_category,
        categories=CATEGORIES,
        selected_category=category,
        search=search,
        selected_month=month,
        current_month=current_month,
        today=date.today().isoformat()
    )


@app.route("/add", methods=["POST"])
def add_expense():
    expense_date = request.form.get("expense_date", "").strip()
    category = request.form.get("category", "").strip()
    description = request.form.get("description", "").strip()
    amount = parse_amount(request.form.get("amount"))

    try:
        datetime.strptime(expense_date, "%Y-%m-%d")
    except ValueError:
        flash("Please enter a valid date.", "error")
        return redirect(url_for("index"))

    if category not in CATEGORIES:
        flash("Please choose a valid category.", "error")
    elif not description:
        flash("Please enter a description.", "error")
    elif len(description) > 120:
        flash("Description must be 120 characters or fewer.", "error")
    elif amount is None:
        flash("Amount must be a number greater than zero.", "error")
    else:
        with get_db() as connection:
            connection.execute(
                "INSERT INTO expenses (expense_date, category, description, amount) VALUES (?, ?, ?, ?)",
                (expense_date, category, description, amount)
            )
        flash("Expense added successfully.", "success")
    return redirect(url_for("index"))


@app.route("/delete/<int:expense_id>", methods=["POST"])
def delete_expense(expense_id):
    with get_db() as connection:
        cursor = connection.execute("DELETE FROM expenses WHERE id = ?", (expense_id,))
        if cursor.rowcount:
            flash("Expense deleted.", "success")
        else:
            flash("Expense was not found.", "error")
    return redirect(url_for("index"))


@app.route("/export")
def export_csv():
    category, search, month = get_filters()
    with get_db() as connection:
        expenses = filtered_expenses(connection, category, search, month)
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["ID", "Date", "Category", "Description", "Amount (INR)"])
    for expense in expenses:
        writer.writerow([
            expense["id"], expense["expense_date"], expense["category"],
            expense["description"], f'{expense["amount"]:.2f}'
        ])
    response = make_response("\ufeff" + output.getvalue())
    response.headers["Content-Type"] = "text/csv; charset=utf-8"
    response.headers["Content-Disposition"] = "attachment; filename=expenses.csv"
    return response


@app.route("/edit/<int:expense_id>", methods=["POST"])
def edit_expense(expense_id):
    expense_date = request.form.get("expense_date", "").strip()
    category = request.form.get("category", "").strip()
    description = request.form.get("description", "").strip()
    amount = parse_amount(request.form.get("amount"))
    try:
        datetime.strptime(expense_date, "%Y-%m-%d")
        valid_date = True
    except ValueError:
        valid_date = False

    if not valid_date or category not in CATEGORIES or not description or len(description) > 120 or amount is None:
        flash("Please check the updated expense details.", "error")
        return redirect(url_for("index"))

    with get_db() as connection:
        cursor = connection.execute("""
            UPDATE expenses
            SET expense_date = ?, category = ?, description = ?, amount = ?
            WHERE id = ?
        """, (expense_date, category, description, amount, expense_id))
    flash("Expense updated." if cursor.rowcount else "Expense was not found.", "success" if cursor.rowcount else "error")
    return redirect(url_for("index"))


init_db()

if __name__ == "__main__":
    app.run(debug=True)
