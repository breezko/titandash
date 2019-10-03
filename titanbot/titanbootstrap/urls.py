from django.urls import path
from . import views


urlpatterns = [
    # BOOTSTRAP.
    path("", views.bootstrap, name="bootstrap"),

    # AJAX Bootstrapper.
    path("ajax/check_update", views.check_update, name="check_update"),
    path("ajax/perform_update", views.perform_update, name="perform_update"),
    path("ajax/perform_requirements", views.perform_requirements, name="perform_requirements"),
    path("ajax/perform_node_packages", views.perform_node_packages, name="perform_node_packages"),
    path("ajax/perform_migration", views.perform_migration, name="perform_migration"),
    path("ajax/perform_cache", views.perform_cache, name="perform_cache"),
    path("ajax/perform_static", views.perform_static, name="perform_static"),
    path("ajax/perform_dependency", views.perform_dependency, name="perform_dependency")
]
