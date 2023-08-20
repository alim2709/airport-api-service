from django.contrib import admin

from service.models import (
    Order,
    Ticket,
    Flight,
    Airplane,
    AirCompany,
    AirplaneType,
    Route,
    Airport,
    Crew,
)


class TicketInline(admin.TabularInline):
    model = Ticket
    extra = 1


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    inlines = (TicketInline,)


admin.site.register(Flight)
admin.site.register(Airplane)
admin.site.register(AirCompany)
admin.site.register(AirplaneType)
admin.site.register(Route)
admin.site.register(Airport)
admin.site.register(Crew)
