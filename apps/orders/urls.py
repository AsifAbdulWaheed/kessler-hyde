from django.urls import path
from . import views

app_name = "orders"

urlpatterns = [
    path("track/", views.track_order, name="track_order"),
    path("cancel/<str:order_number>/", views.cancel_order_view, name="cancel_order"),
    path("my-orders/", views.my_orders, name="my_orders"),
]