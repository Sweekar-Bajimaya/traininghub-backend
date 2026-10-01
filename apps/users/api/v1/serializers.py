from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.validators import FileExtensionValidator
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from apps.common.serializers import DynamicFieldsModelSerializer
from apps.common.validators import validate_attachment
from apps.users import services
from apps.users.constants import GRANTABLE_PERMISSIONS

User = get_user_model()


class ProfileSerializer(DynamicFieldsModelSerializer):
    """Own profile: email and role are read-only."""

    permissions = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "id",
            "full_name",
            "email",
            "phone_number",
            "gender",
            "profile_picture",
            "role",
            "permissions",
            "created_at",
            "last_login",
        )
        read_only_fields = ("id", "email", "role", "created_at", "last_login")
        extra_kwargs = {
            "profile_picture": {
                "required": False,
                "allow_null": True,
                "use_url": True,
                "validators": [
                    FileExtensionValidator(["jpg", "png"]),
                    validate_attachment,
                ],
            }
        }

    def get_permissions(self, obj):
        # codename list; relies on prefetch_related("user_permissions") in list views
        return sorted(p.codename for p in obj.user_permissions.all())


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


class PasswordChangeSerializer(serializers.Serializer):
    """This class is used for password change only."""

    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True)

    def validate_old_password(self, value):
        if not self.context["request"].user.check_password(value):
            raise serializers.ValidationError("Old password is incorrect.")
        return value

    def validate_new_password(self, value):
        user = self.context["request"].user
        if user.check_password(value):
            raise serializers.ValidationError(
                "New password must differ from the old password."
            )
        validate_password(value, user)
        return value

    def update(self, instance, validated_data):
        services.change_password(instance, validated_data["new_password"])
        return instance


class UpdateStatusSerializer(DynamicFieldsModelSerializer):
    """This class is called during update status"""

    class Meta:
        model = User
        fields = ("id", "is_active")
        read_only_fields = ("id",)

    def update(self, instance, validated_data):
        return services.set_status(
            instance, active=validated_data["is_active"], by=self.request.user
        )


class LoginSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        data["user"] = ProfileSerializer(self.user, context=self.context).data
        return data
