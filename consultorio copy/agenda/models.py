from django.db import models

#  Modelo Paciente
class Paciente(models.Model):
    nombre = models.CharField(max_length=100)
    fecha_nacimiento = models.DateField()
    telefono = models.CharField(max_length=20)

    def __str__(self):
        return self.nombre

# Modelo Medico 
class Medico(models.Model):
    nombre = models.CharField(max_length=100)
    especialidad = models.CharField(max_length=50)

    def __str__(self):
        return self.nombre

# Modelo Cita
class Cita(models.Model):
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE)
    medico = models.ForeignKey(Medico, on_delete=models.CASCADE)
    fecha_hora = models.DateTimeField()
    motivo = models.TextField()
    
    ESTADOS = [
        ('pendiente', 'Pendiente'),
        ('atendida', 'Atendida'),
        ('cancelada', 'Cancelada'),
    ]
    estado = models.CharField(max_length=10, choices=ESTADOS, default='pendiente')
    notas_atencion = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Cita {self.id} - {self.paciente}"