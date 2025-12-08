import sqlite3
from datetime import datetime

# Nombre del archivo donde se guardará la BD local
DB_NAME = "local.db"

def insertar_usuario(first_name, last_name, email, password, role, phone, city, gender):
    try:
        # 1. Establecer conexión
        conexion = sqlite3.connect(DB_NAME)
        cursor = conexion.cursor()

        # 2. Definir la consulta SQL con placeholders (?)
        query = """
        INSERT INTO users (
            first_name, last_name, email, password, role, phone, city, gender, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        
        # 3. Obtener la fecha actual para el campo created_at
        fecha_creacion = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # 4. Ejecutar la consulta pasando los datos en una tupla
        cursor.execute(query, (
            first_name, last_name, email, password, role, phone, city, gender, fecha_creacion
        ))

        # 5. Confirmar los cambios
        conexion.commit()
        print(f"Éxito: El usuario {first_name} ha sido registrado.")
        return True

    except sqlite3.Error as e:
        print(f"Error al insertar en la base de datos: {e}")
        return False

    finally:
        # 6. Siempre cerrar la conexión, pase lo que pase
        if conexion:
            conexion.close()

def insertar_maquina(user_id, name, location, status, max_water, current_level, price, 
                     filter_ac, filter_sg, filter_zeo, filter_rom, filter_ml):
    conexion = None
    try:
        conexion = sqlite3.connect(DB_NAME)
        cursor = conexion.cursor()

        # Query con todos los campos que mencionaste
        query = """
        INSERT INTO machines (
            user_id, name, location, status, max_water, current_level, price,
            filter_active_carbon, filter_sand_and_gravel, filter_zeolite,
            filter_reverse_osmosis_membrane, filter_mineral_layer
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """

        valores = (
            user_id, name, location, status, max_water, current_level, price,
            filter_ac, filter_sg, filter_zeo, filter_rom, filter_ml
        )

        cursor.execute(query, valores)
        conexion.commit()
        
        print(f"✅ Máquina '{name}' vinculada al usuario ID {user_id} correctamente.")
        return True

    except sqlite3.Error as e:
        print(f"❌ Error al insertar máquina: {e}")
        return False
    finally:
        if conexion:
            conexion.close()