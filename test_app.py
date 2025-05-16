from datetime import datetime, timedelta
from db import db
from models import Task
import pytest
from app import app as flask_app
from db import db

@pytest.fixture
def app():
    flask_app.config["TESTING"] = True
    flask_app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    
    with flask_app.app_context():
        db.create_all()
        yield flask_app
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

def test_home_route(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"Task Tracker" in response.data

def test_tasks_route(client):
    response = client.get("/tasks")
    assert response.status_code == 200
    assert b"All Tasks" in response.data

def test_create_task(client, app):
    future_date = (datetime.now() + timedelta(days=3)).strftime("%Y-%m-%d")
    response = client.post("/tasks/add", data={
        "title": "Test Task",
        "type": "Work",
        "due_date": future_date,
        "description": "test task",
        "status": "Incomplete"
    }, follow_redirects=True)

    assert response.status_code == 200
    assert b"Test Task" in response.data

    with app.app_context():
        task = db.session.execute(
            db.select(Task).where(Task.title == "Test Task")).scalar_one_or_none()
        assert task is not None

def test_empty_description(client):
    future_date = (datetime.now() + timedelta(days=3)).strftime("%Y-%m-%d")
    response = client.post("/tasks/add", data={
        "title": "test task",
        "type": "Work",
        "due_date": future_date,
        "description": "",
        "status": "Incomplete"
    }, follow_redirects=True)

    assert response.status_code == 200

def test_delete_task(client, app):
    with app.app_context():
        task = Task(
            title="Temp Task",
            type="School",
            due_date=datetime.now() + timedelta(days=1),
            description="To be deleted",
            status="Incomplete"
        )
        db.session.add(task)
        db.session.commit()
        task_id = task.id

    response = client.post(f"/tasks/delete/{task_id}", follow_redirects=True)
    assert response.status_code == 200

    with app.app_context():
        deleted = db.session.get(Task, task_id)
        assert deleted is None

def test_edit_task(client, app):
    with app.app_context():
        task = Task(
            title="Test Task",
            type="School",
            due_date=datetime.now() + timedelta(days=1),
            description="edit test",
            status="Incomplete"
        )
        db.session.add(task)
        db.session.commit()
        task_id = task.id

    update_data = {
        "title": "Edited Test Task",
        "type": "School",
        "due_date": (datetime.now() + timedelta(days=2)).strftime("%Y-%m-%d"),
        "description": "edit test updated",
        "status": "Incomplete"
    }

    response = client.post(f"/tasks/edit/{task_id}", data=update_data, follow_redirects=True)
    assert response.status_code == 200

    with app.app_context():
        edited = db.session.get(Task, task_id)
        assert edited is not None
        assert edited.title == "Edited Test Task"

def test_edit_completed_task(client, app):
    with app.app_context():
        task = Task(
            title="Test Completed Task",
            type="School",
            due_date=datetime.now() + timedelta(days=1),
            description="edit test",
            status="Incomplete"
        )
        db.session.add(task)
        db.session.commit()
        task_id = task.id

    update_data = {
        "title": "Edited Test Task",
        "type": "School",
        "due_date": (datetime.now() + timedelta(days=2)).strftime("%Y-%m-%d"),
        "description": "edit test updated",
        "status": "Complete"
    }

    response = client.post(f"/tasks/edit/{task_id}", data=update_data, follow_redirects=True)
    assert response.status_code == 200

    with app.app_context():
        edited = db.session.get(Task, task_id)
        assert edited is not None


def test_edit_task_fail_deletion(client, app):
    with app.app_context():
        task = Task(
            title="Test Task",
            type="School",
            due_date=datetime.now() + timedelta(days=1),
            description="edit test",
            status="Incomplete"
        )
        db.session.add(task)
        db.session.commit()
        task_id = task.id

    response = client.post(f"/tasks/edit/{task_id}", follow_redirects=True)
    assert response.status_code == 400 # DOUBLE CHECK

    with app.app_context():
        edited = db.session.get(Task, task_id)
        assert edited is not None # DOUBLE CHECK


def test_task_does_not_exist(client, app):
    dne_id = -1
    response = client.post(f"/tasks/delete/{dne_id}", follow_redirects=True)
    assert response.status_code == 404 #DOUBLE CHECK