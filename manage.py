from app import app
from db import db
from models import Task
import sys
import random
from datetime import datetime, timedelta

def drop_tables():
    db.drop_all()
    print("Successfully dropped tables")

def create_tables():
    db.create_all()
    print("Successfully created tables")

def generate_random_tasks():
    titles = ["Buy groceries", "Study Python", "Workout", "Meeting", "Read book", "Write report"]
    types = ["School", "Work", "Personal", "Other"] 
    statuses = ["Incomplete", "On-Hold"]

    for _ in range(10):
        title = random.choice(titles)
        task_type = random.choice(types)
        due_date = datetime.now() + timedelta(days=random.randint(0, 30))
        description = f"{title}"
        status = random.choice(statuses)

        task = Task(
            title=title,
            type=task_type,
            due_date=due_date,
            description=description,
            status=status
        )
        db.session.add(task)

    db.session.commit()
    print("Generated 10 random tasks")

if __name__ == "__main__":
    with app.app_context():
        drop_tables()
        create_tables()
        generate_random_tasks()