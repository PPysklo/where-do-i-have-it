from django.contrib import admin
from .models import *

admin.site.register(Thing)
admin.site.register(Location)
admin.site.register(Image)
admin.site.register(ImageTag)

# admin.site.register(History)


@admin.register(History)
class HistoryAdmin(admin.ModelAdmin):
    list_display = ("thing", "location", "validFrom", "validTo", "owner", "id")
    list_filter = ("validFrom", "validTo")

    def owner(self, obj=None):

        if obj is not None:
            return obj.thing.owner
        return ""
