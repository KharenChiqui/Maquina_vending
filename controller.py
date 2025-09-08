import sqlite3

DB_NAME = "local.db"

# --------------------------
# Funciones de conexión
# --------------------------
def get_connection():
    """Abre conexión a la base de datos local"""
    return sqlite3.connect(DB_NAME)

# --------------------------
# CRUD genérico
# --------------------------
def insert(table, data: dict):
    """
    Inserta un registro en una tabla.
    :param table: nombre de la tabla
    :param data: diccionario {columna: valor}
    """
    conn = get_connection()
    cursor = conn.cursor()

    columns = ", ".join(data.keys())
    placeholders = ", ".join(["?" for _ in data.values()])
    values = tuple(data.values())

    query = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"
    cursor.execute(query, values)

    conn.commit()
    conn.close()
    print(f"✅ Insertado en {table}: {data}")
    return cursor.lastrowid


def get_all(table):
    """Obtiene todos los registros de una tabla"""
    conn = get_connection()
    cursor = conn.cursor()

    query = f"SELECT * FROM {table}"
    cursor.execute(query)
    rows = cursor.fetchall()

    conn.close()
    return rows


def get_by_id(table, record_id):
    """Obtiene un registro por ID"""
    conn = get_connection()
    cursor = conn.cursor()

    query = f"SELECT * FROM {table} WHERE id = ?"
    cursor.execute(query, (record_id,))
    row = cursor.fetchone()

    conn.close()
    return row


def update(table, record_id, data: dict):
    """Actualiza un registro por ID"""
    conn = get_connection()
    cursor = conn.cursor()

    set_clause = ", ".join([f"{col} = ?" for col in data.keys()])
    values = tuple(data.values()) + (record_id,)

    query = f"UPDATE {table} SET {set_clause} WHERE id = ?"
    cursor.execute(query, values)

    conn.commit()
    conn.close()
    print(f"✏️ Registro {record_id} actualizado en {table}")


def delete(table, record_id):
    """Elimina un registro por ID"""
    conn = get_connection()
    cursor = conn.cursor()

    query = f"DELETE FROM {table} WHERE id = ?"
    cursor.execute(query, (record_id,))

    conn.commit()
    conn.close()
    print(f"🗑️ Registro {record_id} eliminado de {table}")
