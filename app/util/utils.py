# import pytest
# import json
# from pathlib import Path
# from datetime import datetime

# from app import create_app
# from app.constants import TokenType


# #### FIXTURES ####

# @pytest.fixture
# def client():
#     app = create_app()

#     app.config["TESTING"] = True
#     app.config["MAIL_SUPPRESS_SEND"] = True
#     app.config["SECRET_KEY"] = "my_precious"
#     BASE_DIR = Path(__file__).resolve().parent.parent

#     client = app.test_client()
#     with app.app_context():
#         yield client  # tests run here

# #### TESTS ####
# def test_jwt_encode():
#     from app.util import custom_jwt_maker
#     access_token = custom_jwt_maker.encode_jwt(token_type=TokenType.ACCESS_TOKEN, user_id=100)
#     assert isinstance(access_token, bytes)
