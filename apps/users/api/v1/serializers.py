from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.validators import FileExtensionValidator
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from apps.common.serializers import DynamicFieldsModelSerializer
from apps.common.validators import validate_attachment, validate_phone_number
from apps.users import services
from apps.users.constants import OTP_LENGTH, OTPPurpose

User = get_user_model()


class UserRegistrationSerializer(serializers.Serializer):
    email = serializers.EmailField(
        validators=[
            UniqueValidator(
                queryset=User.objects.all(),
                lookup="iexact",
                message="A user with that email already exists.",
            )
        ]
    )
    password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)
    phone_number = serializers.CharField(
        max_length=25,
        required=False,
        validators=[
            validate_phone_number,
            UniqueValidator(
                queryset=User.objects.all(),
                message="A user with that phone number already exists.",
            ),
        ],
    )

    def validate_password(self, value):
        validate_password(value)
        return value

    def validate(self, attrs):
        # confirm_password only guards against a typo: it is dropped here, so it never reaches the
        # service and then User.objects.create_user(**owner)
        if attrs["password"] != attrs.pop("confirm_password"):
            raise serializers.ValidationError(
                {"confirm_password": "Passwords do not match."}
            )
        return attrs


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


class NormalizedEmailSerializer(serializers.Serializer):
    """Base for the OTP serializers: every one takes an email and normalises it the same way
    (services.normalize_email), so the cache keys built from it never drift between requests.

    The serializers answer with a fixed message, never with the input (see to_representation),
    so a code can never be echoed back.
    """

    email = serializers.EmailField()
    message = None  # what the 200 response says; set by subclasses

    def validate_email(self, value):
        return services.normalize_email(value)

    def create(self, validated_data):
        raise NotImplementedError

    def to_representation(self, instance):
        return {"message": self.message}


class OTPField(serializers.CharField):
    """A six-digit code. Rejected here, before it can count as a wrong guess."""

    def __init__(self, **kwargs):
        kwargs.setdefault("min_length", OTP_LENGTH)
        kwargs.setdefault("max_length", OTP_LENGTH)
        kwargs.setdefault("write_only", True)
        super().__init__(**kwargs)


class SendOTPSerializer(NormalizedEmailSerializer):
    """Password reset: only an address that has an account gets a code."""

    message = "OTP sent to your email."

    def create(self, validated_data):
        services.send_password_reset_otp(validated_data["email"])
        return validated_data


class VerifyOTPSerializer(NormalizedEmailSerializer):
    """Checks a password-reset code without using it up."""

    otp = OTPField()
    message = "OTP verified successfully."

    def create(self, validated_data):
        services.verify_otp(
            validated_data["email"],
            validated_data["otp"],
            purpose=OTPPurpose.PASSWORD_RESET,
        )
        return validated_data


class RegistrationOTPSerializer(NormalizedEmailSerializer):
    """Step 1 of registration: email a code to the address that will be the owner's login."""

    message = "Verification code sent to your email."

    def create(self, validated_data):
        services.send_registration_otp(validated_data["email"])
        return validated_data


class RegistrationOTPVerifySerializer(NormalizedEmailSerializer):
    """Optional step 2: confirm the code before the rest of the form is submitted. The code is
    checked again, and used up, by the registration itself."""

    otp = OTPField()
    message = "Email verified."

    def create(self, validated_data):
        services.verify_registration_otp(validated_data["email"], validated_data["otp"])
        return validated_data
