from django.urls import path
from . import views

app_name = 'catalogo'

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('propiedades/', views.PropiedadListView.as_view(), name='lista'),
    path('propiedades/nueva/', views.PropiedadCreateView.as_view(), name='crear'),
    path('propiedades/administrar/', views.BuscarPropiedadView.as_view(), name='buscar'),
    path('propiedades/<int:pk>/', views.PropiedadDetailView.as_view(), name='detalle'),
    path('propiedades/<int:pk>/editar/', views.PropiedadUpdateView.as_view(), name='editar'),
    path('propiedades/<int:pk>/baja/', views.PropiedadDarDeBajaView.as_view(), name='baja'),
]