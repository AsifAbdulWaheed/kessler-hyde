from django.urls import path
from . import views

app_name = "catalog"

urlpatterns = [
    path("product/<slug:slug>/", views.product_detail, name="product_detail"),
    path("<slug:slug>/", views.category_page, name="category_page"),
]