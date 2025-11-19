from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages

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