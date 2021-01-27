import pytest
import json
from pathlib import Path
from datetime import datetime

from app import create_app, db as database
from app.models import Task


#### GLOBAL PYTEST FIXTURES ####


@pytest.fixture
def client():
    app = create_app()

    app.config["TESTING"] = True
    app.config["MAIL_SUPPRESS_SEND"] = True
    app.config["REDIS_URL"] = "redis://redis:6379/0"
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///unittest_db.db"
    app.config["SECRET_KEY"] = "my_precious"
    BASE_DIR = Path(__file__).resolve().parent.parent

    client = app.test_client()
    with app.app_context():
        yield client  # tests run here


@pytest.fixture
def db(client, request):
    database.drop_all()
    database.create_all()
    database.session.commit()

    def fin():
        database.session.remove()

    request.addfinalizer(fin)
    return database


@pytest.fixture
def user(db):
    from tests.util import user_data
    from app.models import User

    user = User.save_user(user_data, otp_secret=None, otp_provisioning_uri=None)
    db.session.add(user)
    db.session.commit()
    return user
