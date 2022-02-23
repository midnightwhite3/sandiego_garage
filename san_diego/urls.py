from django.urls import path, register_converter
from . import views
from django.contrib.auth import views as auth_views
from .converters import DateConverter

register_converter(DateConverter, 'date')

urlpatterns = [
    path('', views.home_view, name='home'),
    # path('login/', auth_views.LoginView.as_view(), name='login'),
    # path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    #------ CAR VIEWS ------#
    path('car_add/', views.CarCreateView.as_view(), name='car_add'),
    path('ajax/load-car_models/', views.load_car_models, name='ajax_load_car_models'), # AJAX
    path('cars/', views.CarListView.as_view(), name='car_library'),
    path('cars/<uuid>/edit', views.CarUpdateView.as_view(), name='car_edit'),
    path('cars/<uuid>', views.CarDetailView.as_view(), name='car_detail'),
    path('cars/<uuid>/delete', views.CarDeleteView.as_view(), name='car_delete'),
    #------ CLIENT VIEWS ------#
    path('client_add/', views.ClientCreateView.as_view(), name='client_add'),
    path('clients/', views.ClientListView.as_view(), name='client_library'),
    path('clients/<uuid>/edit', views.ClientEditView.as_view(), name='client_edit'), # <uuid:uuid> for standard uuid field
    path('clients/<uuid>', views.ClientDetailView.as_view(), name='client_detail'),
    path('clients/<uuid>/delete', views.ClientDeleteView.as_view(), name='client_delete'),
    #------ SERVICE VIEWS ------#
    path('cars/<uuid>/add_service', views.ServiceAddView.as_view(), name='service_add'),
    path('cars/<uuid>/service_history', views.ServiceHistoryView.as_view(), name='service_history'),
    path('cars/<uuid>/<date:date>/delete', views.ServiceDeleteView.as_view(), name='service_delete'),
    path('cars/<uuid>/service_history/<date:date>/edit', views.ServiceEditView.as_view(), name='service_edit'),
    #------  INVOICE  ------#
    path('cars/<uuid>/invoice/<date:date>', views.generate_invoice_pdf, name='invoice'),
]
