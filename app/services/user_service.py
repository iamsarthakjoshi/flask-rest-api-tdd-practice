import os
import copy
import secrets
from uuid import uuid4
from flask import current_app as app
from passlib.hash import sha256_crypt

from app import db
from app.models import User
from app.util import (
    encode_jwt,
    decode_jwt,
    launch_async_task,
    get_time_based_otp_provisioning_uri,
    verify_time_based_otp,
    format_error_log,
    CustomExceptionHandler,
)
from app.constants import TokenType, EmailTemplate, TwoFactorAuthType, TaskType
from config import qr_code_image_base_url, user_security_questions
from app.api_clients import StrapiDataRetriever

domain_url = os.getenv("DOMAIN_URL", "Domain-URL-Not-Assigned")
logger = app.logger

# load singleton
strapi_api = StrapiDataRetriever.get_instance()


class UserService:
    __instance = None

    @staticmethod
    def get_instance() -> "UserService":
        if not UserService.__instance:
            UserService.__instance = UserService()

        return UserService.__instance

    def __init__(self):
        UserService.__instance = self
        self.cache = {}

    def _get_token_cache_key(self, token_type, key):
        return token_type + "_" + key

    def user_exists_by_email(self, email):
        user = User.query.filter_by(email=email).first()
        if not user:
            raise CustomExceptionHandler(
                at="user_exists_by_email",
                message="User does not exits.",
                status_code=404,
            )

    def user_exists_by_id(self, user_uuid):
        if not user_uuid:
            raise CustomExceptionHandler(
                at="user_exists_by_id", message="User Id is missing.", status_code=404
            )
        user = User.query.get(user_uuid)
        if not user:
            raise CustomExceptionHandler(
                at="user_exists_by_id", message="User does not exits.", status_code=404
            )
        return user

    def get_user_info(self, user_uuid):
        user = self.user_exists_by_id(user_uuid=user_uuid)
        return user.to_dict()

    def udpate_disclaimer_shown(self, user_uuid, disclaimer_shown):
        data = {
            "uuid": user_uuid,
            "disclaimerShown": disclaimer_shown,
        }
        user = User.update_user(kwargs=data)
        return {"isUpdated": True, "disclaimerShown": user.disclaimer_shown}

    def get_disclaimer(self, user_uuid):
        user = self.user_exists_by_id(user_uuid=user_uuid)
        disclaimers = strapi_api.retrieve_disclaimers()
        disclaimer = next(filter(lambda x: x["active"] == True, disclaimers), None)
        if disclaimer:
            return {"disclaimer": disclaimer["disclaimer"]}
        else:
            return {"disclaimer": None}

    def signup(self, kwargs):
        # verify user existence
        user_email = User.user_exits_by_email(kwargs["email"])
        user_name = User.user_exits_by_username(kwargs["username"])
        if user_email or user_name:
            raise CustomExceptionHandler(
                at="singup",
                status_code=401,
                message=f"{'Username' if user_name else 'User email'} already exits.",
            )

        # generate otp secret for 2FA even if user does not select otp as an 2FA option so that a qr code can be
        # displayed in their profile page in ui to enable 2FA later
        otp_secret, otp_provisioning_uri = get_time_based_otp_provisioning_uri(
            email=kwargs["email"]
        )

        # attemp to save new user
        user = User.save_user(kwargs, otp_secret, otp_provisioning_uri)

        # Send email verification link to the user
        data = self.send_account_verification_email(email=user.email)
        return data

    def login(self, email_or_username, password, otp, security_answers, twoFA_type):
        # find user
        user_email = User.query.filter_by(email=email_or_username).first()
        user_name = User.query.filter_by(username=email_or_username).first()

        # check user existence
        if not user_email and not user_name:
            raise CustomExceptionHandler(
                at="login", message="User does not exits", status_code=404
            )

        # assign user from either from email or username
        user = user_email if user_email else user_name if user_name else None

        # if not app.debug:
        # compare password
        if not sha256_crypt.verify(password, user.password_hash):
            raise CustomExceptionHandler(
                at="login", message="Inavlid Password.", status_code=401
            )

        # check email verified if user valid
        if not bool(int(user.email_verified)):
            # send email verification again
            task_id = self.send_account_verification_email(email=user.email)
            raise CustomExceptionHandler(
                at="login",
                message="Email verification needed. We have just sent you a verificaiton link in your email.",
                status_code=403,
            )

        otp_length = len(str(otp))
        is2FA = bool(user.two_factor_enabled)

        # if user select OTP as 2FA in UI Login
        if twoFA_type == TwoFactorAuthType.OTP:
            if not is2FA and otp_length > 0:
                # check if 2FA is disabled and when user sends fake otp code
                raise CustomExceptionHandler(
                    at="login",
                    message="You don't have 2FA enabled. Please try with security questions.",
                    status_code=403,
                )
            elif not is2FA and otp_length == 0 or is2FA and otp_length == 0:
                raise CustomExceptionHandler(
                    at="login",
                    message="Missing OTP Code. Please try again with new code.",
                    status_code=403,
                )
            elif (
                is2FA
                and otp_length > 0
                and not verify_time_based_otp(user.otp_secret, otp)
            ):
                # check if 2FA is enabled and when user sends otp code
                raise CustomExceptionHandler(
                    at="login",
                    message="Invalid OTP Code. Please try again with new code.",
                    status_code=403,
                )

        # if user select QNA as 2FA in UI Login
        if twoFA_type == TwoFactorAuthType.QNA:
            if (
                security_answers["securityAnswerOne"] != user.security_question_one
                or security_answers["securityAnswerTwo"] != user.security_question_two
                or security_answers["securityAnswerThree"]
                != user.security_question_three
            ):
                raise CustomExceptionHandler(
                    at="login",
                    message="Answers does not match. Please try again.",
                    status_code=403,
                )

        # generate refresh and access tokens
        refresh_token = encode_jwt(TokenType.REFRESH_TOKEN, user.uuid)
        access_token = encode_jwt(TokenType.ACCESS_TOKEN, user.uuid)

        return {
            "userUuid": user.uuid,
            "username": user.username,
            "refresh": refresh_token,
            "access": access_token,
            TokenType.API_TOKEN: secrets.token_hex(32),
            TokenType.COOKIE_TOKEN: secrets.token_hex(32),
        }

    def tokens_valid(self, user_uuid, api_token, cookie_token, cookie_check):
        # Check the api token against cache
        api_cache_key = self._get_token_cache_key(TokenType.API_TOKEN, api_token)
        if not api_cache_key in self.cache or self.cache[api_cache_key] != user_uuid:
            return False
        # Check the cookie only if cookie checks have been enabled
        cookie_cache_key = self._get_token_cache_key(TokenType.COOKIE_TOKEN, api_token)
        if cookie_check and (
            not cookie_cache_key in self.cache
            or self.cache[cookie_cache_key] != user_uuid
        ):
            return False
        return True

    def logout(self, cookie_token, api_token):
        # Delete tokens from cache if they exist
        if api_token:
            api_cache_key = self._get_token_cache_key(TokenType.API_TOKEN, api_token)
            self.cache.pop(api_cache_key, None)
        if cookie_token:
            cookie_cache_key = self._get_token_cache_key(
                TokenType.COOKIE_TOKEN, cookie_token
            )
            self.cache.pop(cookie_cache_key, None)

    def send_reset_password_email(self, email):
        user = User.query.filter_by(email=email).first()
        if not user:
            raise Exception("Your email does not exist in our database.")

        user_id = user.uuid
        user_email = user.email

        # generate reset link+token
        password_reset_token = encode_jwt(TokenType.RESET_PASSWORD, user_id)
        reset_link = f"{domain_url}{EmailTemplate.RESET_PASSWORD_ENDPOINT}/{password_reset_token}"

        # set password_recovery_token in user db for later verificaiton
        user.password_recovery_token = password_reset_token
        db.session.commit()

        # data for send_email_with_template task
        data = {
            "html_data": {
                "action_url": reset_link,
                "support_contact": os.getenv("SUPPORT_CONTACT", None),
                "support_email": os.getenv("SUPPORT_EMAIL", None),
            },
            "user_id": user_id,
            "email_template": EmailTemplate.RESET_PASSWORD,
            "email_subject": EmailTemplate.RESET_PASSWORD_SUBJECT,
            "recipients": [user_email],
        }

        # launch rq task
        task_id = launch_async_task(name="send_email_with_template", kwargs=data)
        return task_id

    def reset_password(self, confirm_password, token):
        payload = decode_jwt(token=token)
        if not payload["decoded"]:
            raise CustomExceptionHandler(
                at="reset_password", message=payload["message"], status_code=401
            )

        payload = payload["payload"]
        user = User.query.filter_by(
            uuid=payload["uid"], password_recovery_token=token
        ).first()
        if not user:
            raise CustomExceptionHandler(
                at="reset_password",
                message="User or recovery token is invalid.",
                status_code=401,
            )

        user.password_hash = sha256_crypt.hash(confirm_password)
        user.password_recovery_token = None
        db.session.commit()
        return user.uuid

    def send_account_verification_email(self, email):
        user = User.query.filter_by(email=email).first()
        if not user:
            raise Exception("User email does not exist in our database.")

        user_id = user.uuid
        user_email = user.email

        # generate otp provisioning_uri to image src
        otp_provisioning_uri = user.otp_provisioning_uri
        qr_code_image_src = f"{qr_code_image_base_url}{otp_provisioning_uri}"

        # generate reset link+token
        email_verification_token = encode_jwt(TokenType.EMAIL_VERIFICATION, user_id)
        reset_link = f"{domain_url}{EmailTemplate.EMAIL_VERIFICATION_ENDPOINT}/{email_verification_token}"

        # set password_recovery_token in user db for later verificaiton
        user.email_verification_token = email_verification_token
        db.session.commit()

        # data for send_email_with_template task
        data = {
            "html_data": {
                "action_url": reset_link,
                "qr_code_image_src": qr_code_image_src,
                "support_contact": os.getenv("SUPPORT_CONTACT", None),
                "support_email": os.getenv("SUPPORT_EMAIL", None),
            },
            "user_id": user_id,
            "email_template": EmailTemplate.EMAIL_VERIFICATION,
            "email_subject": EmailTemplate.EMAIL_VERIFICATION_SUBJECT,
            "recipients": [user_email],
            "verification_token": email_verification_token,
        }

        # launch rq task
        task_id = launch_async_task(name="send_email_with_template", kwargs=data)

        # add taskid to data
        data["task_id"] = task_id
        return data

    def verify_email(self, token):
        payload = decode_jwt(token=token)
        if not payload["decoded"]:
            raise CustomExceptionHandler(
                at="verify_email", message=payload["message"], status_code=401
            )

        payload = payload["payload"]
        user = User.query.filter_by(
            uuid=payload["uid"], email_verification_token=token
        ).first()
        if not user:
            raise CustomExceptionHandler(
                at="verify_email",
                message="User or verification token is invalid.",
                status_code=401,
            )

        # update data and return user obj for login stuff
        user.email_verified = True
        user.email_verification_token = None
        db.session.commit()

        # user info
        username = user.username

        # send user welcome message via email
        data = {
            "html_data": {
                "username": username,
                "login_page_url": os.getenv("DOMAIN_LOGIN_URL", None),
                "support_contact": os.getenv("SUPPORT_CONTACT", None),
                "support_email": os.getenv("SUPPORT_EMAIL", None),
            },
            "user_id": user.uuid,
            "email_template": EmailTemplate.WELCOME_ABOARD,
            "email_subject": EmailTemplate.WELCOME_ABOARD_SUBJECT,
            "recipients": [user.email],
        }

        # launch rq task
        task_id = launch_async_task(name="send_email_with_template", kwargs=data)
        logger.info(
            "Verify email: Welcome email sent to user {username}. Task id: {task_id}"
        )

        return user
