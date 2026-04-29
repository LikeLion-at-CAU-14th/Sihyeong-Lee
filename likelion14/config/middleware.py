import logging

request_logger = logging.getLogger('http.request')

class RequestLoggingMiddleware:
    
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        full_url = request.build_absolute_uri()
        message = f"{request.method} {request.get_full_path()} -> {response.status_code}"

        if response.status_code >= 400:
            request_logger.warning(message, extra={"url": full_url})
        else:
            request_logger.info(message, extra={"url": full_url})

        return response

    def process_exception(self, request, exception):
        full_url = request.build_absolute_uri()
        request_logger.exception(
            f"{request.method} {request.get_full_path()} -> unhandled exception: {exception}",
            extra={"url": full_url},
        )