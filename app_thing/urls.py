from django.urls import path

from . import views

app_name = "app_thing"

urlpatterns = [
    path("", views.all_user_things, name="all_things"),
    path("things_map/", views.things_map, name="things_map"),

    path("locations/", views.location_management, name="locations"),
    path('delete_location/<str:pk>/', views.LocationDeleteView.as_view(), name='delete_location'),

    path("add_thing/", views.add_thing, name="add_thing"),
    path("update_thing/<str:pk>/", views.update_thing, name="update_thing"),
    path("thing/<str:pk>/", views.ThingDetailView.as_view(), name="thing_detail"),
    path("delete_thing/<str:pk>/", views.ThingDeleteView.as_view(), name="delete_thing"),

    path("image_recognition/<str:pk>/", views.image_recognition, name="image_recognition"),
    path("add_image/<str:pk>/", views.add_image, name="add_image"),
    path("delete_image/<str:pk>/", views.ImageDeleteView.as_view(), name="delete_image"),

    path("scanner/", views.scanner, name="scanner"),

    path("about/", views.about, name="about"),

]
