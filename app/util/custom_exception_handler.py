from flask import jsonify


class CustomExceptionHandler(Exception):
    status_code = 400

    def __init__(self, at, message, status_code=None, payload=None):
        """
        Arguments:
            - message: string
            - status_code: number
                - Http Code:
                    1xx Informational 100 Continue 101 Switching Protocols 102 Processing (WebDAV)
                    2xx Success 200 OK 201 Created 202 Accepted 203 Non-Authoritative Information 204 No Content 205 Reset Content 206 Partial Content 207 Multi-Status (WebDAV) 208 Already Reported (WebDAV) 226 IM Used

                    3xx Redirection 300 Multiple Choices 301 Moved Permanently 302 Found 303 See Other 304 Not Modified 305 Use Proxy 306 (Unused) 307 Temporary Redirect 308 Permanent Redirect (experimental)

                    4xx Client Error 400 Bad Request 401 Unauthorized 402 Payment Required 403 Forbidden 404 Not Found 405 Method Not Allowed 406 Not Acceptable 407 Proxy Authentication Required 408 Request Timeout 409 Conflict 410 Gone 411 Length Required 412 Precondition Failed 413 Request Entity Too Large 414 Request-URI Too Long 415 Unsupported Media Type 416 Requested Range Not Satisfiable 417 Expectation Failed 418 I'm a teapot (RFC 2324) 420 Enhance Your Calm (Twitter) 422 Unprocessable Entity (WebDAV) 423 Locked (WebDAV) 424 Failed Dependency (WebDAV) 425 Reserved for WebDAV 426 Upgrade Required 428 Precondition Required 429 Too Many Requests 431 Request Header Fields Too Large 444 No Response (Nginx) 449 Retry With (Microsoft) 450 Blocked by Windows Parental Controls (Microsoft) 451 Unavailable For Legal Reasons 499 Client Closed Request (Nginx)
            - payload: object
        """
        Exception.__init__(self)
        self.message = message
        self.at = at
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv["message"] = self.message
        rv["at"] = self.at
        return rv


""" Implementation
Registering an Error Handler
At that point views can raise that error, but it would immediately result in an internal server error. The reason for this is that there is no handler registered for this error class. That however is easy to add:

@app.errorhandler(InvalidUsage)
def handle_invalid_usage(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response

Usage in Views
Here is how a view can use that functionality:

@app.route('/foo')
def get_foo():
    raise InvalidUsage('This view is gone', status_code=410)


# Source: https://flask.palletsprojects.com/en/1.1.x/patterns/apierrors/
"""
