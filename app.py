import os
from datetime import date, datetime

from flask import Flask, redirect, render_template, request, url_for
from flask_sqlalchemy import SQLAlchemy


def create_app() -> Flask:
    app = Flask(__name__)
    app.config.setdefault("SECRET_KEY", os.environ.get("SECRET_KEY", "dev"))

    database_url = os.environ.get("DATABASE_URL", "sqlite:///budget.db")
    # Heroku-style PostgreSQL URLs use the deprecated postgres scheme. Normalize it so
    # SQLAlchemy can understand the URI when the project eventually moves to Postgres.
    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)

    app.config["SQLALCHEMY_DATABASE_URI"] = database_url
    app.config.setdefault("SQLALCHEMY_TRACK_MODIFICATIONS", False)

    db = SQLAlchemy(app)

    class Entry(db.Model):
        __tablename__ = "entries"

        id = db.Column(db.Integer, primary_key=True)
        period = db.Column(db.String(7), nullable=False, index=True)
        entry_type = db.Column(db.String(10), nullable=False)
        description = db.Column(db.String(120), nullable=False)
        amount = db.Column(db.Float, nullable=False)
        created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    @app.before_first_request
    def init_db() -> None:
        db.create_all()

    def get_active_period() -> str:
        period = request.args.get("period")
        if period:
            return period
        today = date.today()
        return f"{today.year:04d}-{today.month:02d}"

    @app.route("/", methods=["GET", "POST"])
    def index():
        period = get_active_period()

        if request.method == "POST":
            entry_type = request.form.get("entry_type")
            description = request.form.get("description", "").strip()
            amount_raw = request.form.get("amount", "").strip()

            if entry_type not in {"income", "bill"} or not description or not amount_raw:
                return redirect(url_for("index", period=period))

            try:
                amount = float(amount_raw)
            except ValueError:
                return redirect(url_for("index", period=period))

            entry = Entry(
                period=period,
                entry_type=entry_type,
                description=description,
                amount=amount,
            )
            db.session.add(entry)
            db.session.commit()
            return redirect(url_for("index", period=period))

        periods = [p[0] for p in db.session.query(Entry.period).distinct().order_by(Entry.period.desc())]
        if period not in periods:
            periods.append(period)
            periods.sort(reverse=True)

        incomes = Entry.query.filter_by(period=period, entry_type="income").order_by(Entry.created_at.asc()).all()
        bills = Entry.query.filter_by(period=period, entry_type="bill").order_by(Entry.created_at.asc()).all()

        total_income = sum(entry.amount for entry in incomes)
        total_bills = sum(entry.amount for entry in bills)
        net = total_income - total_bills

        return render_template(
            "index.html",
            period=period,
            periods=periods,
            incomes=incomes,
            bills=bills,
            total_income=total_income,
            total_bills=total_bills,
            net=net,
        )

    @app.post("/delete/<int:entry_id>")
    def delete_entry(entry_id: int):
        period = get_active_period()
        entry = Entry.query.get_or_404(entry_id)
        db.session.delete(entry)
        db.session.commit()
        return redirect(url_for("index", period=period))

    return app


app = create_app()


if __name__ == "__main__":
    app.run(debug=True)
