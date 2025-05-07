from flask import Flask, render_template, request, redirect, url_for
from pathlib import Path
from db import db
from routes import api_bp
from models import *

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
    return render_template("home.html")

@app.route("/tasks", methods=["GET"])
def view_tasks():
    statement = db.select(Task)
    tasks = db.session.execute(statement).scalars().all()
    return render_template("tasks.html", tasks=tasks)

@app.route("/tasks/add", methods=["POST"])
def add_task():
    return redirect(url_for("view_tasks"))


if __name__ == "__main__":
    app.run(debug=True, port=8888)