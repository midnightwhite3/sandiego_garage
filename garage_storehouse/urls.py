from django.urls import path
from . import views

urlpatterns = [
    path('storehouse/', views.StorehouseView.as_view(), name='storehouse'),
    path('storehouse/add_part', views.StorehouseAddPartView.as_view(), name='storehouse_add_part'),
    path('storehouse/<int:id>/edit_part', views.StorehouseEditPartView.as_view(), name='storehouse_edit_part'),
    path('storehouse/<int:id>/delete_part', views.StorehouseDeletePartView.as_view(), name='storehouse_delete_part'),
    
]