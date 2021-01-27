import json
import requests
import os
from flask import current_app as app


class StrapiDataRetriever:

    __instance = None

    @staticmethod
    def get_instance() -> "StrapiDataRetriever":
        if not StrapiDataRetriever.__instance:
            StrapiDataRetriever.__instance = StrapiDataRetriever()
        return StrapiDataRetriever.__instance

    def __init__(self):
        self.url = (
            os.environ["STRAPI_SERVICE_URL"]
            if "STRAPI_SERVICE_URL" in os.environ
            else "http://127.0.0.1:1337"
        )
        self.headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
        }

    def retrieve_products(self, data={}):
        request_url = self.url + "/products"
        resp = requests.get(request_url, data=json.dumps(data), headers=self.headers)
        return json.loads(resp.text)

    def retrieve_disclaimers(self, data={}):
        request_url = self.url + "/disclaimers"
        resp = requests.get(request_url, data=json.dumps(data), headers=self.headers)
        return json.loads(resp.text)
