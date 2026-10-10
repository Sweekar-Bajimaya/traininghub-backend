from django.db.models import Q
from rest_framework import serializers

from apps.common.models.category import Category
from apps.common.serializers import (
    DynamicFieldsModelSerializer,
    DynamicFieldsSerializer,
)
from apps.common.validators import validate_phone_number
from apps.institutes.models import InstituteLocation
from apps.institutes.validators import validate_image_file
from apps.training import services
from apps.training.constants import WeekDay
from apps.training.models import (
    LearningOutcome,
    Training,
    TrainingModule,
    TrainingSession,
)

DAY_LABELS = dict(WeekDay.CHOICES)


def format_class_days(days):
    """['SUN', 'MON', 'TUE', 'WED', 'THU', 'FRI'] gives 'Sun – Fri'; a gap gives 'Sun, Tue, Thu'."""
    indexes = sorted(WeekDay.ORDER.index(d) for d in set(days))
    if len(indexes) > 2 and indexes == list(range(indexes[0], indexes[-1] + 1)):
        return f"{DAY_LABELS[WeekDay.ORDER[indexes[0]]]} – {DAY_LABELS[WeekDay.ORDER[indexes[-1]]]}"
    return ", ".join(DAY_LABELS[WeekDay.ORDER[i]] for i in indexes)


def duration_text(obj):
    if not obj.duration_value:
        return ""
    unit = obj.duration_unit.lower()
    return f"{obj.duration_value} {unit[:-1] if obj.duration_value == 1 else unit}"


# public
class PublicTrainingListSerializer(DynamicFieldsModelSerializer):
    """Everything here comes from select_related rows: no per-row queries."""

    duration = serializers.SerializerMethodField()
    institute = serializers.SerializerMethodField()
    category = serializers.SerializerMethodField()
    location = serializers.SerializerMethodField()
    skills = serializers.ListField(source="detail.skills", read_only=True)

    class Meta:
        model = Training
        fields = (
            "id",
            "slug",
            "title",
            "short_description",
            "mode",
            "level",
            "duration",
            "fee_npr",
            "start_date",
            "end_date",
            "registration_deadline",
            "cover_image",
            "skills",
            "institute",
            "category",
            "location",
            "published_at",
        )

    def get_duration(self, obj):
        return {
            "value": obj.duration_value,
            "unit": obj.duration_unit,
            "weeks": obj.duration_weeks,
            "text": duration_text(obj),
        }

    def get_institute(self, obj):
        institute = obj.institute
        return {
            "slug": institute.slug,
            "name": institute.name,
            "logo": institute.logo.url if institute.logo else None,
        }

    def get_category(self, obj):
        parent = obj.category.parent
        return {
            "id": obj.category_id,
            "name": obj.category.name,
            "parent": {"id": parent.id, "name": parent.name} if parent else None,
        }

    def get_location(self, obj):
        place = obj.institute_location
        if place is None:
            return None  # online
        return {
            "municipality": place.location.name,
            "district": place.location.district.name,
            "province": place.location.province.name,
            "address": place.address,
            "map_url": place.map_url,
        }


class PublicTrainingDetailSerializer(PublicTrainingListSerializer):
    """sessions, modules and outcomes are prefetched in order by the view."""

    overview = serializers.CharField(source="detail.overview", read_only=True)
    eligibility = serializers.CharField(source="detail.eligibility", read_only=True)
    certification = serializers.CharField(source="detail.certification", read_only=True)
    schedule = serializers.SerializerMethodField()
    modules = serializers.SerializerMethodField()
    outcomes = serializers.SerializerMethodField()
    contact = serializers.SerializerMethodField()

    class Meta(PublicTrainingListSerializer.Meta):
        fields = PublicTrainingListSerializer.Meta.fields + (
            "overview",
            "eligibility",
            "certification",
            "seats",
            "schedule",
            "modules",
            "outcomes",
            "contact",
        )

    def get_schedule(self, obj):
        return [
            {
                "class_days": s.class_days,
                "class_days_text": format_class_days(s.class_days),
                "start_time": s.start_time,
                "end_time": s.end_time,
            }
            for s in obj.sessions.all()
        ]

    def get_modules(self, obj):
        return [
            {"title": m.title, "description": m.description} for m in obj.modules.all()
        ]

    def get_outcomes(self, obj):
        return [o.text for o in obj.outcomes.all()]

    def get_contact(self, obj):
        # a missing row raises an AttributeError subclass, so getattr falls back to the default
        own = getattr(obj, "contact", None)
        institute = getattr(obj.institute, "contact", None)
        return {
            "person": own.contact_person if own else "",
            "phone": (own.contact_phone if own else "")
            or (institute.contact_phone if institute else ""),
            "email": (own.contact_email if own else "")
            or (institute.contact_email if institute else ""),
        }


