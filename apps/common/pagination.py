from rest_framework.pagination import LimitOffsetPagination


class CappedLimitOffsetPagination(LimitOffsetPagination):
    """`limit` / `offset` paging with a ceiling on `limit`.

    Plain `LimitOffsetPagination` has no ceiling, so a public list answers
    `?limit=100000` with the whole table in one request. A `limit` above `max_limit` is
    lowered to it (not an error); a missing, zero or negative `limit` is `PAGE_SIZE`."""

    max_limit = 100
