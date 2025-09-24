from django.urls import path, include
from .views import (
    CreateUserViewSet, 
    SetNewPassword, 
    ForgotPassword, 
    LoginView, 
    VerifyOTP, 
    ResendOTP,
    UserProfileViewSet,
    UpdateUserProfileViewSet,
    UpdateServiceProviderProfileViewSet,
    UpdateIndividualProfileViewSet,
    CreateIndividualViewSet,
    CreateServiceProvidersViewSet,
    GetIndividualProfileViewSet,
    GetServiceProviderProfileViewSet,
    RetrieveIndividualProfileViewSet,
    RetrieveServiceProviderProfileViewSet,
    RetrieveUserProfileViewSet,
    CustomTokenRefreshView,
    UserMetricsView,
    UserRoleMetricsView,
)

individual_profile_urlpatterns = [
    path("create-individual-profile", CreateIndividualViewSet.as_view()),
    path("get-individual-profile", GetIndividualProfileViewSet.as_view(), name="get_individual_profile"),
    path("update-individual-profile", UpdateIndividualProfileViewSet.as_view(), name="update_individual_profile"),
    path("retrieve-individual-profile/<str:pk>", RetrieveIndividualProfileViewSet.as_view(), name="retrieve_individual_profile"),
]

service_provider_profile_urlpatterns = [
    path("get-service-provider-profile", GetServiceProviderProfileViewSet.as_view(), name="get_service_provider_profile"),
    path("create-service-provider-profile", CreateServiceProvidersViewSet.as_view()),
    path("update-service-provider-profile", UpdateServiceProviderProfileViewSet.as_view(), name="update_service_provider_profile"),
    path("retrieve-service-provider-profile/<str:pk>", RetrieveServiceProviderProfileViewSet.as_view(), name="retrieve_service_provider_profile"),
]
account_urlpatterns = [
    path("refresh-token", CustomTokenRefreshView.as_view(), name="token_refresh"),
    path("login", LoginView.as_view(), name="login"),
    path('student-sign-up', CreateUserViewSet.as_view(), name='Student_sign_up'),
    path("forgot-password", ForgotPassword.as_view(), name="forgot_password"),
    path("set-new-password", SetNewPassword.as_view(), name="set_new_password"),
    path("verify-user-otp", VerifyOTP.as_view()),
    path("resend-otp", ResendOTP.as_view()),
    # user profile
    path("get-user-profile", UserProfileViewSet.as_view(), name="get_user_profile"),
    path("update-bio", UpdateUserProfileViewSet.as_view(), name="update_profile"),
    path("get-user-profile/<str:pk>", RetrieveUserProfileViewSet.as_view(), name="retrieve_user_profile"),
]
admin_urlpatterns = [
    path("get-all-users", UserMetricsView.as_view(), name="get_all_users"),
    path("get-user-role-metrics", UserRoleMetricsView.as_view(), name="get_user_role_metrics"),
]
urlpatterns = [
    path("", include(account_urlpatterns)),
    path("admin/", include(admin_urlpatterns)),
    path("individual-profiles/", include(individual_profile_urlpatterns)),
    path("service-provider-profiles/", include(service_provider_profile_urlpatterns)),
]
