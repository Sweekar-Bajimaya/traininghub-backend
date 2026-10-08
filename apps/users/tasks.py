"""Django Q task entrypoints for this app.

Each task is a thin wrapper: catch, log, and swallow so a delivery failure
never surfaces as a worker crash or a retry storm. Callers must generate and
persist any state (OTPs, tokens, etc.) *before* queuing - these functions
only deliver a notification. Add a sibling function per notification type
(registration OTP, login OTP, etc.) following the same shape.

OTP tasks are queued with the address only. The code is read from the cache when the task
runs, so it never sits in the broker payload or in django-q's results table.
"""

import logging

from apps.users.constants import OTPPurpose
from apps.users.services import (
    get_otp,
    send_otp_email,
    send_registration_otp_email,
)

logger = logging.getLogger(__name__)


def _deliver_otp(email, purpose, send):
    otp = get_otp(email, purpose=purpose)
    if otp is None:
        # expired (or used up) before the worker got to it; nothing valid left to send
        logger.warning("OTP for %s (%s) expired before it was emailed", email, purpose)
        return
    try:
        send(email, otp)
    except Exception:
        logger.exception("Failed to send %s OTP email to %s", purpose, email)


def send_otp_email_task(email):
    _deliver_otp(email, OTPPurpose.PASSWORD_RESET, send_otp_email)


def send_registration_otp_email_task(email):
    _deliver_otp(email, OTPPurpose.INSTITUTE_REGISTRATION, send_registration_otp_email)
