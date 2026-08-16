from django.urls import path
from . import views

app_name = "returns"

urlpatterns = [
    path("", views.returns_lookup, name="returns_lookup"),
    path("submit/<int:order_item_id>/", views.submit_return, name="submit_return"),
]