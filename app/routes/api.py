import rq
import stripe
import pdfkit
import os, traceback, json
from functools import wraps
from flask import (
    Flask,
    request,
    abort,
    jsonify,
    make_response,
    send_file,
    Response,
    render_template,
    current_app,
)
from flask_cors import CORS
from app.security import Endpoints, AccessVerifier
from app.services.user_service import UserService
from app.routes import api_bp as api
from app.util import (
    jwt_required,
    sanitize_request,
    format_error_log,
    launch_async_task,
    CustomExceptionHandler,
    validate_cart_items,
    get_inventory_with_valid_image_value,
)
from app.tasks import test_task
from app.models import Task
from app.api_clients import StrapiDataRetriever
from app.constants import TokenType
from app import db

# Security check settings
COOKIE_CHECK = False  # Set to False because cookies need to be from the same domain and are currently not
TWO_FA_NEEDED = False

# Load singletons
verifier = AccessVerifier.get_instance()
user_service = UserService.get_instance()

# Load API Client Singletons
strapi_api = StrapiDataRetriever.get_instance()

# Cache userid
temp_user_id = {}

# logger
logger = current_app.logger


def make_error_message(message):
    return jsonify(message=message)


# Catch all error handler
@api.errorhandler(500)
def handle_error(e):
    logger.error(format_error_log(message=str(e)))
    return make_error_message("Unexpected server error, please try again!")


# Error response support function
@api.errorhandler(CustomExceptionHandler)
def handle_invalid_usage(error):
    logger.error(format_error_log(at=error.at, message=error.message))
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response


@api.route("test_async_task", methods=["POST", "GET"])
def test_async_task():
    rq_job = launch_async_task(name="test_task")
    job_id = rq_job.get_id()  # or job.id
    job_status = rq_job.get_status()  # job.status
    current_app.logger.info({"id": str(job_id), "text": f"{str(job_id)} {job_status}!"})
    return jsonify({"status": "executed", "job_id": job_id, "job_status": job_status})


# Endpoints
@api.route(Endpoints.ping, methods=["POST", "GET"])
def ping():
    return jsonify(message="pong", status="success")


@api.route(Endpoints.resetPassword, methods=["POST"])
@sanitize_request
def reset_password():
    body = request.get_json()
    password = body.get("password", None)
    confirm_password = body.get("confirmPassword", None)
    recovery_token = body.get("recoveryToken", None)
    if password != confirm_password:
        raise Exception("Passwords does not match.")
    user_id = user_service.reset_password(
        confirm_password=confirm_password, token=recovery_token
    )
    return (
        jsonify(
            message=f"Password has been successfully reset for userid: {user_id}",
            status=200,
        ),
        200,
    )


@api.route(Endpoints.resetPasswordRequest, methods=["POST"])
def reset_password_request():
    try:
        # verifier.verify(request)
        body = request.get_json()
        email = body.get("email", None)
        user = user_service.user_exists_by_email(email=email)
        task_id = user_service.send_reset_password_email(email=email)
        return (
            jsonify(
                message=f"Reset Password request successful with task id: {task_id}",
                status=201,
            ),
            201,
        )
    except Exception as e:
        logger.error(format_error_log(at="reset_password_request"))
        return jsonify(error=str(e), status=404), 404


@api.route(Endpoints.verifyEmail, methods=["POST"])
def verify_email():
    body = request.get_json()
    verification_token = body.get("verificationToken", None)
    if not verification_token:
        raise CustomExceptionHandler(
            at="verify_email",
            message="Email verification token is missing.",
            status_code=403,
        )
    user = user_service.verify_email(token=verification_token)
    # TODO: create refresh+access token
    # TODO: send tokens or redirect user to login for login
    return jsonify(token="token"), 200


@api.route(Endpoints.signup, methods=["POST"])
def signup():
    # verifier.verify(request)
    data = request.get_json()
    task_id = user_service.signup(kwargs=data)["task_id"]

    return (
        jsonify(
            message=f"Signup request was successful with task id: {task_id}", status=201
        ),
        201,
    )
    # return jsonify(data=response), 201


@api.route(Endpoints.login, methods=["POST"])
# @sanitize_request
def login():
    body = request.get_json()
    email_or_username = body.get("emailOrUsername", None)
    username = body.get("username", None)
    password = body.get("password", None)
    twoFA_type = body.get("twoFA", None)
    otp = body.get("otp", None)
    security_answers = body.get("securityAnswers", None)
    resp = user_service.login(
        email_or_username, password, otp, security_answers, twoFA_type
    )
    return jsonify(resp), 200


@api.route(Endpoints.logout, methods=["POST"])
def logout():
    try:
        # verifier.verify(request)
        api_token = request.get_json()[TokenType.API_TOKEN]
        user_service.logout(cookie_token=None, api_token=api_token)
        return jsonify(message="Successfully logged out.", status=200), 200
    except Exception as e:
        logger.error(format_error_log(at="logout"))
        return jsonify(error=str(e), status=404), 404


