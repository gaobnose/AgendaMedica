from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.contrib.auth.models import User
from agenda.models import Paciente

def pagina_login(request):
    if request.method == 'POST':
        # Obtener usuario y contraseña del HTML
        usuario = request.POST.get('username')
        contra = request.POST.get('password')
        
        # Verificar si existen en la base de datos
        user = authenticate(request, username=usuario, password=contra)
        
        if user is not None:
            #  Si existe, iniciar sesión y redirigir a la Agenda
            login(request, user)
            return redirect('/') # Te lleva a la raíz (agenda)
        else:
            #  Si falla, mandar mensaje de error
            messages.error(request, "Usuario o contraseña incorrectos")
    
    return render(request, 'login.html')


def pagina_registro(request):
    if request.method == 'POST':
        usuario = request.POST.get('username')
        correo = request.POST.get('email')
        contra1 = request.POST.get('password')
        contra2 = request.POST.get('confirm_password')

        #  Validar que las contraseñas coincidan
        if contra1 != contra2:
            messages.error(request, "Las contraseñas no coinciden")
            return redirect('registro')

        # Validar que el usuario no exista ya
        if User.objects.filter(username=usuario).exists():
            messages.error(request, "El nombre de usuario ya está en uso")
            return redirect('registro')

        # Crear el usuario (Por defecto NO es admin, es paciente)
        try:
            #Crear el Usuario de Login
            user = User.objects.create_user(username=usuario, email=correo, password=contra1)
            user.save()
            
            # Crear automáticamente el perfil de Paciente asociado
            Paciente.objects.create(
                user=user,          # Conectamos con el usuario creado
                nombre=usuario,     # Usamos el nombre de usuario como nombre inicial
                telefono=""         # Dejamos vacío para que lo llene después
            )
            
            # 3. Iniciar sesión
            login(request, user)
            return redirect('inicio')
            
        except Exception as e:
            messages.error(request, f"Error al crear usuario: {e}")
            return redirect('registro')

    return render(request, 'registro.html')