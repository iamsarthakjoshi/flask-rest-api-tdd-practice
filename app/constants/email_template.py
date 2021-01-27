class EmailTemplate:
    COMMON = "common.html"
    RESET_PASSWORD = "resetPassword.html"
    EMAIL_VERIFICATION = "verifyAccount.html"
    IDENTITY_VERIFICATION = "verifyIdentity.html"
    WELCOME_ABOARD = "welcomeAboard.html"

    # Email Subjects
    RESET_PASSWORD_SUBJECT = "Reset Password"
    EMAIL_VERIFICATION_SUBJECT = "Verify Your Email"
    IDENTITY_VERIFICATION_SUBJECT = "Verify Your Identity"
    WELCOME_ABOARD_SUBJECT = "Welcome to Our Platform"

    # Domain url endpoint
    RESET_PASSWORD_ENDPOINT = "/reset-password"
    EMAIL_VERIFICATION_ENDPOINT = "/email-verification"
