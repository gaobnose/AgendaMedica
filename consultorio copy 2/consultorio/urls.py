"""
URL configuration for consultorio project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
# consultorio/consultorio/urls.py

# C:\Users\Martin\Desktop\xd\consultorio\consultorio\urls.py

from django.contrib import admin
from django.urls import path, include
from usuarios.views import pagina_login # Importar la vista

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('agenda.urls')),
    
    # Nueva ruta para el login
    path('login/', pagina_login, name='login'),
]