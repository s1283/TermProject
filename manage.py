from app import app
from db import db
from models import Task
import sys

def drop_tables():
    db.drop_all()
    print("Successfully dropped tables")

def create_tables():
    db.create_all()
    print("Successfully created tables")

if __name__ == "__main__":
    with app.app_context():
        drop_tables()
        create_tables()