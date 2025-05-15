from flask import Flask, render_template, request, redirect, url_for
from pathlib import Path
from db import db
from routes import api_bp
from models import *
from datetime import datetime, timedelta

app = Flask(__name__)
# This will make Flask use a 'sqlite' database with the filename provided
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///assignments.db"
# This will make Flask store the database file in the path provided
app.instance_path = Path(".").resolve()

db.init_app(app)
# Register the blueprint
app.register_blueprint(api_bp, url_prefix="/api")

@app.route("/", methods=["GET"])
def home():
    now = datetime.now()
    statement = db.select(Task).order_by(Task.due_date).limit(5)
    completed_statement = db.select(Task).where(
        Task.status == "Completed",
        Task.due_date >= now - timedelta(days=7)
    ).order_by(Task.due_date.desc()).limit(3)

    top_tasks = db.session.execute(statement).scalars().all()
    recent_completed = db.session.execute(completed_statement).scalars().all()

    return render_template("home.html", tasks=top_tasks, completed_tasks=recent_completed)

@app.route("/tasks", methods=["GET"])
def view_tasks():
    statement = db.select(Task)
    tasks = db.session.execute(statement).scalars().all()
    return render_template("tasks.html", tasks=tasks)

@app.route("/tasks/add", methods=["POST"])
def add_task():
    title = request.form["title"]
    task_type = request.form["type"]
    due_date_str = request.form["due_date"]
    due_date = datetime.strptime(due_date_str, "%Y-%m-%d")
    description = request.form["description"]
    status = request.form["status"]

    new_task = Task(
        title=title,
        type=task_type,
        due_date=due_date,
        description=description,
        status=status
    )
    db.session.add(new_task)
    db.session.commit()
    return redirect(url_for("view_tasks"))

@app.route("/tasks/edit/<int:id>", methods=["GET", "POST"])
def edit_task(id):
    statement = db.select(Task).where(Task.id == id)
    task = db.session.execute(statement).scalars().first()

    if request.method == "POST":
        task.title = request.form["title"]
        task.type = request.form["type"]
        task.due_date = datetime.strptime(request.form["due_date"], "%Y-%m-%d")
        task.description = request.form["description"] if "description" in request.form else None
        task.status = request.form["status"]
        db.session.commit()
        return redirect(url_for("view_tasks"))

    return render_template("edit_task.html", task=task)

@app.route("/tasks/delete/<int:id>", methods=["POST"])
def delete_task(id):
    statement = db.select(Task).where(Task.id == id)
    task = db.session.execute(statement).scalars().first()
    if task:
        db.session.delete(task)
        db.session.commit()
    return redirect(url_for("view_tasks"))

@app.route("/tasks/add", methods=["GET"])
def add_task_form():
    return render_template("add_task.html")

@app.route("/tasks/complete/<int:id>", methods=["POST"])
def complete_task(id):
    statement = db.select(Task).where(Task.id == id)
    task = db.session.execute(statement).scalars().all()
    task = task[0]
    if task:
        task.status = "Completed"
        db.session.commit()
    return redirect(url_for("view_tasks"))

if __name__ == "__main__":
    app.run(debug=True, port=8888)