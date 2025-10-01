####
class Paciente:
    def __init__(self, id, nombre, fecha_nac, telefono):
        self.id = id
        self.nombre = nombre
        self.fecha_nac = fecha_nac
        self.telefono = telefono
        self.historial = []  # lista de citas atendidas


            