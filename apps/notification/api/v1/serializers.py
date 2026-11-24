from rest_framework import serializers

from apps.common.serializers import DynamicFieldsModelSerializer
from apps.notification.models import Notification


class NotificationSerializer(DynamicFieldsModelSerializer):
    is_read = serializers.SerializerMethodField()

    class Meta:
        model = Notification
        fields = (
            "id",
            "type",
            "title",
            "body",
            "payload",
            "is_read",
            "read_at",
            "created_at",
        )
        read_only_fields = fields

    def get_is_read(self, obj):
        return obj.read_at is not None
