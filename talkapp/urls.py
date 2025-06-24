from django.urls import path
from .views import (
    CreateUserViewSet, 
    SetNewPassword, 
    ForgotPassword, 
    LoginView, 
    VerifyOTP, 
    ResendOTP,
    UpdateUserProfileViewSet,
    UpdateServiceProviderProfileViewSet,
    UpdateIndividualProfileViewSet,
    CreateIndividualViewSet,
    CreateServiceProvidersViewSet
)


urlpatterns = [
    path("login", LoginView.as_view(), name="login"),
    path('student-sign-up', CreateUserViewSet.as_view(), name='Student_sign_up'),
    path("forgot-password", ForgotPassword.as_view(), name="forgot_password"),
    path("set-new-password", SetNewPassword.as_view(), name="set_new_password"),
    path("verify-user-otp", VerifyOTP.as_view()),
    path("resend-otp", ResendOTP.as_view()),
    # user profile
    path("update-bio", UpdateUserProfileViewSet.as_view(), name="update_profile"),
    path("create-individual-profile", CreateIndividualViewSet.as_view()),
    path("create-service-provider-profile", CreateServiceProvidersViewSet.as_view()),
    path("update-service-provider-profile", UpdateServiceProviderProfileViewSet.as_view(), name="update_service_provider_profile"),
    path("update-individual-profile", UpdateIndividualProfileViewSet.as_view(), name="update_individual_profile")
]
