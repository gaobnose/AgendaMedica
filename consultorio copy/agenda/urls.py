from django.urls import path
from . import views
from .views import index, registrar_paciente, registrar_medico, agendar_cita, eliminar_cita, editar_cita, generar_usuarios_aleatorios

urlpatterns = [
    path('', index, name='inicio'),
    path('registrar/paciente/', registrar_paciente, name='registrar_paciente'),
    path('registrar/medico/', registrar_medico, name='registrar_medico'),
    path('agendar/cita/', agendar_cita, name='agendar_cita'),
    path('eliminar/cita/<int:id>/', eliminar_cita, name='eliminar_cita'),
    path('editar/cita/<int:id>/', editar_cita, name='editar_cita'),
    path('usuarios/generar/', generar_usuarios_aleatorios, name='generar_usuarios'),
]