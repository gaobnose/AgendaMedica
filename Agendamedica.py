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

    def agendar_cita(self, paciente_id, medico_id, fecha_hora, motivo, db):
        paciente_existe = db.ejecutar_consulta("SELECT 1 FROM Pacientes WHERE PacienteID = ?", (paciente_id,))
        if not paciente_existe:
            print(f"Error: No se encontró ningún paciente con el ID {paciente_id}.")
            return
        medico_existe = db.ejecutar_consulta("SELECT 1 FROM Medicos WHERE MedicoID = ?", (medico_id,))
        if not medico_existe:
            print(f"Error: No se encontró ningún médico con el ID {medico_id}.")
            return
        conflicto = db.ejecutar_consulta(
            "SELECT 1 FROM Citas WHERE MedicoID = ? AND FechaHora = ? AND Estado = 'pendiente'",
            (medico_id, fecha_hora)
        )
        if conflicto:
            print("Error: Conflicto de horario. El médico ya tiene una cita en esa fecha y hora.")
            return     
        consulta_sql = """
        INSERT INTO Citas (PacienteID, MedicoID, FechaHora, Motivo, Estado)
        VALUES (?, ?, ?, ?, 'pendiente')
        """
        try:
            db.ejecutar_instruccion(consulta_sql, (paciente_id, medico_id, fecha_hora, motivo))
            print(f"Cita agendada exitosamente en la base de datos.")

        except Exception as e:
            print(f"Ocurrió un error inesperado al agendar la cita: {e}")

    def listar_proximas_citas(self, db):
        consulta_sql = """
        SELECT
            c.CitaID,
            c.FechaHora,
            p.Nombre AS NombrePaciente,
            m.Nombre AS NombreMedico,
            c.Motivo
        FROM Citas c
        JOIN Pacientes p ON c.PacienteID = p.PacienteID
        JOIN Medicos m ON c.MedicoID = m.MedicoID
        WHERE c.Estado = 'pendiente'
        ORDER BY c.FechaHora ASC;
        """
        citas = db.ejecutar_consulta(consulta_sql)
        if not citas:
            print("No hay próximas citas pendientes.")
            return
        print("\n--- Próximas citas pendientes ---")
        for c in citas:
            fecha_formateada = c[1].strftime('%Y-%m-%d %H:%M')
            print(f"\nID Cita: {c[0]} | Fecha: {fecha_formateada}")
            print(f"  Paciente: {c[2]}")
            print(f"  Médico:   {c[3]}")
            print(f"  Motivo:   {c[4]}")

    def registrar_atencion(self, cita_id, notas, db):
        consulta_sql = "SELECT Estado FROM Citas WHERE CitaID = ?"
        resultado = db.ejecutar_consulta(consulta_sql, (cita_id,))

        if not resultado:
            print(f"Error: No se encontró ninguna cita con el ID {cita_id}.")
            return

        estado_actual = resultado[0][0]

        if estado_actual == 'atendida':
            print(f"Aviso: La cita ID {cita_id} ya ha sido atendida.")
            return
        elif estado_actual != 'pendiente':
            print(f"Error: La cita no se puede atender porque su estado es '{estado_actual}'.")
            return
        
        print(f"Registrando atención para la cita ID {cita_id}...")
        update_sql = "UPDATE Citas SET Estado = 'atendida', NotasAtencion = ? WHERE CitaID = ?"
        db.ejecutar_instruccion(update_sql, (notas, cita_id))


    def historial_paciente(self, paciente_id, db):
        if not db.ejecutar_consulta("SELECT 1 FROM Pacientes WHERE PacienteID = ?", (paciente_id,)):
            print(f"\n>> Error: No se encontró ningún paciente con el ID {paciente_id}.")
            return
            
        historial = db.ejecutar_consulta(
            "SELECT c.FechaHora, m.Nombre, c.Motivo, c.NotasAtencion FROM Citas c JOIN Medicos m ON c.MedicoID = m.MedicoID WHERE c.PacienteID = ? AND c.Estado = 'atendida' ORDER BY c.FechaHora DESC",
            (paciente_id,)
        )

        nombre_paciente = db.ejecutar_consulta("SELECT Nombre FROM Pacientes WHERE PacienteID = ?", (paciente_id,))[0][0]
        print(f"--- HISTORIAL MÉDICO DE: {nombre_paciente} (ID {paciente_id}) ---")

        if not historial:
            print("\n>> No hay historial médico para este paciente.")
            return

        for registro in historial:
            fecha, medico_nombre, motivo, notas = registro
            print("\n-------------------------------------------")
            print(f"Fecha:     {fecha.strftime('%Y-%m-%d %H:%M')}")
            print(f"Médico:    {medico_nombre}")
            print(f"Motivo:    {motivo}")
            print(f"Notas:     {notas}")
        print("-------------------------------------------")

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


    def cancelar_cita(self, cita_id, db):
        resultado = db.ejecutar_consulta("SELECT Estado FROM Citas WHERE CitaID = ?", (cita_id,))
        if not resultado:
            print(f"\n>> Error: No se encontró ninguna cita con el ID {cita_id}.")
            return

        estado_actual = resultado[0][0]
        if estado_actual == 'cancelada':
            print(f"\n>> Aviso: La cita ID {cita_id} ya se encuentra cancelada.")
        elif estado_actual == 'atendida':
            print(f"\n>> Error: Una cita ya atendida no puede ser cancelada.")
        else:
            update_sql = "UPDATE Citas SET Estado = 'cancelada' WHERE CitaID = ?"
            if db.ejecutar_instruccion(update_sql, (cita_id,)):
                print(f"\n>> Cita ID {cita_id} cancelada exitosamente.")


