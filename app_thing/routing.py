from django.urls import re_path
from .consumers import ImageRecognitionConsumer, AddImageConsumer, ScannerConsumer

websocket_urlpatterns =[
    re_path('ws/image_reco/', ImageRecognitionConsumer.as_asgi()),
    re_path('ws/add_image/', AddImageConsumer.as_asgi()),
    re_path('ws/scanner/', ScannerConsumer.as_asgi()),

]