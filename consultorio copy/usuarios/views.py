from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.models import User
from agenda.models import Paciente
import re

def pagina_login(request):
    if request.method == 'POST':
        usuario = request.POST.get('username')
        contra = request.POST.get('password')
        
        user = authenticate(request, username=usuario, password=contra)
        
        if user is not None:
            login(request, user)
            return redirect('/')
        else:
            messages.error(request, "Usuario o contraseña incorrectos")
    
    return render(request, 'login.html')


def pagina_registro(request):
    if request.method == 'POST':
        usuario = request.POST.get('username')
        correo = request.POST.get('email')
        contra1 = request.POST.get('password')
        contra2 = request.POST.get('confirm_password')

        if len(usuario) < 3:
            messages.error(request, "El nombre debe tener 3 o más caracteres")
            return redirect('registro')

        if re.search(r'\d', usuario):
            messages.error(request, "El nombre no puede contener números")
            return redirect('registro')

        if contra1 != contra2:
            messages.error(request, "Las contraseñas no coinciden")
            return redirect('registro')

        if User.objects.filter(username=usuario).exists():
            messages.error(request, "El nombre de usuario ya está en uso")
            return redirect('registro')

        try:
            user = User.objects.create_user(username=usuario, email=correo, password=contra1)
            user.save()
            
            Paciente.objects.create(
                user=user,
                nombre=usuario,
                telefono=""
            )
            
            login(request, user)
            return redirect('inicio')
            
        except Exception as e:
            messages.error(request, f"Error al crear usuario: {e}")
            return redirect('registro')

    return render(request, 'registro.html')

def cerrar_sesion(request):
    logout(request)
    return redirect('login')