def limpiar_pantalla():
    os.system('cls' if os.name == 'nt' else 'clear')


def imprimir_tabla(datos, encabezados):
        """Imprime una lista de tuplas o listas en un formato de tabla."""
    # Calcular anchos de columna
        anchos = [len(h) for h in encabezados]
        for fila in datos:
            for i, celda in enumerate(fila):
                if len(celda) > anchos[i]:
                    anchos[i] = len(celda)
    
    # Imprimir
        separador = "+-" + "-+-".join("-" * a for a in anchos) + "-+"
        print(separador)
        print("| " + " | ".join(h.ljust(anchos[i]) for i, h in enumerate(encabezados)) + " |")
        print(separador)
        for fila in datos:
            print("| " + " | ".join(celda.ljust(anchos[i]) for i, celda in enumerate(fila)) + " |")
        print(separador)
            


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
    print("9. Cancelar Cita")
    print("10. Salir")
    print("--- Dr. Simi Constultorio Médico ---\n")

def validar_nombre(prompt):
    """Pide un nombre y valida que tenga más de 3 caracteres y solo contenga letras y espacios."""
    while True:
        nombre = input(prompt).strip()
        if len(nombre) > 3 and nombre.replace(' ', '').isalpha():
            return nombre
        else:
            print("Error: El nombre debe tener más de 3 caracteres y contener solo letras y espacios. Intente de nuevo.")


def validar_fecha(prompt, formato="%Y-%m-%d"):
    """Pide una fecha y valida que tenga el formato correcto."""
    while True:
        fecha_str = input(prompt).strip()
        try:
            fecha_obj = datetime.strptime(fecha_str, formato)
            return fecha_obj
        except ValueError:
            print(f"Error: Formato de fecha inválido. Por favor, use el formato {formato.replace('%Y', 'AAAA').replace('%m', 'MM').replace('%d', 'DD').replace('%H', 'HH').replace('%M', 'mm')}.")


def validar_telefono(prompt):
    """Pide un teléfono y valida que sea numérico y tenga una longitud razonable."""
    while True:
        telefono = input(prompt).strip()
        if telefono.isdigit() and len(telefono) >= 8:
            return telefono
        else:
            print("Error: El teléfono debe contener solo números y tener al menos 8 dígitos. Intente de nuevo.")


def validar_entero(prompt):
    """Pide un número entero (como un ID) y valida que sea un número."""
    while True:
        id_str = input(prompt).strip()
        try:
            return int(id_str)
        except ValueError:
            print("Error: Por favor, ingrese un número de ID válido.")


def validar_texto_no_vacio(prompt):
    """Pide un texto (como un motivo o notas) y valida que no esté vacío."""
    while True:
        texto = input(prompt).strip()
        if texto:
            return texto
        else:
            print("Error: Este campo no puede estar vacío. Intente de nuevo.")

