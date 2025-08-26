from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
import jwt
from .custom_auth_backend import CustomRefreshToken as RefreshToken
from django.template.loader import get_template
from utils.helpers import send_email_in_thread, custom_response
from rest_framework.generics import (
    GenericAPIView,
    CreateAPIView,
    UpdateAPIView,
    RetrieveAPIView
)
from django.utils.timezone import now
import datetime
from rest_framework_simplejwt.views import TokenRefreshView
from drf_spectacular.utils import extend_schema
from django.conf import settings
from .models import CustomUser, Individual, ServiceProvider, OneTimePassword
from .serializers import (
    CustomUserSerializer, 
    UserLoginSerializer, 
    SetNewPasswordSerializer, 
    ResendEmailActivationSerializer, 
    OTPVerificationSerializer,
    UpdateUserProfileSerializer,
    IndividualSerializer,
    ServiceProvidersSerializer,
)
from django.contrib.auth import get_user_model
from django.contrib import auth
import threading
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import exceptions
from rest_framework_simplejwt.views import TokenRefreshView

User = get_user_model()

class CreateUserViewSet(CreateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = [AllowAny]
    @extend_schema(tags=["Students Auth"], operation_id="Student sign up")

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        user_data = User.objects.get(id=user.id)

        response_data = {
            "status": "success",
            "message": "User created successfully",
            "data": serializer.data,
        }

        try:
            otp_code = OneTimePassword.objects.get(user_id=user_data.id).otp

            email_data = get_template("emails/email_verification.html").render({
                "heading": "",
                "content": f"Thank you for signing up! Here's your OTP code: {otp_code}",
                "email": user.email,
            })

            subject = "One time PWD"
            thread = threading.Thread(target=send_email_in_thread, args=(subject, email_data, user.email))
            thread.start()

        except ObjectDoesNotExist:
            raise exceptions.ValidationError({"error": ["User with this email not found"]})
        except Exception as e:
            return Response({
                "status": "failed",
                "code": status.HTTP_400_BAD_REQUEST,
                "message": str(e),
            }, status=status.HTTP_400_BAD_REQUEST)

        return Response(response_data, status=status.HTTP_201_CREATED)

class LoginView(GenericAPIView):
    serializer_class = UserLoginSerializer
    permission_classes = [AllowAny]
    @extend_schema(tags=["Students Auth"], operation_id="Student login")

    def post(self, request):
        obj = request.data
        serializer = self.serializer_class(data=obj)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        user_data = serializer.data

        user = auth.authenticate(
            email=user_data["email"], password=user_data["password"]
        )

        if user:
            user.save()

        if not user:
            data = {"type": "invalid", "message": "Invalid login credentials"}
            raise exceptions.AuthenticationFailed(data)

        refresh = RefreshToken.for_user(user)
        
        refresh['user_role'] = user.user_role
        
        access = refresh.access_token
        expiration_time = datetime.datetime.fromtimestamp(access['exp'], tz=datetime.timezone.utc)
        access_exp = (expiration_time - datetime.datetime.now(tz=datetime.timezone.utc)).seconds
        data = user.profile()
        data.update({"access": str(access), "refresh": str(refresh), "expires_in_secs": str(access_exp)})

        return Response(data, status.HTTP_200_OK)

@extend_schema(
    tags=["Students Auth"],
    operation_id="Refresh access token"
)
class CustomTokenRefreshView(TokenRefreshView):
    """Students can refresh their access token using refresh token"""
    pass

class ForgotPassword(GenericAPIView):
    serializer_class = ResendEmailActivationSerializer
    @extend_schema(tags=["Password validators"], operation_id="Forgot password")

    def post(self, request):
        obj = request.data
        serializer = self.serializer_class(data=obj)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        user_data = serializer.data
        email = user_data["email"]
        user = User.objects.get(email=email)
        token = RefreshToken.for_user(user).access_token
        absurl = f"{settings.CLIENT_SITE_URL}/?token={str(token)}"

        email_data = get_template("emails/email_verification.html").render({
            "heading": "Password reset email",
            "content": "We’ve have received a request to reset the password to your Talk account. You can reset your password by clicking the button below ",
            "link": absurl,
            "action_text": "Reset Password",
            "email": user_data['email']
        })

        subject ='Talk: Password Reset Link'

        thread = threading.Thread(
            target=send_email_in_thread,
            args=(subject, email_data, user_data['email'])
        )
        thread.start()

        user_data["message"] = "password reset link sent successfully"
        return Response(user_data, status.HTTP_201_CREATED)

class SetNewPassword(GenericAPIView):
    serializer_class = SetNewPasswordSerializer
    @extend_schema(tags=["Password validators"], operation_id="Set new password")


    def post(self, request):
        obj = request.data
        serializer = self.serializer_class(data=obj)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        user_data = serializer.data
        token = user_data["token"]
        password = user_data["password"]
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
            user = User.objects.get(id=payload["user_id"])
            user.set_password(password)
            user.save()
            return Response(
                {"message": "New password set successfully"}, status=status.HTTP_200_OK
            )
        except jwt.ExpiredSignatureError as identifier:
            return Response(
                {"error": "Activation Expired"}, status=status.HTTP_400_BAD_REQUEST
            )
        except jwt.exceptions.DecodeError as identifier:
            return Response(
                {"error": "Invalid token"}, status=status.HTTP_400_BAD_REQUEST
            )

class VerifyOTP(GenericAPIView):
    serializer_class = OTPVerificationSerializer
    @extend_schema(tags=["OTP Verification"], operation_id="Verify user with `OTP`")

    def post(self, request):
        obj = request.data
        serializer = self.serializer_class(data=obj)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        user_data = serializer.data
        token = user_data["otp_code"]
        try:
            otp = OneTimePassword.objects.get(otp=token)
            if otp.is_used:
                return Response(
                    {"error": "OTP already used"}, status=status.HTTP_400_BAD_REQUEST
                )
            if otp.expires_at < now():
                return Response(
                    {"error": "OTP expired"}, status=status.HTTP_400_BAD_REQUEST
                )
            user = User.objects.get(id=otp.user_id)
            user.email_verified = True
            user.save()
            otp.is_used = True
            otp.save()

            data = {"user": user.profile()}

            return Response(
                custom_response(status.HTTP_200_OK, status="success", mssg="User verified successfully", data=data),
                status=status.HTTP_200_OK,
            )
        except OneTimePassword.DoesNotExist:
            return Response(
                custom_response(status.HTTP_400_BAD_REQUEST, status="failed", mssg="Invalid OTP", data={}),
                status=status.HTTP_400_BAD_REQUEST
            )
        except User.DoesNotExist:
            return Response(
                custom_response(status.HTTP_400_BAD_REQUEST, status="failed", mssg="User not found", data={}),
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                custom_response(status.HTTP_500_INTERNAL_SERVER_ERROR, status="failed", mssg=str(e), data={}),
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class ResendOTP(GenericAPIView):
    serializer_class  = ResendEmailActivationSerializer
    @extend_schema(tags=["OTP Verification"], operation_id="Resend OTP code")

    def post(self, request):
        obj = request.data
        serializer = self.serializer_class(data=obj)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        user_data = serializer.data
        email = user_data["email"]

        try:
            user = User.objects.get(email=email)
            otp_code = OneTimePassword.objects.get(user_id=user_data.id).otp

            email_data = get_template("emails/email_verification.html").render({
                "heading": "",
                "content": f"Thank you for signing up! Here's your OTP code: {otp_code}",
                "email": user.email,
            })

            subject = "One time PWD"
            thread = threading.Thread(target=send_email_in_thread, args=(subject, email_data, user.email))
            thread.start()

            user_data["message"] = "Email activation link sent successfully"
            return Response(user_data, status.HTTP_201_CREATED)
        except ObjectDoesNotExist:
            raise exceptions.ValidationError(
                {"error": ["User with this email not found"]}
            )
        except Exception as e:
            user_data["message"] = f"{e}"
            return Response(user_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class UserProfileViewSet(RetrieveAPIView):
    queryset = CustomUser.objects.all()
    permission_classes = [IsAuthenticated]

    @extend_schema(tags=["Profile Updates"], operation_id="View user profile")
    def get(self, request, *args, **kwargs):
        user = self.request.user
        return Response({
            "status": "success",
            "code": status.HTTP_200_OK,
            "message": "User profile retrieved successfully",
            "data": user.profile(),
        }, status=status.HTTP_200_OK)

class UpdateUserProfileViewSet(UpdateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = UpdateUserProfileSerializer
    permission_classes = [IsAuthenticated]
    http_method_names = ["patch"]
    @extend_schema(tags=["Profile Updates"], operation_id="Update user profile")
    
    # def get_object(self):
    #     return self.request.user
    
    def patch(self, request, *args, **kwargs):
        user = self.request.user
        serializer = self.get_serializer(user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({
            "status": "success",
            "code": status.HTTP_200_OK,
            "message": "User profile updated successfully",
            "data": serializer.data,
        }, status=status.HTTP_200_OK)

class CreateIndividualViewSet(CreateAPIView):
    serializer_class = IndividualSerializer
    queryset = Individual.objects.all()
    permission_classes = [IsAuthenticated]
    http_method_names = ["post"]
    @extend_schema(tags=["Profile Updates"], operation_id="Create individual profile")

    def post(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response({
                "status": "success",
                "code": status.HTTP_201_CREATED,
                "message": "Individual profile created successfully",
                "data": serializer.data,
            }, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({
                "status": "failed",
                "code": status.HTTP_400_BAD_REQUEST,
                "message": str(e),
            }, status=status.HTTP_400_BAD_REQUEST)

class CreateServiceProvidersViewSet(CreateAPIView):
    serializer_class = ServiceProvidersSerializer
    queryset = ServiceProvider.objects.all()
    permission_classes = [IsAuthenticated]
    http_method_names = ["post"]
    @extend_schema(tags=["Profile Updates"], operation_id="Create Service Provider's Profile")

    def post(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response({
                "status": "success",
                "code": status.HTTP_201_CREATED,
                "message": "Profile created!",
                "data": serializer.data
            }, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({
                "status": "failed",
                "code": status.HTTP_400_BAD_REQUEST,
                "message": str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

class UpdateIndividualProfileViewSet(UpdateAPIView):
    serializer_class = IndividualSerializer
    queryset = Individual.objects.all()
    permission_classes = [IsAuthenticated]
    http_method_names = ["patch"]
    @extend_schema(tags=["Profile Updates"], operation_id="Update individual profile")
    
    def patch(self, request, *args, **kwargs):
        user = Individual.objects.get(user=self.request.user)
        serializer = self.get_serializer(user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({
            "status": "success",
            "code": status.HTTP_200_OK,
            "message": "Individual profile updated successfully",
            "data": serializer.data,
        }, status=status.HTTP_200_OK)

class UpdateServiceProviderProfileViewSet(UpdateAPIView):
    serializer_class = ServiceProvidersSerializer
    queryset = ServiceProvider.objects.all()
    permission_classes = [IsAuthenticated]
    http_method_names = ["patch"]
    @extend_schema(tags=["Profile Updates"], operation_id="Update Service provider's profile")
    
    def patch(self, request, *args, **kwargs):
        user = ServiceProvider.objects.get(user=self.request.user)
        serializer = self.get_serializer(user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({
            "status": "success",
            "code": status.HTTP_200_OK,
            "message": "Service provider profile updated successfully",
            "data": serializer.data,
        }, status=status.HTTP_200_OK)

class RetrieveServiceProviderProfileViewSet(GenericAPIView):
    queryset = CustomUser.objects.all()
    permission_classes = [IsAuthenticated]
    http_method_names = ["get"]
    lookup_field = "id"

    @extend_schema(tags=["Profile Updates"], operation_id="View Service provider's profile")

    def get(self, request, id=None):
        queryset = self.get_queryset()
        try:
            instance = queryset.get(id=id).profile()
            return Response({
                "status": "success",
                "code": status.HTTP_200_OK,
                "message": "Service provider profile retrieved successfully",
                "data": instance
            }, status=status.HTTP_200_OK)
        except ObjectDoesNotExist as e:
            print("Error occurred:", e)
            return Response({
                "status": "failed",
                "code": status.HTTP_404_NOT_FOUND,
                "message": str(e)
            }, status=status.HTTP_404_NOT_FOUND)
