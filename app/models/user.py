from passlib.hash import sha256_crypt
from datetime import datetime
from dateutil import parser
from uuid import uuid4, UUID

from app import db


class User(db.Model):
    __tablename__ = "user"
    uuid = db.Column(db.String(77), primary_key=True, nullable=False)
    username = db.Column(db.String(77), unique=True, nullable=False)
    name_title = db.Column(db.String(10))
    fullname = db.Column(db.String(100))
    email = db.Column(db.String(150), unique=True)
    contact_number = db.Column(db.String(50))
    profile_image = db.Column(db.String(20), default="avatar.jpg")
    password_hash = db.Column(db.String(77), nullable=False)
    password_recovery_token = db.Column(db.String(255), unique=True)
    email_verification_token = db.Column(db.String(255), unique=True)
    login_verification_token = db.Column(db.String(255), unique=True)
    two_factor_enabled = db.Column(db.Integer, default=0)
    otp_secret = db.Column(db.String(100))
    otp_provisioning_uri = db.Column(db.String(255))
    email_verified = db.Column(db.Integer, nullable=False, default=0)
    security_question_one = db.Column(db.String(255))
    security_question_two = db.Column(db.String(255))
    security_question_three = db.Column(db.String(255))
    last_updated = db.Column(db.DateTime, default=datetime.utcnow)
    last_created = db.Column(db.DateTime, default=None)
    disclaimer_shown = db.Column(db.Boolean, default=False)
    session_id = db.Column(db.String(30), default=None)

    def __repr__(self):
        return f"User {self.uuid} {self.username} {self.email}"

    def __init__(
        self,
        uuid,
        username,
        password_hash,
        email=None,
        name_title=None,
        fullname=None,
        contact_number=None,
        profile_image="avatar.jpg",
        password_recovery_token=None,
        email_verification_token=None,
        login_verification_token=None,
        two_factor_enabled=None,
        otp_secret=None,
        otp_provisioning_uri=None,
        email_verified=None,
        security_question_one=None,
        security_question_two=None,
        security_question_three=None,
        last_created=None,
        disclaimer_shown=False,
        session_id=None,
    ):
        self.uuid = uuid
        self.username = username
        self.password_hash = password_hash
        self.email = email
        self.name_title = name_title
        self.fullname = fullname
        self.contact_number = contact_number
        self.profile_image = profile_image
        self.password_recovery_token = password_recovery_token
        self.email_verification_token = email_verification_token
        self.login_verification_token = login_verification_token
        self.two_factor_enabled = two_factor_enabled
        self.otp_secret = otp_secret
        self.otp_provisioning_uri = otp_provisioning_uri
        self.email_verified = email_verified
        self.security_question_one = security_question_one
        self.security_question_two = security_question_two
        self.security_question_three = security_question_three
        self.disclaimer_shown = disclaimer_shown
        self.last_created = last_created
        self.session_id = session_id

    def to_dict(self):
        return {
            "uuid": self.uuid,
            "username": self.username,
            "name_title": self.name_title,
            "fullname": self.fullname,
            "email": self.email,
            "contact_number": self.contact_number,
            "profile_image": self.profile_image,
            "two_factor_enabled": self.two_factor_enabled,
            "otp_secret": self.otp_secret,
            "otp_provisioning_uri": self.otp_provisioning_uri,
            "email_verified": self.email_verified,
            "security_question_one": self.security_question_one,
            "security_question_two": self.security_question_two,
            "security_question_three": self.security_question_three,
            "last_updated": self.last_updated,
            "last_created": self.last_created,
            "disclaimer_shown": self.disclaimer_shown,
            "session_id": self.session_id,
        }

    @classmethod
    def user_exits(self, user_uuid):
        user = User.query.get(user_uuid)
        return user if user else None

    @staticmethod
    def user_exits(user_uuid):
        user = User.query.get(user_uuid)
        return user if user else None

    @staticmethod
    def user_exits_by_email(email):
        user = User.query.filter_by(email=email).first()
        return user if user else None

    @staticmethod
    def user_exits_by_username(username):
        user = User.query.filter_by(username=username).first()
        return user if user else None

    @classmethod
    def save_user(self, kwargs, otp_secret, otp_provisioning_uri):
        user_id = str(UUID(bytes=uuid4().bytes)).replace("-", "")
        user_email = kwargs["email"]
        two_factor_enabled = (
            kwargs["twoFactorEnabled"] if "twoFactorEnabled" in kwargs else None
        )
        security_answers = kwargs["securityAnswers"]
        user = User(
            uuid=user_id,
            email=user_email,
            password_hash=sha256_crypt.hash(kwargs["password"]),
            username=kwargs["username"] if "username" in kwargs else None,
            name_title=kwargs["nameTitle"] if "nameTitle" in kwargs else None,
            fullname=kwargs["fullname"] if "fullname" in kwargs else None,
            contact_number=kwargs["contactNumber"]
            if "contactNumber" in kwargs
            else None,
            profile_image=kwargs["profileImage"]
            if "profileImage" in kwargs
            else "avatar.png",
            two_factor_enabled=two_factor_enabled,
            otp_secret=otp_secret,  # if two_factor_enabled else None,
            otp_provisioning_uri=otp_provisioning_uri,  # if two_factor_enabled else None,
            email_verified=kwargs["emailVerified"]
            if "emailVerified" in kwargs
            else None,
            security_question_one=security_answers["securityAnswerOne"]
            if "securityAnswerOne" in security_answers
            else None,
            security_question_two=security_answers["securityAnswerTwo"]
            if "securityAnswerTwo" in security_answers
            else None,
            security_question_three=security_answers["securityAnswerThree"]
            if "securityAnswerThree" in security_answers
            else None,
            # last_created = datetime.strptime(kwargs['lastCreated'],'%Y-%m-%dT%H:%M:%SZ') if 'lastCreated' in kwargs else None
        )
        db.session.add(user)
        db.session.commit()
        return User.query.get(user_id)

    @classmethod
    def update_user(self, kwargs):
        # Mandatory fields
        user = self.user_exits(kwargs["uuid"])
        user.username = kwargs["username"] if "username" in kwargs else user.username
        user.email = kwargs["email"] if "email" in kwargs else user.email

        # Optional fields
        user.fullname = kwargs["fullname"] if "fullname" in kwargs else user.fullname
        user.name_title = (
            kwargs["nameTitle"] if "nameTitle" in kwargs else user.name_title
        )
        user.contact_number = (
            kwargs["contactNumber"]
            if "contactNumber" in kwargs
            else user.contact_number
        )
        user.profile_image = (
            kwargs["profileImage"] if "profileImage" in kwargs else user.profile_image
        )

        # Security fields
        user.two_factor_enabled = (
            kwargs["twoFactorEnabled"]
            if "twoFactorEnabled" in kwargs
            else user.two_factor_enabled
        )
        user.email_verified = (
            kwargs["emailVerified"]
            if "emailVerified" in kwargs
            else user.email_verified
        )

        # Optional security question's answers fields
        user.security_question_one = (
            kwargs["securityAnswerOne"]
            if "securityAnswerOne" in kwargs
            else user.security_question_one
        )
        user.security_question_two = (
            kwargs["securityAnswerTwo"]
            if "securityAnswerTwo" in kwargs
            else user.security_question_two
        )
        user.security_question_three = (
            kwargs["securityAnswerThree"]
            if "securityAnswerThree" in kwargs
            else user.security_question_three
        )
        user.disclaimer_shown = (
            kwargs["disclaimerShown"]
            if "disclaimerShown" in kwargs
            else user.disclaimer_shown
        )
        # Commit the changes
        db.session.commit()
        return user
