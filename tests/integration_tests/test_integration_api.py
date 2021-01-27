import pytest
import json
from pathlib import Path
from datetime import datetime

from app import create_app, db
from app.models import Task


#### FIXTURES ####


@pytest.fixture
def client():
    app = create_app()

    app.config["TESTING"] = True
    app.config["MAIL_SUPPRESS_SEND"] = True
    app.config["REDIS_URL"] = "redis://redis:6379/0"
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///integration_db.db"
    app.config["SECRET_KEY"] = "my_precious"
    BASE_DIR = Path(__file__).resolve().parent.parent

    client = app.test_client()

    with app.app_context():
        db.create_all()  # setup
        yield client  # tests run here
        # teardown
        # db.drop_all()


#### HELPER FUNCTIONS ####
def signup(client, data):
    return client.post("/api/signup", json=data)


def login(client, data):
    return client.post("/api/login", json=data)


def verify_email(client, data):
    from app.services.user_service import UserService

    # load singletons
    user_service = UserService.get_instance()
    # fake sending verfication email to the user
    email_verfication_res = user_service.send_account_verification_email(data["email"])
    # get verification token
    verification_token = {
        "verificationToken": email_verfication_res["verification_token"]
    }
    return client.post("/api/verifyEmail", json=verification_token)


##### TESTS #####


def test_server_health(client):
    res = client.get("/api/ping")
    assert res.status_code == 200
    data = json.loads(res.data)
    assert data["message"] == "pong"
    assert data["status"] == "success"


def test_sign_up_logining_unverified_email(client):
    from tests.util import user_data

    # attemp to signup
    res = signup(client, user_data)
    assert res.status_code == 201

    # attemp to login with unverified email
    login_creds = {"emailOrUsername": "foo@foo.com", "password": "password"}
    res = login(client, login_creds)
    assert res.status_code == 403


def test_logining_verified_email(client):
    from tests.util import user_data

    # attemp to verify email
    res = verify_email(client, user_data)
    assert res.status_code == 200

    # attemp to login with verified email
    login_creds = {"emailOrUsername": "foo@foo.com", "password": "password"}
    res = login(client, login_creds)
    assert res.status_code == 200
