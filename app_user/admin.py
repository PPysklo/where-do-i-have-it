from django.contrib import admin
from app_user.models import CustomUser

# Register your models here.


@admin.register(CustomUser)
class HistoryAdmin(admin.ModelAdmin):
    list_display = ("username", 'first_name', "email", "id")
