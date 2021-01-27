import logging
from app.security.endpoints import Endpoints
from app.services.user_service import UserService
from app.constants import TokenType


class AccessVerifier:
    __instance = None
    UNAUTHORIZED_ENDPOINTS = {
        Endpoints.signup,
        Endpoints.login,
        Endpoints.logout,
        Endpoints.ping,
        Endpoints.downloadFile,
    }
    ONLY_USER_LOGIN_REQUIRED_EDNPOINTS = {
        Endpoints.fetchUserInfo,
        Endpoints.getStripeCheckoutSessionInfo,
        Endpoints.updateDisclaimerShown,
        Endpoints.fetchDisclaimer,
    }

    @staticmethod
    def get_instance() -> "AccessVerifier":
        if not AccessVerifier.__instance:
            AccessVerifier.__instance = AccessVerifier()
        return AccessVerifier.__instance

    def __init__(self):
        self.user_service = UserService.get_instance()

    def authenticated_request(self, request) -> bool:
        """

        :param request:
        :return: boolean: True or False, depending if the request is authenticated
        """
        user_uuid = request.get_json()["userUuid"]
        api_token = request.get_json()[TokenType.API_TOKEN]
        return self.user_service.tokens_valid(
            user_uuid=user_uuid,
            api_token=api_token,
            cookie_token=None,
            cookie_check=False,
        )

    """ Raises error if not authorized """

    def verify(self, request):
        endpoint = str(request.url_rule)
        if endpoint in AccessVerifier.UNAUTHORIZED_ENDPOINTS:
            return
        if endpoint in AccessVerifier.ONLY_USER_LOGIN_REQUIRED_EDNPOINTS:
            if self.authenticated_request(request=request):
                return
        # Return false if none of the verification conditions are met
        raise Exception("Not authorized")
