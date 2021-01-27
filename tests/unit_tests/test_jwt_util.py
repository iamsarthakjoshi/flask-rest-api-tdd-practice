from app.constants import TokenType
from tests.util import user_data

##### TESTS #####
def test_jwt_encode(client):
    from app.util import custom_jwt_maker

    # access token
    access_token = custom_jwt_maker.encode_jwt(
        token_type=TokenType.ACCESS_TOKEN, user_id="1234"
    )
    assert isinstance(access_token, str)

    # refresh token
    refresh_token = custom_jwt_maker.encode_jwt(
        token_type=TokenType.REFRESH_TOKEN, user_id="1234"
    )
    assert isinstance(refresh_token, str)


def test_jwt_decode_success(client, user):
    from app.util import custom_jwt_maker

    # access token
    access_token = custom_jwt_maker.encode_jwt(
        token_type=TokenType.ACCESS_TOKEN, user_id=user.uuid
    )
    # decode access token
    res = custom_jwt_maker.decode_jwt(token=access_token)
    assert "exp", "uid" in res["payload"]
    assert user.uuid == res["payload"]["uid"]


def test_jwt_decoded_token_expired(client, user):
    import time
    from app.util import custom_jwt_maker

    # access token
    access_token = custom_jwt_maker.encode_jwt(
        token_type=TokenType.ACCESS_TOKEN, user_id=user.uuid
    )
    time.sleep(6)
    # decode access token
    res = custom_jwt_maker.decode_jwt(token=access_token)
    assert not res["decoded"]
    assert res["message"] == "Expired token. Please log in again."


def test_jwt_decoded_token_invalid(client, user):
    import time
    from app.util import custom_jwt_maker

    # access token
    access_token = custom_jwt_maker.encode_jwt(
        token_type=TokenType.ACCESS_TOKEN, user_id=user.uuid
    )
    # decode access token
    res = custom_jwt_maker.decode_jwt(token=access_token + "modified")
    assert not res["decoded"]
    assert res["message"] == "Invalid token. Please log in again."
