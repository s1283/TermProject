from flask import Flask, render_template, request, redirect, url_for
from pathlib import Path
from db import db
from routes import api_bp
from models import *
from datetime import datetime, timedelta
from random import choice, randint

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
    top_tasks_stmt = db.select(Task).where(Task.status != "Completed").order_by(Task.due_date).limit(5)

    recent_completed_stmt = db.select(Task).where(
        Task.status == "Completed",
        Task.due_date >= now - timedelta(days=7)
    ).order_by(Task.due_date.desc()).limit(3)

    top_tasks = db.session.execute(top_tasks_stmt).scalars().all()
    recent_completed = db.session.execute(recent_completed_stmt).scalars().all()

    for task in top_tasks:
        if task.due_date.date() < now.date() and task.status not in ["Completed", "Overdue", "On-Hold"]:
            task.status = "Overdue"
    db.session.commit()

    return render_template("home.html", tasks=top_tasks, completed_tasks=recent_completed)

@app.route("/tasks", methods=["GET"])
def view_tasks():
    now = datetime.now()
    sort_by = request.args.get("sort_by")
    order = request.args.get("order")
    statement = db.select(Task)

    valid_fields = {
        "title": Task.title,
        "type": Task.type,
        "due_date": Task.due_date,
        "description": Task.description,
        "status": Task.status
    }
    if sort_by in valid_fields:
        column = valid_fields[sort_by]
        if order == "desc":
            statement = statement.order_by(column.desc())
        else:
            statement = statement.order_by(column)
    else:
        statement = statement.order_by(Task.due_date)
    tasks = db.session.execute(statement).scalars().all()
    for task in tasks:
        if task.due_date.date() < now.date() and task.status not in ["Completed", "Overdue", "On-Hold"]:
            task.status = "Overdue"
    db.session.commit()
    active_tasks = [task for task in tasks if task.status != "Completed"]
    return render_template("tasks.html", tasks=active_tasks)

@app.route("/completed", methods=["GET"])
def completed_tasks():
    statement = db.select(Task).where(Task.status == "Completed").order_by(Task.due_date.desc())
    completed = db.session.execute(statement).scalars().all()
    return render_template("completed_tasks.html", tasks=completed)

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
    if task and task.status == "Completed":
        return redirect(url_for("completed_tasks"))
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

@app.route("/tasks/generate", methods=["POST"])
def generate_random_tasks():
    titles = ["Math Quiz", "Read Book", "Clean Room", "Submit Report"]
    types = ["School", "Work", "Personal", "Other"]
    statuses = ["Not Started", "On-Hold", "Completed", "In-Progress"]  

    for _ in range(20):
        task = Task(
            title=choice(titles),
            type=choice(types),
            due_date=datetime.now() + timedelta(days=randint(1, 10)),
            description="Auto-generated",
            status=choice(statuses)
        )
        db.session.add(task)

    db.session.commit()
    return redirect(url_for("view_tasks"))

if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True, port=8888)