@api.route(Endpoints.downloadFile, methods=["GET"])
def download_file():
    # filename = body.get("filename", None)
    # get file from bucket or static
    # file = get_file(filename)
    return send_file("file.pdf", as_attachment=True)


@api.route(Endpoints.fetchUserInfo, methods=["POST"])
@jwt_required
def fetch_user_info():
    body = request.get_json()
    user_uuid = body.get("userUuid", None)
    return jsonify(user_service.get_user_info(user_uuid=user_uuid)), 200


@api.route(Endpoints.updateDisclaimerShown, methods=["POST"])
# @jwt_required
def udpate_disclaimer_shown():
    body = request.get_json()
    user_uuid = body.get("userUuid", None)
    disclaimer_shown = body.get("disclaimerShown", None)
    return (
        jsonify(
            user_service.udpate_disclaimer_shown(
                user_uuid=user_uuid, disclaimer_shown=disclaimer_shown
            )
        ),
        200,
    )


@api.route(Endpoints.fetchDisclaimer, methods=["POST"])
# @jwt_required
def fetch_disclaimer():
    body = request.get_json()
    user_uuid = body.get("userUuid", None)
    return jsonify(user_service.get_disclaimer(user_uuid=user_uuid)), 200


@api.route(Endpoints.rqJob, defaults={"job_id": None}, methods=["GET"])
@api.route(Endpoints.rqJob + "/<job_id>", methods=["GET"])
def rq_job(job_id):
    try:
        task = Task()
        job = task.get_rq_job(job_id)
        if not job:
            return jsonify(error="Invalid Job Id"), 404
        response = {"job_id": job.id, "status": job.get_status(), "result": job.result}
        return jsonify(job_id), 200
    except Exception as e:
        logger.error(format_error_log(at="rq_job"))
        return jsonify(error=str(e), status=404), 404


@api.route(Endpoints.rqJobs, methods=["GET"])
def rq_jobs():
    try:
        return jsonify(tasks=Task.get_rq_jobs())
    except Exception as e:
        logger.error(format_error_log(at="rq_jobs"))
        return jsonify(error=str(e), status=404), 404


# Stripe Payment Stuff
@api.route(Endpoints.createStripeCheckoutSession, methods=["POST"])
# @jwt_required
def create_stripe_checkout_session():
    body = request.get_json()
    cart_details = body.get("cartDetails", None)  # productsJSON
    inventory = get_inventory_with_valid_image_value(strapi_api.retrieve_products())
    line_items = validate_cart_items(inventory, cart_details)
    checkout_session = stripe.checkout.Session.create(
        line_items=line_items,
        mode="payment",
        payment_method_types=["card"],
        success_url=os.getenv("STRIPE_SUCCESS_URL"),
        cancel_url=os.getenv("STRIPE_CANCELED_URL"),
    )
    return jsonify(sessionId=checkout_session["id"]), 200


# Fetch the Checkout Session to display the JSON result on the success page
@api.route(Endpoints.getStripeCheckoutSessionInfo, methods=["POST"])
# @jwt_required
def get_stripe_checkout_session():
    body = request.get_json()
    id = body.get("sessionId", None)
    checkout_session = stripe.checkout.Session.retrieve(id)
    return jsonify(checkout_session)


# Stripe WebHooks
@api.route(Endpoints.stripeWebhook, methods=["POST"])
def stripe_webhook():
    """
    You can use webhooks to receive information about asynchronous payment events.
    For more about webhook events check out https://stripe.com/docs/webhooks.

    DO NOT FORGET: to put this endpoint in stripe's webhook's details
    """
    webhook_secret = os.getenv("STRIPE_WEBHOOK_SECRET")
    request_data = json.loads(request.data)

    # Retrieve the event by verifying the signature using the raw body and secret if webhook signing is configured.
    signature = request.headers.get("Stripe-Signature", None)
    if not signature:
        return jsonify(message="No Signature Header!"), 400

    if webhook_secret:
        try:
            event = stripe.Webhook.construct_event(
                payload=request.data, sig_header=signature, secret=webhook_secret
            )
            data = event["data"]
        except ValueError as e:
            return jsonify(message="Invalid payload"), 400
        except stripe.error.SignatureVerificationError as e:
            return jsonify(message="Invalid signature"), 400
        except Exception as e:
            return jsonify(message=str(e)), 400
        # Get the type of webhook event sent - used to check the status of PaymentIntents.
        event_type = event["type"]
    else:
        data = request_data["data"]
        event_type = request_data["type"]

    data_object = data["object"]

    if event_type == "invoice.paid" or event_type == "invoice.payment_succeeded":
        print(f"===={event_type}===")

    return jsonify(status="ok"), 200
