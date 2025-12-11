from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from datetime import datetime, time
from .models import Paciente, Medico, Cita
import re
import json
import urllib.request
from django.contrib.auth.models import User
from django.db import IntegrityError

def es_texto_valido(texto):
    if not texto: return False
    patron = r'^[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+$'
    return re.match(patron, texto) is not None

@login_required
def index(request):
    lista_citas = []
    
    if request.user.is_staff:
        lista_citas = Cita.objects.all().order_by('fecha_hora')
    else:
        try:
            paciente_actual = request.user.paciente 
            lista_citas = Cita.objects.filter(paciente=paciente_actual).order_by('fecha_hora')
        except AttributeError:
            lista_citas = []

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
            
           
            if not es_texto_valido(nombre):
                messages.error(request, "Error: El nombre solo puede contener letras y espacios.")
                return redirect('inicio')

           
            if fecha_nac:
                fecha_nac_obj = datetime.strptime(fecha_nac, '%Y-%m-%d').date()
                fecha_hoy = datetime.now().date()
                
                if fecha_nac_obj.year < 1900:
                    messages.error(request, "Error: El año de nacimiento no puede ser menor a 1900.")
                    return redirect('inicio')
                
                if fecha_nac_obj > fecha_hoy:
                    messages.error(request, "Error: El paciente no puede haber nacido en el futuro.")
                    return redirect('inicio')

            if Paciente.objects.filter(nombre__iexact=nombre).exists():
                messages.error(request, f"Error: El paciente '{nombre}' ya se encuentra registrado.")
                return redirect('inicio')
            
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

            if not es_texto_valido(nombre):
                errores.append("El nombre contiene caracteres no permitidos (números o símbolos).")
            
            if not es_texto_valido(especialidad):
                errores.append("La especialidad contiene caracteres no permitidos.")

            if Medico.objects.filter(nombre__iexact=nombre).exists():
                errores.append(f"El médico '{nombre}' ya existe en el sistema.")

            if errores:
                for error in errores:
                    messages.error(request, error)
                return redirect('inicio')
            
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
        fecha_hora_str = request.POST.get("cita-fecha")
        motivo = request.POST.get("cita-motivo")
        medico_id = request.POST.get("cita-medico-id")
        
        
        if request.user.is_staff:
            paciente_id = request.POST.get("cita-paciente-id")
        else:
            try:
                paciente_id = request.user.paciente.id 
            except AttributeError:
                messages.error(request, "Tu usuario no tiene un perfil de paciente asociado.")
                return redirect('inicio')

        
        if not fecha_hora_str:
            messages.error(request, "Debes seleccionar una fecha y hora.")
            return redirect("inicio")

        try:
            fecha_hora_obj = datetime.strptime(fecha_hora_str, "%Y-%m-%dT%H:%M")
        except ValueError:
            messages.error(request, "Formato de fecha inválido.")
            return redirect("inicio")

       
        ahora = datetime.now()
        if fecha_hora_obj < ahora:
            messages.error(request, "No puedes agendar citas en el pasado.")
            return redirect("inicio")

        hora_cita = fecha_hora_obj.time()
        hora_apertura = time(6, 0)
        hora_cierre = time(20, 0)
        if not (hora_apertura <= hora_cita <= hora_cierre):
            messages.error(request, "El consultorio atiende solo de 06:00 AM a 08:00 PM.")
            return redirect("inicio")

       
        if Cita.objects.filter(medico_id=medico_id, fecha_hora=fecha_hora_obj).exists():
            messages.error(request, "Lo sentimos, el médico ya tiene una cita ocupada a esa hora exacta.")
            return redirect("inicio")

        try:
            paciente_obj = get_object_or_404(Paciente, id=paciente_id)
            medico_obj = get_object_or_404(Medico, id=medico_id)

            Cita.objects.create(
                paciente=paciente_obj,
                medico=medico_obj,
                fecha_hora=fecha_hora_obj,
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
            paciente_id = request.POST.get('cita-paciente-id')
            medico_id = request.POST.get('cita-medico-id')
            fecha_hora_str = request.POST.get('cita-fecha')
            motivo = request.POST.get('cita-motivo')

            if not fecha_hora_str:
                messages.error(request, "Debes seleccionar una fecha y hora.")
                return redirect('editar_cita', id=id)

            try:
                fecha_hora_obj = datetime.strptime(fecha_hora_str, "%Y-%m-%dT%H:%M")
            except ValueError:
                messages.error(request, "Formato de fecha inválido.")
                return redirect('editar_cita', id=id)

           
            ahora = datetime.now()
            if fecha_hora_obj < ahora:
                messages.error(request, "No puedes mover una cita al pasado.")
                return redirect('editar_cita', id=id)

            hora_cita = fecha_hora_obj.time()
            if not (time(6, 0) <= hora_cita <= time(20, 0)):
                messages.error(request, "El consultorio atiende solo de 06:00 AM a 08:00 PM.")
                return redirect('editar_cita', id=id)

            
            choque = Cita.objects.filter(medico_id=medico_id, fecha_hora=fecha_hora_obj).exclude(id=id).exists()
            
            if choque:
                messages.error(request, "El médico ya tiene otra cita agendada a esa hora.")
                return redirect('editar_cita', id=id)

            cita.paciente_id = paciente_id
            cita.medico_id = medico_id
            cita.fecha_hora = fecha_hora_obj 
            cita.motivo = motivo
            cita.save()
            
            messages.success(request, "Cita actualizada correctamente.")
            return redirect('inicio')

        except Exception as e:
             messages.error(request, f"Error al editar: {e}")
             return redirect('editar_cita', id=id)

    medicos = Medico.objects.all().order_by('nombre')
    pacientes = Paciente.objects.all().order_by('nombre')
    
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

@login_required
def generar_usuarios_aleatorios(request):
    if not request.user.is_staff:
        messages.error(request, "No tienes permisos para realizar esta acción.")
        return redirect('inicio')

    if request.method == 'POST':
        try:
            
            url = 'https://randomuser.me/api/?results=1&nat=es'
            response = urllib.request.urlopen(url)
            data = json.loads(response.read())
            
            usuario_data = data['results'][0]
            
            
            nombre_first = usuario_data['name']['first']
            nombre_last = usuario_data['name']['last']
            username = usuario_data['login']['username']
            password = usuario_data['login']['password']
            email = usuario_data['email']
            phone = usuario_data['phone']
            dob = usuario_data['dob']['date'][:10] # YYYY-MM-DD
            
            # Nombre completo para el modelo Paciente
            nombre_completo = f"{nombre_first} {nombre_last}"

            # Verificar si existe el usurio
            if User.objects.filter(username=username).exists():
                
                import random
                username = f"{username}{random.randint(100, 999)}"
            
            # Crear Usuario Django
            user = User.objects.create_user(username=username, email=email, password=password)
            user.save()
            
            # Crear Perfil Paciente
            Paciente.objects.create(
                user=user,
                nombre=nombre_completo,
                fecha_nacimiento=dob,
                telefono=phone
            )
            
            messages.success(request, f"Usuario generado: {username} (Pass: {password})")
            
        except Exception as e:
            messages.error(request, f"Error al generar usuario: {e}")
            
    return redirect('inicio')