def validar_nombre_sin_simbolos(prompt):
    """Pide un nombre y valida que tenga más de 3 caracteres, solo contenga letras y espacios, y no incluya símbolos."""
    while True:
        nombre = input(prompt).strip()
        if len(nombre) > 3 and all(c.isalpha() or c.isspace() for c in nombre):
            return nombre
        else:
            print("Error: El texto debe tener más de 3 caracteres, contener solo letras y no incluir símbolos. Intente de nuevo.")

def main():
    agenda = AgendaMedica()
    db = ConexionBD()
    db.conectar()
    
    print("Conectando a la base de datos...")
    db.conectar()
    
    if not db.conexion:
        print("\nNo se pudo conectar a la base de datos. El programa terminará.")
        input("Presione Enter para salir.")
        return

    while True:
        limpiar_pantalla()
        mostrar_menu()
        opcion = input("Seleccione una opción: ")

        if opcion == '1':
            limpiar_pantalla()
            print("--- REGISTRAR NUEVO PACIENTE ---")
            nombre = validar_nombre("Nombre del paciente: ")
            fecha_obj = validar_fecha("Fecha de nacimiento (AAAA-MM-DD): ", formato="%Y-%m-%d")
            fecha_nac = fecha_obj.strftime("%Y-%m-%d")
            telefono = validar_telefono("Teléfono: ")
            db.ejecutar_instruccion(
            "INSERT INTO Pacientes (nombre, fechaNacimiento, Telefono) VALUES (?, ?, ?)", (nombre, fecha_nac, telefono)
            )
            agenda.registrar_paciente(nombre, fecha_nac, telefono)

        elif opcion == '2':
            limpiar_pantalla()
            print("--- REGISTRAR NUEVO MÉDICO ---")
            nombre = validar_nombre_sin_simbolos("Nombre del médico (solo letras, mínimo 3 caracteres, sin símbolos): ")
            especialidad = validar_nombre_sin_simbolos("Especialidad del médico (solo letras, mínimo 3 caracteres, sin símbolos): ")
            db.ejecutar_instruccion(
                "INSERT INTO Medicos (nombre, especialidad) VALUES (?, ?)", (nombre, especialidad)
            )
            agenda.registrar_medico(nombre, especialidad)

        elif opcion == '3':
            limpiar_pantalla()
            print("--- AGENDAR NUEVA CITA ---")
            try:
                paciente_id = validar_entero("ID del paciente: ")
                medico_id = validar_entero("ID del médico: ")
                fecha_hora = validar_fecha("Fecha y hora de la cita (AAAA-MM-DD HH:MM): ", formato="%Y-%m-%d %H:%M")
                motivo = validar_texto_no_vacio("Motivo de la consulta: ")
                agenda.agendar_cita(paciente_id, medico_id, fecha_hora, motivo,db)
            except ValueError:
                print("Error: Formato de fecha/hora inválido o ID no numérico.")

        elif opcion == '4':
            limpiar_pantalla()
            agenda.listar_proximas_citas(db)

        elif opcion == '5':
            limpiar_pantalla()
            print("--- REGISTRAR ATENCIÓN DE CITA ---")
            try:
                cita_id = validar_entero("ID de la cita a registrar como atendida: ")
                notas = validar_texto_no_vacio("Notas de la atención: ")
                agenda.registrar_atencion(cita_id, notas,db)
            except ValueError:
                print("ID inválido.")
          
        elif opcion == '6':
            limpiar_pantalla()
            try:
                paciente_id = validar_entero("ID del paciente para ver historial: ")
                agenda.historial_paciente(paciente_id,db)
            except ValueError:
                print("ID inválido.")
             
        elif opcion == '7':
            limpiar_pantalla()
            pacientes = db.ejecutar_consulta("SELECT * FROM Pacientes")
            agenda.listar_pacientes(pacientes)

        elif opcion == '8':
            limpiar_pantalla()
            medicos = db.ejecutar_consulta("SELECT * FROM Medicos")
            agenda.listar_medicos(medicos)

        elif opcion == '9':
            limpiar_pantalla()
            print("--- CANCELAR CITA ---")
            cita_id = validar_entero("ID de la Cita a cancelar: ")
            agenda.cancelar_cita(cita_id, db)


        elif opcion == '10':
            print("\nSaliendo del sistema. ¡Hasta luego!")
            db.cerrar_conexion()
            break

        else:
            print("\n>> Opción no válida. Intente de nuevo.")

        if opcion != '10':
            input("\nPresione Enter para volver al menú...")

if __name__ == "__main__":
    main()
