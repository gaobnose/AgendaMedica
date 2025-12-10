from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from datetime import datetime, time
from .models import Paciente, Medico, Cita
import re

# --- VALIDADORES ---

def es_texto_valido(texto):
    """
    Retorna True si el texto solo contiene letras (incluyendo tildes/ñ) y espacios.
    Retorna False si contiene números o símbolos especiales.
    """
    if not texto: return False
    patron = r'^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+$'
    return re.match(patron, texto) is not None

# --- VISTAS ---

@login_required
def index(request):
    """
    Vista principal: Muestra el listado de citas según el rol (Staff vs Paciente)
    y carga las listas para los formularios (médicos y pacientes).
    """
    lista_citas = []
    
    # 1. Lógica para mostrar citas
    if request.user.is_staff:
        # Administrador ve todo
        lista_citas = Cita.objects.all().order_by('fecha_hora')
    else:
        # Paciente ve solo lo suyo
        try:
            paciente_actual = request.user.paciente 
            lista_citas = Cita.objects.filter(paciente=paciente_actual).order_by('fecha_hora')
        except AttributeError:
            # Usuario logueado pero sin perfil de Paciente asociado
            lista_citas = []

    # 2. Listas para los formularios (selects)
    lista_pacientes = Paciente.objects.all().order_by('nombre')
    lista_medicos = Medico.objects.all().order_by('nombre')

    contexto = {
        'citas': lista_citas,
        'pacientes': lista_pacientes,
        'medicos': lista_medicos
    }
    return render(request, 'agenda.html', contexto)


def registrar_paciente(request):
    if request.method == 'POST':
        try:
            nombre = request.POST.get('paciente-nombre')
            fecha_nac = request.POST.get('paciente-fecha-nac')
            telefono = request.POST.get('paciente-telefono')
            
            # --- 1. Validación de Caracteres ---
            if not es_texto_valido(nombre):
                messages.error(request, "Error: El nombre solo puede contener letras y espacios.")
                return redirect('inicio')

            # --- 2. Validación de Duplicados ---
            # __iexact hace que la búsqueda no distinga mayúsculas (Juan == juan)
            if Paciente.objects.filter(nombre__iexact=nombre).exists():
                messages.error(request, f"Error: El paciente '{nombre}' ya se encuentra registrado.")
                return redirect('inicio')
            
            # --- 3. Creación ---
            Paciente.objects.create(
                nombre=nombre,
                fecha_nacimiento=fecha_nac,
                telefono=telefono
            )
            messages.success(request, f"Paciente {nombre} registrado exitosamente.")
            return redirect('inicio')

        except Exception as e:
            messages.error(request, f"Error inesperado al registrar paciente: {e}")
            return redirect('inicio')
            
    return redirect('inicio')


def registrar_medico(request):
    if request.method == 'POST':
        try:
            nombre = request.POST.get('medico-nombre')
            especialidad = request.POST.get('medico-especialidad')

            errores = []

            # --- 1. Validación de Caracteres ---
            if not es_texto_valido(nombre):
                errores.append("El nombre contiene caracteres no permitidos (números o símbolos).")
            
            if not es_texto_valido(especialidad):
                errores.append("La especialidad contiene caracteres no permitidos.")

            # --- 2. Validación de Duplicados ---
            if Medico.objects.filter(nombre__iexact=nombre).exists():
                errores.append(f"El médico '{nombre}' ya existe en el sistema.")

            # Si acumulamos errores, los mostramos y cancelamos
            if errores:
                for error in errores:
                    messages.error(request, error)
                return redirect('inicio')
            
            # --- 3. Creación ---
            Medico.objects.create(
                nombre=nombre,
                especialidad=especialidad
            )
            messages.success(request, f"Médico {nombre} registrado exitosamente.")
            return redirect('inicio')

        except Exception as e:
            messages.error(request, f"Error inesperado al registrar médico: {e}")
            return redirect('inicio')
            
    return redirect('inicio')


