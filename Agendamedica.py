####
class Paciente:
    def __init__(self, id, nombre, fecha_nac, telefono):
        self.id = id
        self.nombre = nombre
        self.fecha_nac = fecha_nac
        self.telefono = telefono
        self.historial = []  # lista de citas atendidas

class medicos:
    def  __init__(self, id, nombre, especialidad, ):
        self.id = id
        self.nombre = nombre
        self.especialidad = especialidad

class cita:
    def __init__(self, id, paciente, medico, fecha, hora, motivo, estado):
     self.id= id 
     self.paciente = paciente
     self.medico = medico
     self.fecha = fecha
     self.hora = hora
     self.motivo = motivo
     self.estado = estado  


class agendamedica:
   def __init__(self):
      self.pacientes = {}
      self.medicos = {}
      self.citas = {}
      self.next_paciente_id = 1
      self.next_medico_id = 1
      self.next_cita_id =1
            