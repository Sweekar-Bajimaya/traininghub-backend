class TooManyRequests(Exception):
    """Raised by a service when the caller must wait (a resend cooldown, too many wrong codes).

    `api_exception_handler` turns it into a 429 with a `Retry-After` header, so services do not
    need to import DRF.
    """

    def __init__(self, message, *, wait=None):
        super().__init__(message)
        self.message = message
        self.wait = wait
