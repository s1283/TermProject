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
    statuses = ["Not Started", "On-Hold", "Completed", "In-Progress"]   

    for _ in range(20):
        title = random.choice(titles)
        task_type = random.choice(types)
        due_date = datetime.now() + timedelta(days=random.randint(0, 30))
        description = "Auto-generated"
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
    print("Generated 20 random tasks")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Please provide a command: create_table, drop_tables, generate_tasks")
        sys.exit(1)
    action = sys.argv[1]
    with app.app_context():
        if action == "create_table":
            create_tables()
        elif action == "drop_table":
            drop_tables()
        elif action == "generate_tasks":
            generate_random_tasks()
        elif action == "create":
            drop_tables()
            create_tables()
            generate_random_tasks()
        else:
            print("Please provide a command: create_table, drop_tables, generate_tasks")
            sys.exit(1)