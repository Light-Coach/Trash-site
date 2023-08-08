from django.urls import path

from .views import *

urlpatterns = [
    path(
        "materials_on_the_map/",
        create_map_for_all_kind_of_materials,
        name="materials_on_the_map",
    ),
    path(
        "material_on_the_map/<int:pk>/",
        create_map_for_different_kind_of_materials,
        name="material_on_the_map",
    ),
    path(
        "organization_on_the_map/<int:pk>/",
        create_map_for_different_organizations,
        name="organization_on_the_map",
    ),
    path("search_field_result", search_field, name="search_field_result"),
]
