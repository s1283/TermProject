from db import db

class Task(db.Model):
    __tablename__ = "tasks"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    type = db.Column(db.String(50), nullable=False)
    due_date = db.Column(db.DateTime, nullable=False)
    description = db.Column(db.String(500), nullable=True)
    status = db.Column(db.String(20), default="Pending")

    def __repr__(self):
        return f"<Task {self.title}>"