# portal (the institute's own staff)
class TrainingSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrainingSession
        fields = ("class_days", "start_time", "end_time")


class TrainingModuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrainingModule
        fields = ("title", "description")


class LearningOutcomeSerializer(serializers.ModelSerializer):
    class Meta:
        model = LearningOutcome
        fields = ("text",)


class OwnLocationField(serializers.PrimaryKeyRelatedField):
    """Only the caller's own active locations are valid; anything else reads as an unknown id."""

    def get_queryset(self):
        membership = getattr(self.context["request"].user, "membership", None)
        if membership is None:  # schema generation
            return InstituteLocation.objects.none()
        return InstituteLocation.objects.filter(
            institute_id=membership.institute_id, is_active=True
        )


def available_categories():
    return Category.objects.filter(is_active=True).filter(
        Q(parent__isnull=True) | Q(parent__is_active=True)
    )


class TrainingContentFields(serializers.Serializer):
    """The flat fields that live on `TrainingDetail` and `TrainingContact`, so the API keeps one
    flat training. Writes arrive nested (`validated_data["detail"]`), as `services` takes them."""

    overview = serializers.CharField(
        source="detail.overview", required=False, allow_blank=True
    )
    eligibility = serializers.CharField(
        source="detail.eligibility", required=False, allow_blank=True
    )
    certification = serializers.CharField(
        source="detail.certification", required=False, allow_blank=True, max_length=255
    )
    skills = serializers.ListField(
        source="detail.skills",
        child=serializers.CharField(max_length=60),
        required=False,
    )
    contact_person = serializers.CharField(
        source="contact.contact_person",
        required=False,
        allow_blank=True,
        max_length=150,
    )
    contact_phone = serializers.CharField(
        source="contact.contact_phone",
        required=False,
        allow_blank=True,
        max_length=25,
        validators=[validate_phone_number],
    )
    contact_email = serializers.EmailField(
        source="contact.contact_email", required=False, allow_blank=True
    )


class PortalTrainingSerializer(TrainingContentFields, DynamicFieldsModelSerializer):
    """A nested list replaces the whole list; leave it out to keep it."""

    category = serializers.PrimaryKeyRelatedField(queryset=available_categories())
    institute_location = OwnLocationField(required=False, allow_null=True)
    sessions = TrainingSessionSerializer(many=True, required=False)
    modules = TrainingModuleSerializer(many=True, required=False)
    outcomes = LearningOutcomeSerializer(many=True, required=False)

    class Meta:
        model = Training
        fields = (
            "id",
            "slug",
            "title",
            "category",
            "short_description",
            "overview",
            "mode",
            "level",
            "duration_value",
            "duration_unit",
            "duration_weeks",
            "fee_npr",
            "seats",
            "start_date",
            "end_date",
            "registration_deadline",
            "institute_location",
            "eligibility",
            "certification",
            "skills",
            "contact_person",
            "contact_phone",
            "contact_email",
            "cover_image",
            "status",
            "review_feedback",
            "published_at",
            "sessions",
            "modules",
            "outcomes",
            "created_at",
        )
        read_only_fields = (
            "id",
            "slug",
            "duration_weeks",
            "cover_image",
            "status",
            "review_feedback",
            "published_at",
            "created_at",
        )

    @staticmethod
    def _children(data):
        return {
            key: data.pop(key, None)
            for key in ("sessions", "modules", "outcomes", "detail", "contact")
        }

    def create(self, validated_data):
        children = self._children(validated_data)
        return services.create_training(
            self.request.user.membership.institute, **children, **validated_data
        )

    def update(self, instance, validated_data):
        children = self._children(validated_data)
        return services.update_training(instance, **children, **validated_data)


class PortalTrainingListSerializer(DynamicFieldsModelSerializer):
    category_name = serializers.CharField(source="category.name", read_only=True)
    municipality = serializers.SerializerMethodField()

    class Meta:
        model = Training
        fields = (
            "id",
            "slug",
            "title",
            "status",
            "review_feedback",
            "category_name",
            "mode",
            "fee_npr",
            "start_date",
            "end_date",
            "municipality",
            "created_at",
        )

    def get_municipality(self, obj):
        return (
            obj.institute_location.location.name if obj.institute_location_id else None
        )


class CoverSerializer(DynamicFieldsSerializer):
    cover_image = serializers.ImageField(validators=[validate_image_file])

    def update(self, instance, validated_data):
        return services.set_cover(instance, validated_data["cover_image"])
