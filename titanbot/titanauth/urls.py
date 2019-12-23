from django.urls import path
from . import views


urlpatterns = [
    # AUTHENTICATE.
    path("authenticate", views.authenticate, name="authenticate"),
    path("authenticate/logout", views.logout, name="authenticate_logout"),
    # CREDENTIALS CHECK.
    path("ajax/credentials", views.credentials, name="credentials")
]

