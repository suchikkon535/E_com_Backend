from django.urls import path
from . import views

urlpatterns = [
    path("create/", views.create_item, name="create_item"),
    path("list/", views.get_items, name="get_items"),
    path("list-single-image/", views.get_items_single_image, name="get_items_single_image"),
    path("delete/<str:item_id>/", views.delete_item, name="delete_item"), 
    path("update/<str:item_id>/", views.update_item, name="update_item"),
    path("items/<str:item_id>/", views.get_item_by_id, name="get_item_by_id"),
]
