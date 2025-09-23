from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from .models import CustomUser, Individual, ServiceProvider
from django.contrib.auth import get_user_model

User = get_user_model()

class CustomUserSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        required=True,
        allow_blank=False,)
    password = serializers.CharField(
        write_only=True, required=True, validators=[validate_password]
    )
    gender = serializers.ChoiceField(choices=["male", "female"], required=True)
    level = serializers.ChoiceField(
        choices=["100", "200", "300", "400", "500", "graduate"],
        required=True,
    )
    class Meta:
        model = CustomUser
        fields = [
            "id",
            "email",
            "first_name",
            "last_name",
            "gender",
            "password",
            "university",
            "level",
            "state",
            "policy"
        ]
        read_only_fields = ["id"]
    
    def create(self, validated_data):
        user = CustomUser.objects.create(**validated_data)
        user.set_password(validated_data["password"])
        user.save()
        return user


class CustomUserAnalyticsSerializer(serializers.ModelSerializer):
    user_role = serializers.ChoiceField(choices=["service providers", "individuals"], read_only=True)

    class Meta:
        model = CustomUser
        fields = [
            "id",
            "talk_id",
            "email",
            "first_name",
            "last_name",
            "user_role",
            "gender",
            "university",
            "level",
            "state",
            "policy",
            "email_verified",
            "created",
        ]
        read_only_fields = ["id", "email_verified"]
    
class UserLoginSerializer(serializers.Serializer):
    email = serializers.CharField(required=True)
    password = serializers.CharField(required=True)

    class Meta:
        model = User
        fields = ("email", "password")

    def validate(self, data):
        data["email"] = data["email"].lower()
        return data

    def create(self, validated_data):
        return validated_data

class UpdateUserRoleSerializer(serializers.ModelSerializer):
    user_role = serializers.ChoiceField(choices=["service providers", "individuals"], required=True)
    class Meta:
        model = CustomUser
        fields = ["user_role"]

    def update(self, instance, validated_data):
        if validated_data:
            instance.user_role = validated_data.get("user_role", instance.user_role)
            instance.save()
        return instance
class RefreshTokenSerializer(serializers.Serializer):
    refresh = serializers.CharField(required=True)

    class Meta:
        fields = ["refresh"]

    def validate(self, data):
        return data

    def create(self, validated_data):
        return validated_data

class IndividualSerializer(serializers.ModelSerializer):
    class Meta:
        model = Individual
        fields = [
            "phone_number",
            "date_of_birth",
            "bio",
            "interests",
            "photo",
        ]
        read_only_fields = ["id", "created_at", "updated_at", "user"]

    def create(self, validated_data):
        individual = Individual.objects.create(user=self.context.get('request').user, **validated_data)
        individual.save()
        return individual
    
    def update(self, instance, validated_data):
        if validated_data:
            instance.phone_number = validated_data.get("phone_number", instance.phone_number)
            instance.date_of_birth = validated_data.get("date_of_birth", instance.date_of_birth)
            instance.save()
        return instance

class ServiceProvidersSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceProvider
        fields = [
            "business_name",
            "business_email",
            "business_tel",
            "business_type",
            "address",
            "description",
            "logo",
            "bio",
            "created",
            "updated",
            "address_verified",
        ]
        read_only_fields = ["id", "created", "updated", "user", "address_verified"]

    def create(self, validated_data):
        try:
            service_provider = ServiceProvider.objects.create(user=self.context.get('request').user, **validated_data)
            service_provider.save()
            return service_provider
        except Exception as e:
            raise serializers.ValidationError({"error": str(e)})
    
    def update(self, instance, validated_data):
        if validated_data:
            instance.business_name = validated_data.get("business_name", instance.business_name)
            instance.business_email = validated_data.get("business_email", instance.business_email)
            instance.business_tel = validated_data.get("business_tel", instance.business_tel)
            instance.business_type = validated_data.get("business_type", instance.business_type)
            instance.address = validated_data.get("address", instance.address)
            instance.description = validated_data.get("description", instance.description)
            instance.logo = validated_data.get("logo", instance.logo)
            instance.save()
        return instance

class UpdateUserProfileSerializer(serializers.ModelSerializer):
    level = serializers.ChoiceField(
        choices=["100", "200", "300", "400", "500", "graduate"],
        required=True,
    )
    class Meta:
        model = CustomUser
        fields =[
            "email",
            "first_name",
            "last_name",
            "level",
            # "registration_number"
        ]

        def update(self, instance, validated_data):
            if validated_data:
                instance.email = validated_data.get("email", instance.email)
                instance.first_name = validated_data.get("first_name", instance.first_name)
                instance.last_name = validated_data.get("last_name", instance.last_name)
                instance.level = validated_data.get("level", instance.level)
                # instance.registration_number = validated_data.get("registration_number", instance.registration_number)
                instance.save()
            return instance

class SetNewPasswordSerializer(serializers.Serializer):
    token = serializers.CharField(required=True)
    password = serializers.CharField(required=True, validators=[validate_password])

    class Meta:
        fields = ["token", "password"]

    def create(self, validated_data):
        return validated_data

class OTPVerificationSerializer(serializers.Serializer):
    otp_code = serializers.CharField(required=True)

    class Meta:
        fields = ["otp_code"]

    def create(self, validated_data):
        return validated_data

class ResendEmailActivationSerializer(serializers.Serializer):
    """
    This and normalizes an email field, checking if a user with that email exists in
    the database.

    :param data: The `data` parameter in the `validate` method refers to the input data that is being
    validated. It is a dictionary containing the field values submitted by the user. In this case, it
    contains the email address that is being validated and processed
    :return: The `create` method is returning the `validated_data` dictionary.
    """

    email = serializers.EmailField(max_length=255, required=True)

    class Meta:
        fields = ["email"]

    def validate(self, data):
        data["email"] = data["email"].lower()
        if not User.objects.filter(email=data["email"]):
            raise serializers.ValidationError("User with email not found")
        return data

    def create(self, validated_data):
        return validated_data
