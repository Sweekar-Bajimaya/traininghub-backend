from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework.validators import UniqueValidator
from rest_framework import serializers
from apps.users.api.v1.serializers import ProfileSerializer
from apps.users.constants import GRANTABLE_PERMISSIONS
from apps.users import services

User = get_user_model()


class AdminSerializer(ProfileSerializer):
    """Admin serializer class for admin related work"""

    password = serializers.CharField(write_only=True, required=False)
    permissions = serializers.ListField(
        child=serializers.ChoiceField(choices=GRANTABLE_PERMISSIONS), required=False
    )

    class Meta(ProfileSerializer.Meta):
        fields = ProfileSerializer.Meta.fields + ("password", "is_active")
        read_only_fields = ("id", "role", "created_at", "last_login", "is_active")
        create_only_fields = ("email", "password")  # read-only after password creation
        extra_kwargs = {
            **ProfileSerializer.Meta.extra_kwargs,
            "email": {
                "validators": [
                    UniqueValidator(
                        queryset=User.objects.all(),
                        lookup="iexact",
                        message="A user with that email already exists.",
                    )
                ]
            },
        }

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["permissions"] = self.get_permissions(instance)
        return data

    def validate_password(self, value):
        validate_password(value)
        return value

    def validate(self, attrs):
        if self.instance is None and "password" not in attrs:
            raise serializers.ValidationError({"password": "This field is required."})
        if self.instance is not None and "password" in attrs:
            raise serializers.ValidationError(
                {"password": "The password cannot be changed here."}
            )
        return attrs

    def create(self, validated_data):
        return services.create_admin(**validated_data)

    def update(self, instance, validated_data):
        return services.update_admin(instance, **validated_data)