def agendar_cita(request):
    if request.method == "POST":
        # 1. Obtener los datos usando los 'name' exactos de tu HTML
        fecha_hora_str = request.POST.get("cita-fecha")   # Viene como "YYYY-MM-DDTHH:MM"
        motivo = request.POST.get("cita-motivo")
        medico_id = request.POST.get("cita-medico-id")
        
        # Lógica para obtener el paciente:
        # Si es admin (staff), toma el ID del input. Si es usuario normal, es él mismo.
        if request.user.is_staff:
            paciente_id = request.POST.get("cita-paciente-id")
        else:
            # Asumimos que el usuario logueado tiene un perfil de paciente
            try:
                paciente_id = request.user.paciente.id 
            except AttributeError:
                messages.error(request, "Tu usuario no tiene un perfil de paciente asociado.")
                return redirect('inicio')

        # 2. Validar que la fecha no venga vacía
        if not fecha_hora_str:
            messages.error(request, "Debes seleccionar una fecha y hora.")
            return redirect("inicio")

        try:
            # 3. Convertir el formato de datetime-local (tiene una 'T' en medio)
            fecha_hora_obj = datetime.strptime(fecha_hora_str, "%Y-%m-%dT%H:%M")
            
        except ValueError:
            messages.error(request, "Formato de fecha inválido.")
            return redirect("inicio")

        # 4. Validaciones de negocio
        ahora = datetime.now()

        # A) Que no sea fecha pasada
        if fecha_hora_obj < ahora:
            messages.error(request, "No puedes agendar citas en el pasado.")
            return redirect("inicio")

        # B) Horario de atención (06:00 a 20:00)
        hora_cita = fecha_hora_obj.time()
        hora_apertura = time(6, 0)
        hora_cierre = time(20, 0)

        if not (hora_apertura <= hora_cita <= hora_cierre):
            messages.error(request, "El consultorio atiende solo de 06:00 AM a 08:00 PM.")
            return redirect("inicio")

        # 5. Crear la cita
        try:
            # Buscamos las instancias de Paciente y Medico para asegurarnos que existen
            paciente_obj = get_object_or_404(Paciente, id=paciente_id)
            medico_obj = get_object_or_404(Medico, id=medico_id)

            Cita.objects.create(
                paciente=paciente_obj,
                medico=medico_obj,
                fecha_hora=fecha_hora_obj, # Guardamos el objeto datetime completo
                motivo=motivo
            )
            messages.success(request, "Cita agendada correctamente.")
            
        except Exception as e:
            messages.error(request, f"Error al guardar la cita: {e}")

        return redirect("inicio")

    return redirect('inicio')


def eliminar_cita(request, id):
    try:
        cita = Cita.objects.get(id=id)
        # Opcional: Validar permisos aquí si es necesario
        cita.delete()
        messages.success(request, "Cita eliminada correctamente.")
    except Cita.DoesNotExist:
        messages.error(request, "La cita que intentas eliminar no existe.")
    
    return redirect('inicio')


def editar_cita(request, id):
    try:
        cita = Cita.objects.get(id=id)
    except Cita.DoesNotExist:
        messages.error(request, "Cita no encontrada.")
        return redirect('inicio')
    
    if request.method == 'POST':
        try:
            cita.paciente_id = request.POST.get('cita-paciente-id')
            cita.medico_id = request.POST.get('cita-medico-id')
            cita.fecha_hora = request.POST.get('cita-fecha')
            cita.motivo = request.POST.get('cita-motivo')
            cita.save()
            messages.success(request, "Cita actualizada correctamente.")
            return redirect('inicio')
        except Exception as e:
             messages.error(request, f"Error al editar: {e}")

    medicos = Medico.objects.all().order_by('nombre')
    pacientes = Paciente.objects.all().order_by('nombre')
    
    # Formateo de fecha para el input datetime-local
    fecha_formato = ""
    if cita.fecha_hora:
        fecha_formato = cita.fecha_hora.strftime('%Y-%m-%dT%H:%M')
    
    contexto = {
        'cita': cita,
        'medicos': medicos,
        'pacientes': pacientes,
        'fecha_formateada': fecha_formato
    }
    return render(request, 'editar_cita.html', contexto)