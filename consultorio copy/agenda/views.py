from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import Paciente, Medico, Cita
#  IMPORTAR EL DECORADOR DE SEGURIDAD
from django.contrib.auth.decorators import login_required


@login_required
def index(request):
    "Consultamos a la base de datos (SELECT * FROM agenda_cita)"
    lista_citas = Cita.objects.all()
    
    
    lista_pacientes = Paciente.objects.all()
    lista_medicos = Medico.objects.all()

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
            # Obtener los datos del formulario 
            paciente_id = request.POST.get('cita-paciente-id')
            medico_id = request.POST.get('cita-medico-id')
            fecha = request.POST.get('cita-fecha')
            motivo = request.POST.get('cita-motivo')

            #  Buscar las instancias de Paciente y Medico en la BD
            # (Django necesita los objetos reales, no solo los números de ID)
            paciente_obj = Paciente.objects.get(id=paciente_id)
            medico_obj = Medico.objects.get(id=medico_id)

            # Crear la Cita
            Cita.objects.create(
                paciente=paciente_obj,
                medico=medico_obj,
                fecha_hora=fecha,
                motivo=motivo
            )
            print("--> ¡Cita agendada EXITOSAMENTE!")
            return redirect('inicio')

        except Paciente.DoesNotExist:
            return HttpResponse("Error: El ID del paciente no existe.")
        except Medico.DoesNotExist:
            return HttpResponse("Error: El ID del médico no existe.")
        except Exception as e:
            return HttpResponse(f"Error al agendar cita: {e}")

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
        # Busca la cita por su ID y la borra
        cita = Cita.objects.get(id=id)
        cita.delete()
    except:
        pass # Si no existe, no hace nada
    return redirect('inicio')