from django.contrib.auth import views as auth_views
from django.urls import include, path

from ..views import authentication

urlpatterns = [
    path(
        "accounts/",
        include(
            [
                path(
                    "login/",
                    auth_views.LoginView.as_view(
                        template_name="authentication/login.html"
                    ),
                    name="login",
                ),
                path("logout/", auth_views.LogoutView.as_view(), name="logout"),
                path(
                    "set-password/",
                    include(
                        [
                            path(
                                "",
                                authentication.PasswordResetRequestView.as_view(),
                                name="password_reset_request",
                            ),
                            path(
                                "<uidb64>/<token>/",
                                authentication.PasswordResetConfirmView.as_view(),
                                name="password_reset_confirm",
                            ),
                        ]
                    ),
                ),
            ]
        ),
    )
]
