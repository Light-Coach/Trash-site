from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.db.models import Q
from django.contrib import messages
import requests
import polyline
import folium
from folium.plugins import MarkerCluster, MousePosition, MeasureControl

from trash_app.models import *
from trash_app.utils import ContextDataMenu
from map_app.models import *

# Create your views here.


def get_client_ip(request):
    """Функция получения ip-адреса из запроса"""

    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")

    if x_forwarded_for:
        ip = x_forwarded_for.split(",")[0]
    else:
        ip = request.META.get("REMOTE_ADDR")
    return ip


def get_info_by_ip(ip):
    try:
        response = requests.get(url=f"http://ip-api.com/json/{ip}").json()
        print(response)
        data = {"lat": response.get("lat"), "lon": response.get("lon")}
    except requests.exceptions.ConnectionError:
        print("Невозможно определить ip-адрес")

    return data


def create_map_for_different_kind_of_materials(request, pk):
    """Функция создания карты с пунктами приёма определённого вторсырья"""

    template = "maps/material_on_the_map.html"
    context = {"title": "Карта", "menu": ContextDataMenu}
    reception_point = (
        Organizations.objects.filter(material__in=TrashMaterial.objects.all())
        .filter(material__id=pk)
        .first()
    )
    print(reception_point)
    ip = get_client_ip(request)
    ip_info = get_info_by_ip(ip)
    print(ip_info)

    """Создание карты с начальной центровкой по заданным координатам"""

    if reception_point:
        if ip_info["lat"] and ip_info["lon"] is not None:
            map = folium.Map(
                location=[ip_info["lat"], ip_info["lon"]],
                zoom_start=10,
                control_scale=True,
            )
            folium.Marker(
                location=[ip_info["lat"], ip_info["lon"]],
                popup=f"Привет, {request.user.username if request.user.username else 'странник'}, прекрасное время, чтобы мусор отнести на переработку!",
                tooltip="Вы здесь",
                icon=folium.Icon(color="lightblue"),
            ).add_to(map)
            for point in reception_point.organizations_coordinates.filter(
                coordinates_id=reception_point.id
            ):
                coordinates_of_point = (
                    point.latitude_coordinate,
                    point.longitude_coordinate,
                )
                folium.Marker(
                    coordinates_of_point,
                    popup=f"{point}, {reception_point.telephone_number}",
                    icon=folium.Icon(color="green"),
                ).add_to(map)
        else:
            messages.error(request, "Не удаётся определить ваше местоположение")
            map = folium.Map(
                location=[43.303842, 77.237040], zoom_start=10, control_scale=True
            )

            for point in reception_point.organizations_coordinates.filter(
                coordinates_id=reception_point.id
            ):
                coordinates_of_point = (
                    point.latitude_coordinate,
                    point.longitude_coordinate,
                )
                folium.Marker(
                    coordinates_of_point,
                    popup=f"{point}, {reception_point.telephone_number}",
                    icon=folium.Icon(color="green"),
                ).add_to(map)
    else:
        if ip_info["lat"] and ip_info["lon"] is not None:
            messages.error(request, "Нет пунктов приёма")
            map = folium.Map(
                location=[ip_info["lat"], ip_info["lon"]],
                zoom_start=10,
                control_scale=True,
            )
            folium.Marker(
                location=[ip_info["lat"], ip_info["lon"]],
                popup=f"Привет, {request.user.username if request.user.username else 'странник'}, прекрасное время, чтобы мусор отнести на переработку!",
                tooltip="Вы здесь",
                icon=folium.Icon(color="lightblue"),
            ).add_to(map)
        else:
            messages.error(
                request,
                "Не удаётся определить ваше местоположение. Нет пунктов приёма.",
            )
            map = folium.Map(
                location=[43.303842, 77.237040], zoom_start=10, control_scale=True
            )

    formatter = "function(num) {return L.Util.formatNum(num, 5);};"
    mouse_position = MousePosition(
        position="topright",
        separator=" Long: ",
        empty_string="None",
        lng_first=False,
        num_digits=20,
        prefix="Lat:",
        lat_formatter=formatter,
        lng_formatter=formatter,
    )
    map.add_child(mouse_position)

    map.add_child(folium.LatLngPopup())

    context["map"] = map._repr_html_()
    return render(request, template, context=context)


