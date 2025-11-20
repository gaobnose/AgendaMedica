from django.urls import path
from .views import index, registrar_paciente, agendar_cita, registrar_medico
from .views import eliminar_cita

urlpatterns = [
    path('', index, name='inicio'),
    path('registrar/paciente/', registrar_paciente, name='registrar_paciente'),
    
    # NUEVA RUTA PARA CITAS:
    path('agendar/cita/', agendar_cita, name='agendar_cita'),
    # NUEVA RUTA:
    path('registrar/medico/', registrar_medico, name='registrar_medico'),
    path('eliminar/cita/<int:id>/', eliminar_cita, name='eliminar_cita'),
]