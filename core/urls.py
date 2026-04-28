from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.index, name='index'),
    path('buscar/', views.run_search, name='run_search'),
    path('busqueda/<int:pk>/', views.search_detail, name='search_detail'),
    path('busqueda/<int:pk>/csv/', views.export_csv, name='export_csv'),
    path('busqueda/<int:pk>/eliminar/', views.delete_search, name='delete_search'),
]
