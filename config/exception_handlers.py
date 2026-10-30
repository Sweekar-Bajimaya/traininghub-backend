from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import IntegrityError
from rest_framework import exceptions, serializers, status
from rest_framework.views import Response, exception_handler

from apps.common.exceptions import TooManyRequests


def api_exception_handler(exc, context):
    """Map Django's ValidationError (raised from models/services) to a 400
    instead of letting it surface as a 500, and TooManyRequests to a 429."""
    if isinstance(exc, DjangoValidationError):
        exc = serializers.ValidationError(detail=serializers.as_serializer_error(exc))

    if isinstance(exc, TooManyRequests):
        exc = exceptions.Throttled(wait=exc.wait, detail=exc.message)

    if isinstance(exc, IntegrityError):
        return Response(
            {"detail": "Conflict with existing data."}, status=status.HTTP_409_CONFLICT
        )

    return exception_handler(exc, context)
