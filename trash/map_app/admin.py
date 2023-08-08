from django.contrib import admin
from map_app.models import *

# Register your models here.


class ClientsIpAddressesAdmin(admin.ModelAdmin):
    list_display = ("ip",)


class CoordinatesAdmin(admin.ModelAdmin):
    list_display = ("id", "coordinates")


admin.site.register(Coordinates, CoordinatesAdmin)
admin.site.register(ClientsIpAddresses, ClientsIpAddressesAdmin)
