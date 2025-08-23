# core/middleware/request_id.py
import uuid
import logging

class RequestIDMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        rid = request.META.get("HTTP_X_REQUEST_ID") or uuid.uuid4().hex
        request.request_id = rid

        # store globally so all future logs use it
        logging._current_request_id = rid

        response = self.get_response(request)
        response["X-Request-ID"] = rid
        return response
