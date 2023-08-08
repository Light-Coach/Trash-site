from trash_app.models import *
from map_app.models import *


class ContextDataMenu:
    header_menu = [
        {"title": "О сайте", "url_name": "about_site"},
        {"title": "Обратная связь", "url_name": "contact"},
    ]

    sidebar_menu = [
        {"title": "Организации", "url_name": "show_organizations"},
        {"title": "Статьи", "url_name": "show_articles"},
        {"title": "Вопросы", "url_name": "show_questions"},
    ]

    materials = TrashMaterial.objects.all()

    organizations = Organizations.objects.all()

    reception_points = Coordinates.objects.all()

    latitudes = [point.latitude_coordinate for point in reception_points]
    longitudes = [point.longitude_coordinate for point in reception_points]
    coordinates = list(zip(latitudes, longitudes))

    organization_data_names = Coordinates.objects.values(
        "coordinates__organization_name"
    )
    organization_names = [
        name
        for dictionary_names in organization_data_names
        for name in dictionary_names.values()
    ]
    organization_data_phone_numbers = Coordinates.objects.values(
        "coordinates__telephone_number"
    )
    organization_phone_numbers = [
        phone_numbers
        for dictionary_phone_numbers in organization_data_phone_numbers
        for phone_numbers in dictionary_phone_numbers.values()
    ]
    organizations_data = list(zip(organization_names, organization_phone_numbers))
    data = [list(data) for data in organizations_data]
