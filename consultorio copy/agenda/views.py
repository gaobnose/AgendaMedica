from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import Paciente, Medico, Cita
from django.contrib.auth.decorators import login_required


@login_required
def index(request):
    "Consultamos a la base de datos (SELECT * FROM agenda_cita)"
    # Es Administrador (Staff) -> Ve "todo"
    if request.user.is_staff:
        lista_citas = Cita.objects.all().order_by('fecha_hora')
    
    # Es Paciente -> Ve SOLO SUYO
    else:
        try:
            # Buscamos la ficha de paciente de este usuario logueado
            paciente_actual = request.user.paciente 
            lista_citas = Cita.objects.filter(paciente=paciente_actual).order_by('fecha_hora')
        except:
            lista_citas = [] # Si no tiene perfil de paciente, no ve citas

    lista_pacientes = Paciente.objects.all().order_by('nombre')
    lista_medicos = Medico.objects.all().order_by('nombre')

    contexto = {
        'citas': lista_citas,
        'pacientes': lista_pacientes,
        'medicos': lista_medicos
    }

    return render(request, 'agenda.html', contexto)



# Vista de Registro de Paciente
def registrar_paciente(request):
    if request.method == 'POST':
        try:
            nombre = request.POST.get('paciente-nombre')
            fecha_nac = request.POST.get('paciente-fecha-nac')
            telefono = request.POST.get('paciente-telefono')
            
            Paciente.objects.create(
                nombre=nombre,
                fecha_nacimiento=fecha_nac,
                telefono=telefono
            )
            return redirect('inicio')
        except Exception as e:
            return HttpResponse(f"Error: {e}")
            
    return redirect('inicio')



def agendar_cita(request):
    if request.method == 'POST':
        try:
            medico_id = request.POST.get('cita-medico-id')
            fecha = request.POST.get('cita-fecha')
            motivo = request.POST.get('cita-motivo')
            medico_obj = Medico.objects.get(id=medico_id)

            # LÓGICA INTELIGENTE:
            if request.user.is_staff:
                # Si es Admin, usa el ID que escribió en el formulario
                paciente_id = request.POST.get('cita-paciente-id')
                paciente_obj = Paciente.objects.get(id=paciente_id)
            else:
                # Si es Paciente, usa SU PROPIO perfil
                paciente_obj = request.user.paciente

            Cita.objects.create(
                paciente=paciente_obj,
                medico=medico_obj,
                fecha_hora=fecha,
                motivo=motivo
            )
        except Exception as e:
            return HttpResponse(f"Error: {e}")
            
    return redirect('inicio')

    return redirect('inicio')

def registrar_medico(request):
    if request.method == 'POST':
        try:
            nombre = request.POST.get('medico-nombre')
            especialidad = request.POST.get('medico-especialidad')
            
            Medico.objects.create(
                nombre=nombre,
                especialidad=especialidad
            )
            return redirect('inicio')
        except Exception as e:
            return HttpResponse(f"Error al registrar médico: {e}")
            
    return redirect('inicio')



def eliminar_cita(request, id):
    try:
        # Busca la cita con ese ID exacto
        cita = Cita.objects.get(id=id)
        # La borra de la base de datos
        cita.delete()
    except Cita.DoesNotExist:
        pass # Si no existe, no hace nada (evita errores)
    
    # Vuelve a cargar la página principal
    return redirect('inicio')



def editar_cita(request, id):
    cita = Cita.objects.get(id=id)
    
    # Si el usuario guardó el formulario
    if request.method == 'POST':
        cita.paciente_id = request.POST.get('cita-paciente-id')
        cita.medico_id = request.POST.get('cita-medico-id')
        cita.fecha_hora = request.POST.get('cita-fecha')
        cita.motivo = request.POST.get('cita-motivo')
        cita.save() # Guardamos los cambios
        return redirect('inicio')
    
    # Si el usuario solo entró a ver el formulario
    medicos = Medico.objects.all()
    pacientes = Paciente.objects.all()
    
    # Formatear fecha para que el input HTML la entienda (YYYY-MM-DDTHH:MM)
    fecha_formato = cita.fecha_hora.strftime('%Y-%m-%dT%H:%M')
    
    contexto = {
        'cita': cita,
        'medicos': medicos,
        'pacientes': pacientes,
        'fecha_formateada': fecha_formato
    }
    return render(request, 'editar_cita.html', contexto)