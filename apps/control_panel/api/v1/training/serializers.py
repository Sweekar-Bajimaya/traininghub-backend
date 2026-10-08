# admin review
from apps.common.serializers import DynamicFieldsModelSerializer, DynamicFieldsSerializer
from apps.training.api.v1.serializers import LearningOutcomeSerializer, PortalTrainingListSerializer, PortalTrainingSerializer, TrainingModuleSerializer, TrainingSessionSerializer
from rest_framework import serializers

from apps.training.models import Training

class AdminTrainingListSerializer(PortalTrainingListSerializer):
    institute_name = serializers.CharField(source="institute.name", read_only=True)

    class Meta(PortalTrainingListSerializer.Meta):
        fields = PortalTrainingListSerializer.Meta.fields + ("institute_name",)


class AdminTrainingSerializer(DynamicFieldsModelSerializer):
    """Read-only view of a whole training for the reviewer."""

    institute = serializers.SerializerMethodField()
    category = serializers.SerializerMethodField()
    institute_location = serializers.SerializerMethodField()
    sessions = TrainingSessionSerializer(many=True, read_only=True)
    modules = TrainingModuleSerializer(many=True, read_only=True)
    outcomes = LearningOutcomeSerializer(many=True, read_only=True)

    class Meta:
        model = Training
        fields = PortalTrainingSerializer.Meta.fields + ("institute",)
        read_only_fields = fields

    def get_institute(self, obj):
        return {
            "id": obj.institute_id,
            "name": obj.institute.name,
            "status": obj.institute.status,
        }

    def get_category(self, obj):
        parent = obj.category.parent
        return {
            "id": obj.category_id,
            "name": obj.category.name,
            "parent": parent.name if parent else None,
        }

    def get_institute_location(self, obj):
        place = obj.institute_location
        if place is None:
            return None
        return {
            "id": place.id,
            "municipality": place.location.name,
            "address": place.address,
        }


class TrainingReasonSerializer(DynamicFieldsSerializer):
    reason = serializers.CharField()
