import sqlite3
from datetime import datetime

DB_NAME = "local.db"

def insertar_usuario(first_name, last_name, email, password, role, phone, city, gender):
    try:

        conexion = sqlite3.connect(DB_NAME)
        cursor = conexion.cursor()

        query = """
        INSERT INTO users (
            first_name, last_name, email, password, role, phone, city, gender, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        
        fecha_creacion = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        cursor.execute(query, (
            first_name, last_name, email, password, role, phone, city, gender, fecha_creacion
        ))

        conexion.commit()
        print(f"Éxito: El usuario {first_name} ha sido registrado.")
        return True

    except sqlite3.Error as e:
        print(f"Error al insertar en la base de datos: {e}")
        return False

    finally:
        if conexion:
            conexion.close()

def insertar_maquina(user_id, name, location, status, max_water, current_level, price, 
                     filter_ac, filter_sg, filter_zeo, filter_rom, filter_ml):
    conexion = None
    try:
        conexion = sqlite3.connect(DB_NAME)
        cursor = conexion.cursor()
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

        print(f"Máquina '{name}' vinculada al usuario ID {user_id} correctamente.")
        return True

    except sqlite3.Error as e:
        print(f"Error al insertar máquina: {e}")
        return False
    finally:
        if conexion:
            conexion.close()

def registrar_pago_y_ventas(
    remote_payment_id,
    payment_method,
    bank,
    reference_code,
    amount,
    receipt,
    recharge,
    carrito,
    user_id,
    machine_id
):
    conexion = None
    try:
        conexion = sqlite3.connect(DB_NAME)
        cursor = conexion.cursor()
        cursor.execute("PRAGMA foreign_keys = ON")

        fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Insertar PAGO
        query_pago = """
        INSERT INTO payments (
            remote_id, date, payment_method, bank,
            reference_code, amount, receipt, recharge
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """

        cursor.execute(query_pago, (
            remote_payment_id,
            fecha_actual,
            payment_method,
            bank,
            reference_code,
            amount,
            receipt,
            recharge
        ))

        payment_id = cursor.lastrowid  # 🔥 ID DEL PAGO

        # Insertar VENTAS (una por producto del carrito)
        query_venta = """
        INSERT INTO sales (
            remote_id, date, product, price,
            quantity, subtotal, user_id,
            machine_id, payment_id
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """

        for item in carrito:
            producto = item['producto']
            cantidad = item['cantidad']
            precio = item['precio']
            subtotal = item['monto_final']

            cursor.execute(query_venta, (
                f"SALE-{remote_payment_id}",
                fecha_actual,
                f"Botellón {producto.litros}L",
                precio,
                cantidad,
                subtotal,
                user_id,
                machine_id,
                payment_id
            ))

        conexion.commit()
        print("Pago y ventas registradas correctamente")
        return True

    except sqlite3.Error as e:
        if conexion:
            conexion.rollback()
        print(f"Error en la transacción: {e}")
        return False

    finally:
        if conexion:
            conexion.close()

