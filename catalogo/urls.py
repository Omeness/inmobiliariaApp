from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView
from . import views, api_views

app_name = 'catalogo'

urlpatterns = [
    # Auth Web
    path('login/', LoginView.as_view(template_name='catalogo/login.html', redirect_authenticated_user=True), name='login'),
    path('logout/', LogoutView.as_view(next_page='catalogo:home'), name='logout'),
    
    # Auth API REST
    path('api/auth/login/', api_views.LoginAPIView.as_view(), name='api_login'),
    path('api/auth/logout/', api_views.LogoutAPIView.as_view(), name='api_logout'),

    # App
    path('', views.HomeView.as_view(), name='home'),
    path('propiedades/', views.PropiedadListView.as_view(), name='lista'),
    path('propiedades/nueva/', views.PropiedadCreateView.as_view(), name='crear'),
    path('propiedades/administrar/', views.BuscarPropiedadView.as_view(), name='buscar'),
    path('propiedades/<int:pk>/', views.PropiedadDetailView.as_view(), name='detalle'),
    path('propiedades/<int:pk>/editar/', views.PropiedadUpdateView.as_view(), name='editar'),
    path('propiedades/<int:pk>/baja/', views.PropiedadDarDeBajaView.as_view(), name='baja'),
]
