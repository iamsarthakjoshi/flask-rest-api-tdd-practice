import pyotp
import urllib.parse as urlparse


def get_new_secret():
    """
    :return: random string which is base 32 encoded
    """
    return pyotp.random_base32()


# Time Based OTPs
def get_time_based_otp_provisioning_uri(email):
    new_secret = get_new_secret()
    provisioning_uri = pyotp.totp.TOTP(new_secret).provisioning_uri(
        name=email, issuer_name="Blink"
    )
    return new_secret, provisioning_uri


def get_secret_from_uri(uri):
    parsed = urlparse.urlparse(uri)
    secret = urlparse.parse_qs(parsed.query)["secret"][0]
    return secret


def verify_time_based_otp(secret, otp_code):
    totp = pyotp.TOTP(secret)
    return totp.verify(otp_code)


# s = pyotp.totp.TOTP('JBSWY3DPEHPK3PXP').provisioning_uri("alice@google.com", issuer_name="Secure App")
# print (s)
# otp = OneTimePasswordService()
# secret = otp.get_secret_from_uri(s)
# print(secret)