def create_map_for_all_kind_of_materials(request):
    """Функция для создания карты с пунктами приёма всякого вторсырья"""

    template = "maps/material_on_the_map.html"
    context = {"title": "Карта", "menu": ContextDataMenu}

    ip = get_client_ip(request)
    ip_info = get_info_by_ip(ip)
    print(ip_info)

    if ContextDataMenu.reception_points:
        if ip_info["lat"] and ip_info["lon"] is not None:
            map = folium.Map(
                location=[ip_info["lat"], ip_info["lon"]],
                zoom_start=10,
                control_scale=True,
            )
            folium.Marker(
                location=[ip_info["lat"], ip_info["lon"]],
                popup=f"Привет, {request.user.username if request.user.username else 'странник'}, прекрасное время, чтобы мусор отнести на переработку!",
                tooltip="Вы здесь",
                icon=folium.Icon(color="lightblue"),
            ).add_to(map)
            MarkerCluster(
                locations=ContextDataMenu.coordinates,
                popups=[", ".join(part) for part in ContextDataMenu.data],
            ).add_to(map)
        else:
            messages.error(request, "Не удаётся определить ваше местоположение")
            map = folium.Map(
                location=[43.303842, 77.237040], zoom_start=10, control_scale=True
            )
            MarkerCluster(
                locations=ContextDataMenu.coordinates,
                popups=[", ".join(part) for part in ContextDataMenu.data],
            ).add_to(map)
    else:
        if ip_info["lat"] and ip_info["lon"] is not None:
            messages.error(request, f"Нет пунктов приёма.")
            map = folium.Map(
                location=[ip_info["lat"], ip_info["lon"]],
                zoom_start=10,
                control_scale=True,
            )
            folium.Marker(
                location=[ip_info["lat"], ip_info["lon"]],
                popup=f"Привет, {request.user.username if request.user.username else 'странник'}, прекрасное время, чтобы мусор отнести на переработку!",
                tooltip="Вы здесь",
                icon=folium.Icon(color="lightblue"),
            ).add_to(map)
        else:
            messages.error(
                request,
                "Не удаётся определить ваше местоположение. Нет пунктов приёма.",
            )
            map = folium.Map(
                location=[43.303842, 77.237040], zoom_start=10, control_scale=True
            )

    formatter = "function(num) {return L.Util.formatNum(num, 5);};"
    mouse_position = MousePosition(
        position="topright",
        separator=" Long: ",
        empty_string="None",
        lng_first=False,
        num_digits=20,
        prefix="Lat:",
        lat_formatter=formatter,
        lng_formatter=formatter,
    )
    map.add_child(mouse_position)

    map.add_child(folium.LatLngPopup())

    context["map"] = map._repr_html_()
    return render(request, template, context=context)


def create_map_for_different_organizations(request, pk):
    """Функция для создания карты для выбранной организации"""

    template = "maps/material_on_the_map.html"
    context = {"title": "Карта", "menu": ContextDataMenu}
    reception_point = Organizations.objects.filter(id=pk).first()
    print(reception_point)

    ip = get_client_ip(request)
    ip_info = get_info_by_ip(ip)
    print(ip_info)

    if reception_point:
        if ip_info["lat"] and ip_info["lon"] is not None:
            map = folium.Map(
                location=[ip_info["lat"], ip_info["lon"]],
                zoom_start=10,
                control_scale=True,
            )
            folium.Marker(
                location=[ip_info["lat"], ip_info["lon"]],
                popup=f"Привет, {request.user.username if request.user.username else 'странник'}, прекрасное время, чтобы мусор отнести на переработку!",
                tooltip="Вы здесь",
                icon=folium.Icon(color="lightblue"),
            ).add_to(map)
            for point in reception_point.organizations_coordinates.filter(
                coordinates_id=reception_point.id
            ):
                coordinates_of_point = (
                    point.latitude_coordinate,
                    point.longitude_coordinate,
                )
                folium.Marker(
                    coordinates_of_point,
                    popup=f"{point}, {reception_point.telephone_number}",
                    icon=folium.Icon(color="green"),
                ).add_to(map)
        else:
            messages.error(request, "Не удаётся определить ваше местоположение")
            map = folium.Map(
                location=[43.303842, 77.237040], zoom_start=10, control_scale=True
            )

            for point in reception_point.organizations_coordinates.filter(
                coordinates_id=reception_point.id
            ):
                coordinates_of_point = (
                    point.latitude_coordinate,
                    point.longitude_coordinate,
                )
                folium.Marker(
                    coordinates_of_point,
                    popup=f"{point}, {reception_point.telephone_number}",
                    icon=folium.Icon(color="green"),
                ).add_to(map)
    else:
        if ip_info["lat"] and ip_info["lon"] is not None:
            messages.error(request, "Нет пунктов приёма")
            map = folium.Map(
                location=[ip_info["lat"], ip_info["lon"]],
                zoom_start=10,
                control_scale=True,
            )
            folium.Marker(
                location=[ip_info["lat"], ip_info["lon"]],
                popup=f"Привет, {request.user.username if request.user.username else 'странник'}, прекрасное время, чтобы мусор отнести на переработку!",
                tooltip="Вы здесь",
                icon=folium.Icon(color="lightblue"),
            ).add_to(map)
        else:
            messages.error(
                request,
                "Не удаётся определить ваше местоположение. Нет пунктов приёма.",
            )
            map = folium.Map(
                location=[43.303842, 77.237040], zoom_start=10, control_scale=True
            )

    formatter = "function(num) {return L.Util.formatNum(num, 5);};"
    mouse_position = MousePosition(
        position="topright",
        separator=" Long: ",
        empty_string="None",
        lng_first=False,
        num_digits=20,
        prefix="Lat:",
        lat_formatter=formatter,
        lng_formatter=formatter,
    )
    map.add_child(mouse_position)

    map.add_child(folium.LatLngPopup())

    context["map"] = map._repr_html_()
    return render(request, template, context=context)


def search_field(request):
    """Функция для поиска информации по сайту"""

    context = {"menu": ContextDataMenu, "title": "Результат поиска"}

    if request.method == "POST":
        searching = request.POST["searching"]
        context["searching"] = searching
        context["searched_organizations"] = Organizations.objects.filter(
            organization_name__contains=searching
        )
        context["searched_articles"] = Article.objects.filter(
            Q(title__contains=searching) | Q(description__contains=searching)
        )
        context["searched_questions"] = Question.objects.filter(
            Q(author__username__contains=searching)
            | Q(title__contains=searching)
            | Q(content__contains=searching)
        )
        return render(request, "search/search_field_result.html", context=context)
    else:
        return render(request, "search/search_field_result.html", context=context)
