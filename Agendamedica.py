import re
from datetime import datetime

class Paciente:
    def __init__(self, id, nombre, fecha_nac, telefono):
        self.id = id
        self.nombre = nombre
        self.fecha_nac = fecha_nac
        self.telefono = telefono
        self.historial = []

class Medico:
    def __init__(self, id, nombre, especialidad):
        self.id = id
        self.nombre = nombre
        self.especialidad = especialidad

class Cita:
    def __init__(self, id, paciente, medico, fecha_hora, motivo):
        self.id = id
        self.paciente = paciente
        self.medico = medico
        self.fecha_hora = fecha_hora
        self.motivo = motivo
        self.estado = 'pendiente'

class AgendaMedica:
    def __init__(self):
        self.pacientes = {}
        self.medicos = {}
        self.citas = {}
        self.next_paciente_id = 1
        self.next_medico_id = 1
        self.next_cita_id = 1

    def registrar_paciente(self, nombre, fecha_nac, telefono):
        paciente = Paciente(self.next_paciente_id, nombre, fecha_nac, telefono)
        self.pacientes[self.next_paciente_id] = paciente
        self.next_paciente_id += 1
        print(f"Paciente registrado: {paciente.nombre} (ID {paciente.id})")

    def registrar_medico(self, nombre, especialidad):
        medico = Medico(self.next_medico_id, nombre, especialidad)
        self.medicos[self.next_medico_id] = medico
        self.next_medico_id += 1
        print(f"Médico registrado: {medico.nombre} (ID {medico.id})")

    def agendar_cita(self, paciente_id, medico_id, fecha_hora, motivo):
        if paciente_id not in self.pacientes:
            print("Paciente no encontrado.")
            return
        if medico_id not in self.medicos:
            print("Médico no encontrado.")
            return
        for cita in self.citas.values():
            if (cita.medico.id == medico_id and cita.fecha_hora == fecha_hora and cita.estado == 'pendiente'):
                print("Conflicto de horario: el médico ya tiene una cita en esa fecha y hora.")
                return
        cita = Cita(self.next_cita_id, self.pacientes[paciente_id], self.medicos[medico_id], fecha_hora, motivo)
        self.citas[self.next_cita_id] = cita
        self.next_cita_id += 1
        print(f"Cita agendada: Paciente {cita.paciente.nombre} con Médico {cita.medico.nombre} el {fecha_hora}")

    def listar_proximas_citas(self):
        fecha_actual = datetime.now()
        citas_proximas = [c for c in self.citas.values() if c.fecha_hora >= fecha_actual and c.estado == 'pendiente']
        citas_proximas.sort(key=lambda c: c.fecha_hora)
        if not citas_proximas:
            print("No hay próximas citas.")
            return
        print("\n--- Próximas citas ---")
        for cita in citas_proximas:
            print(f"ID {cita.id}: {cita.fecha_hora} - Paciente: {cita.paciente.nombre}, Médico: {cita.medico.nombre}")

    def registrar_atencion(self, cita_id, notas):
        if cita_id not in self.citas:
            print("Cita no encontrada.")
            return
        cita = self.citas[cita_id]
        if cita.estado != 'pendiente':
            print("La cita ya fue atendida o cancelada.")
            return
        cita.estado = 'atendida'
        cita.paciente.historial.append({
            'fecha': cita.fecha_hora,
            'medico': cita.medico.nombre,
            'motivo': cita.motivo,
            'notas': notas
        })
        print(f"Cita ID {cita_id} marcada como atendida.")

    def historial_paciente(self, paciente_id):
        if paciente_id not in self.pacientes:
            print("Paciente no encontrado.")
            return
        paciente = self.pacientes[paciente_id]
        if not paciente.historial:
            print(f"No hay historial médico para {paciente.nombre}.")
            return
        print(f"\n--- Historial médico de {paciente.nombre} ---")
        for atencion in paciente.historial:
            print(f"- {atencion['fecha']}: Médico {atencion['medico']}, Motivo: {atencion['motivo']}, Notas: {atencion['notas']}")

    def listar_pacientes(self):
        if not self.pacientes:
            print("No hay pacientes registrados.")
            return
        print("\n--- Lista de pacientes ---")
        for p in self.pacientes.values():
            print(f"ID {p.id}: {p.nombre}, Fecha de nacimiento: {p.fecha_nac}, Teléfono: {p.telefono}")

    def listar_medicos(self):
        if not self.medicos:
            print("No hay médicos registrados.")
            return
        print("\n--- Lista de médicos ---")
        for m in self.medicos.values():
            print(f"ID {m.id}: {m.nombre}, Especialidad: {m.especialidad}")
