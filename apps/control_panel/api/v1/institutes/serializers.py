from apps.common import serializers as common_serializers
from apps.institutes.constants import DocumentStatus
from apps.institutes.models import Institute, InstituteDocument
from rest_framework import serializers


class ReasonSerializer(serializers.Serializer):
    reason = serializers.CharField()


# admin review
class AdminDocumentSerializer(common_serializers.DynamicFieldsModelSerializer):
    class Meta:
        model = InstituteDocument
        fields = ("id", "name", "status", "created_at")  # never the file path or URL
        read_only_fields = ("id", "name", "created_at")


class DocumentReviewSerializer(serializers.Serializer):
    status = serializers.ChoiceField(
        choices=(DocumentStatus.VERIFIED, DocumentStatus.REJECTED)
    )


class AdminInstituteSerializer(common_serializers.DynamicFieldsModelSerializer):
    documents = AdminDocumentSerializer(many=True, read_only=True)
    owner_email = serializers.SerializerMethodField()

    class Meta:
        model = Institute
        fields = (
            "id",
            "slug",
            "name",
            "type",
            "status",
            "status_reason",
            "established_year",
            "description",
            "created_at",
            "owner_email",
            "documents",
        )

    def get_owner_email(self, obj):
        owners = getattr(obj, "owner_members", [])  # prefetched by the admin viewset
        return owners[0].user.email if owners else None
