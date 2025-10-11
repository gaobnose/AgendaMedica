import re
from datetime import datetime
import pyodbc
from dotenv import load_dotenv
import os

class ConexionBD:
    def __init__(self):
        load_dotenv()
        self.servidor = os.getenv("DB_SERVER")
        self.base_datos = os.getenv("DB_NAME")
        self.usuario = os.getenv("DB_USER")
        self.contrasena = os.getenv("DB_PASSWORD")
        self.conexion = None

    def conectar(self):
        try:
            self.conexion = pyodbc.connect(
                f'DRIVER={{ODBC Driver 17 for SQL Server}};'
                f'SERVER={self.servidor};'
                f'DATABASE={self.base_datos};'
                f'UID={self.usuario};'
                f'PWD={self.contrasena}'
            )
            print("Conexión exitosa a SQL Server.")
        except Exception as e:
            print("Error al conectar a la base de datos:", e)

    def cerrar_conexion(self):
        if self.conexion:
            self.conexion.close()
            print("Conexión cerrada.")

    def ejecutar_consulta(self, consulta, parametros=()):
        try:
            cursor = self.conexion.cursor()
            cursor.execute(consulta, parametros)
            return cursor.fetchall()
        except Exception as e:
            print("Error al ejecutar la consulta:", e)
            return []

    def ejecutar_instruccion(self, consulta, parametros=()):
        try:
            cursor = self.conexion.cursor()
            cursor.execute(consulta, parametros)
            self.conexion.commit()
            print("Instrucción ejecutada correctamente.")
        except Exception as e:
            print("Error al ejecutar la instrucción:", e)
            self.conexion.rollback()



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

    def listar_pacientes(self, pacientes):
        
        if not pacientes:
            print("No hay pacientes registrados.")
            return
        print("\n--- Lista de pacientes ---")
        for p in pacientes:
            print(f"ID {p[0]}: {p[1]}, Fecha de nacimiento: {p[2]}, Teléfono: {p[3]}")

    def listar_medicos(self, medicos):
        if not medicos:
            print("No hay médicos registrados.")
            return
        print("\n--- Lista de médicos ---")
        for m in medicos:
            print(f"ID {m[0]}: {m[1]}, Especialidad: {m[2]}")
            


def mostrar_menu():
    print("\n--- MENÚ PRINCIPAL ---")
    print("1. Registrar paciente")
    print("2. Registrar médico")
    print("3. Agendar cita médica")
    print("4. Listar próximas citas")
    print("5. Registrar atención de cita")
    print("6. Ver historial médico por paciente")
    print("7. Listar pacientes")
    print("8. Listar médicos")
    print("9. Salir")

def main():
    agenda = AgendaMedica()
    db = ConexionBD()
    db.conectar()
    while True:
        mostrar_menu()
        opcion = input("Seleccione una opción: ")

        if opcion == '1':
            nombre = input("Nombre del paciente: ").strip()
            fecha_nac = input("Fecha de nacimiento (YYYY-MM-DD): ").strip()
            telefono = input("Teléfono: ").strip()
            db.ejecutar_instruccion(
            "INSERT INTO Pacientes (nombre, fechaNacimiento, Telefono) VALUES (?, ?, ?)", (nombre, fecha_nac, telefono)
            )
            agenda.registrar_paciente(nombre, fecha_nac, telefono)

        elif opcion == '2':
            nombre = input("Nombre del médico: ").strip()
            especialidad = input("Especialidad: ").strip()
            db.ejecutar_instruccion(
            "INSERT INTO Medicos (nombre, Especialidad) VALUES (?, ?, )", (nombre, especialidad)
            )
            agenda.registrar_medico(nombre, especialidad)

        elif opcion == '3':
            try:
                paciente_id = int(input("ID del paciente: "))
                medico_id = int(input("ID del médico: "))
                fecha_str = input("Fecha y hora de la cita (YYYY-MM-DD HH:MM): ").strip()
                fecha_hora = datetime.strptime(fecha_str, "%Y-%m-%d %H:%M")
                motivo = input("Motivo de la consulta: ").strip()
                agenda.agendar_cita(paciente_id, medico_id, fecha_hora, motivo)
            except ValueError:
                print("Error: Formato de fecha/hora inválido o ID no numérico.")

        elif opcion == '4':
            agenda.listar_proximas_citas()

        elif opcion == '5':
            try:
                cita_id = int(input("ID de la cita a registrar como atendida: "))
                notas = input("Notas de la atención: ").strip()
                agenda.registrar_atencion(cita_id, notas)
            except ValueError:
                print("ID inválido.")

        elif opcion == '6':
            try:
                paciente_id = int(input("ID del paciente para ver historial: "))
                agenda.historial_paciente(paciente_id)
            except ValueError:
                print("ID inválido.")

        elif opcion == '7':
            pacientes = db.ejecutar_consulta("SELECT * FROM Pacientes")
            agenda.listar_pacientes(pacientes)

        elif opcion == '8':
            medicos = db.ejecutar_consulta("SELECT * FROM Medicos")
            agenda.listar_medicos(medicos)

        elif opcion == '9':
            print("Saliendo del sistema. ¡Hasta luego!")
            break

        else:
            print("Opción no válida, intente de nuevo.")

if __name__ == "__main__":
    main()
