import sqlite3
from datetime import datetime, timedelta

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



# --------------------------
# CRUD PARA USUARIOS
# --------------------------

def create_user(user_data: dict) -> int:
    """
    Crea un nuevo usuario con validaciones específicas
    """
    # Validaciones
    required_fields = ['first_name', 'last_name', 'email', 'password', 'role']
    for field in required_fields:
        if field not in user_data:
            raise ValueError(f"Campo requerido faltante: {field}")
    
    # Validar rol
    valid_roles = ['owner', 'client', 'admin']
    if user_data['role'] not in valid_roles:
        raise ValueError(f"Rol inválido. Debe ser uno de: {valid_roles}")
    
    # Validar género si se proporciona
    if 'gender' in user_data and user_data['gender']:
        valid_genders = ['male', 'female', 'other']
        if user_data['gender'] not in valid_genders:
            raise ValueError(f"Género inválido. Debe ser uno de: {valid_genders}")
    
    # Validar formato de email básico
    if '@' not in user_data['email']:
        raise ValueError("Formato de email inválido")
    
    try:
        return insert('users', user_data)
    except sqlite3.IntegrityError as e:
        if "UNIQUE constraint failed: users.email" in str(e):
            raise ValueError("El email ya existe en la base de datos")
        raise e

def get_user_by_id(user_id: int) -> dict:
    """Obtiene un usuario por ID"""
    user = get_by_id('users', user_id)
    if user:
        # Convertir tupla a diccionario con nombres de columnas
        columns = ['id', 'remote_id', 'first_name', 'last_name', 'email', 'password', 
                  'role', 'id_document_number', 'phone', 'city', 'gender', 
                  'created_at', 'status']
        return dict(zip(columns, user))
    return None

def get_user_by_email(email: str) -> dict:
    """Obtiene un usuario por email"""
    conn = get_connection()
    cursor = conn.cursor()
    
    query = "SELECT * FROM users WHERE email = ?"
    cursor.execute(query, (email,))
    user = cursor.fetchone()
    
    conn.close()
    
    if user:
        columns = ['id', 'remote_id', 'first_name', 'last_name', 'email', 'password', 
                  'role', 'id_document_number', 'phone', 'city', 'gender', 
                  'created_at', 'status']
        return dict(zip(columns, user))
    return None

def get_all_users() -> list:
    """Obtiene todos los usuarios"""
    users = get_all('users')
    columns = ['id', 'remote_id', 'first_name', 'last_name', 'email', 'password', 
              'role', 'id_document_number', 'phone', 'city', 'gender', 
              'created_at', 'status']
    
    return [dict(zip(columns, user)) for user in users]

def update_user(user_id: int, update_data: dict) -> bool:
    """
    Actualiza un usuario con validaciones
    """
    # Validar rol si se está actualizando
    if 'role' in update_data:
        valid_roles = ['owner', 'client', 'admin']
        if update_data['role'] not in valid_roles:
            raise ValueError(f"Rol inválido. Debe ser uno de: {valid_roles}")
    
    # Validar género si se está actualizando
    if 'gender' in update_data and update_data['gender']:
        valid_genders = ['male', 'female', 'other']
        if update_data['gender'] not in valid_genders:
            raise ValueError(f"Género inválido. Debe ser uno de: {valid_genders}")
    
    try:
        update('users', user_id, update_data)
        return True
    except sqlite3.IntegrityError as e:
        if "UNIQUE constraint failed: users.email" in str(e):
            raise ValueError("El email ya existe en la base de datos")
        raise e

def delete_user(user_id: int) -> bool:
    """Elimina un usuario"""
    delete('users', user_id)
    return True

def deactivate_user(user_id: int) -> bool:
    """Desactiva un usuario (borrado lógico)"""
    return update_user(user_id, {'status': 'inactive'})

def activate_user(user_id: int) -> bool:
    """Reactiva un usuario"""
    return update_user(user_id, {'status': 'active'})

def get_users_by_role(role: str) -> list:
    """Obtiene usuarios por rol"""
    conn = get_connection()
    cursor = conn.cursor()
    
    query = "SELECT * FROM users WHERE role = ? ORDER BY created_at DESC"
    cursor.execute(query, (role,))
    users = cursor.fetchall()
    
    conn.close()
    
    columns = ['id', 'remote_id', 'first_name', 'last_name', 'email', 'password', 
              'role', 'id_document_number', 'phone', 'city', 'gender', 
              'created_at', 'status']
    
    return [dict(zip(columns, user)) for user in users]

def get_active_users() -> list:
    """Obtiene usuarios activos"""
    conn = get_connection()
    cursor = conn.cursor()
    
    query = "SELECT * FROM users WHERE status = 'active' ORDER BY created_at DESC"
    cursor.execute(query)
    users = cursor.fetchall()
    
    conn.close()
    
    columns = ['id', 'remote_id', 'first_name', 'last_name', 'email', 'password', 
              'role', 'id_document_number', 'phone', 'city', 'gender', 
              'created_at', 'status']
    
    return [dict(zip(columns, user)) for user in users]


# --------------------------
# Funciones específicas para Machines
# --------------------------

def create_machine(machine_data: dict) -> int:
    """
    Crea una nueva máquina con validaciones específicas
    """
    # Validaciones
    required_fields = ['user_id', 'name', 'status']
    for field in required_fields:
        if field not in machine_data:
            raise ValueError(f"Campo requerido faltante: {field}")
    
    # Validar status
    valid_statuses = ['available', 'active', 'inactive']
    if machine_data['status'] not in valid_statuses:
        raise ValueError(f"Status inválido. Debe ser uno de: {valid_statuses}")
    
    # Validar que el user_id existe
    user = get_user_by_id(machine_data['user_id'])
    if not user:
        raise ValueError("El user_id no existe en la base de datos")
    
    # Validar valores numéricos
    numeric_fields = ['max_water', 'current_level', 'price', 'filter_active_carbon', 
                     'filter_sand_and_gravel', 'filter_zeolite', 
                     'filter_reverse_osmosis_membrane', 'filter_mineral_layer']
    
    for field in numeric_fields:
        if field in machine_data and machine_data[field] is not None:
            try:
                machine_data[field] = float(machine_data[field])
            except (ValueError, TypeError):
                raise ValueError(f"El campo {field} debe ser un número válido")
    
    try:
        return insert('machines', machine_data)
    except sqlite3.IntegrityError as e:
        if "FOREIGN KEY constraint failed" in str(e):
            raise ValueError("El user_id no existe en la base de datos")
        raise e

def get_machine_by_id(machine_id: int) -> dict:
    """Obtiene una máquina por ID"""
    machine = get_by_id('machines', machine_id)
    if machine:
        columns = ['id', 'remote_id', 'user_id', 'name', 'location', 'status', 
                  'max_water', 'current_level', 'price', 'filter_active_carbon',
                  'filter_sand_and_gravel', 'filter_zeolite', 
                  'filter_reverse_osmosis_membrane', 'filter_mineral_layer']
        return dict(zip(columns, machine))
    return None

def get_all_machines() -> list:
    """Obtiene todas las máquinas"""
    machines = get_all('machines')
    columns = ['id', 'remote_id', 'user_id', 'name', 'location', 'status', 
              'max_water', 'current_level', 'price', 'filter_active_carbon',
              'filter_sand_and_gravel', 'filter_zeolite', 
              'filter_reverse_osmosis_membrane', 'filter_mineral_layer']
    
    return [dict(zip(columns, machine)) for machine in machines]

def get_machines_by_user(user_id: int) -> list:
    """Obtiene todas las máquinas de un usuario específico"""
    conn = get_connection()
    cursor = conn.cursor()
    
    query = "SELECT * FROM machines WHERE user_id = ? ORDER BY name"
    cursor.execute(query, (user_id,))
    machines = cursor.fetchall()
    
    conn.close()
    
    columns = ['id', 'remote_id', 'user_id', 'name', 'location', 'status', 
              'max_water', 'current_level', 'price', 'filter_active_carbon',
              'filter_sand_and_gravel', 'filter_zeolite', 
              'filter_reverse_osmosis_membrane', 'filter_mineral_layer']
    
    return [dict(zip(columns, machine)) for machine in machines]

def get_machines_by_status(status: str) -> list:
    """Obtiene máquinas por status"""
    valid_statuses = ['available', 'active', 'inactive']
    if status not in valid_statuses:
        raise ValueError(f"Status inválido. Debe ser uno de: {valid_statuses}")
    
    conn = get_connection()
    cursor = conn.cursor()
    
    query = "SELECT * FROM machines WHERE status = ? ORDER BY name"
    cursor.execute(query, (status,))
    machines = cursor.fetchall()
    
    conn.close()
    
    columns = ['id', 'remote_id', 'user_id', 'name', 'location', 'status', 
              'max_water', 'current_level', 'price', 'filter_active_carbon',
              'filter_sand_and_gravel', 'filter_zeolite', 
              'filter_reverse_osmosis_membrane', 'filter_mineral_layer']
    
    return [dict(zip(columns, machine)) for machine in machines]

def update_machine(machine_id: int, update_data: dict) -> bool:
    """
    Actualiza una máquina con validaciones
    """
    # Validar status si se está actualizando
    if 'status' in update_data:
        valid_statuses = ['available', 'active', 'inactive']
        if update_data['status'] not in valid_statuses:
            raise ValueError(f"Status inválido. Debe ser uno de: {valid_statuses}")
    
    # Validar user_id si se está actualizando
    if 'user_id' in update_data:
        user = get_user_by_id(update_data['user_id'])
        if not user:
            raise ValueError("El user_id no existe en la base de datos")
    
    # Validar valores numéricos
    numeric_fields = ['max_water', 'current_level', 'price', 'filter_active_carbon', 
                     'filter_sand_and_gravel', 'filter_zeolite', 
                     'filter_reverse_osmosis_membrane', 'filter_mineral_layer']
    
    for field in numeric_fields:
        if field in update_data and update_data[field] is not None:
            try:
                update_data[field] = float(update_data[field])
            except (ValueError, TypeError):
                raise ValueError(f"El campo {field} debe ser un número válido")
    
    try:
        update('machines', machine_id, update_data)
        return True
    except sqlite3.IntegrityError as e:
        if "FOREIGN KEY constraint failed" in str(e):
            raise ValueError("El user_id no existe en la base de datos")
        raise e

def delete_machine(machine_id: int) -> bool:
    """Elimina una máquina"""
    delete('machines', machine_id)
    return True

def update_machine_status(machine_id: int, status: str) -> bool:
    """Actualiza solo el status de una máquina"""
    valid_statuses = ['available', 'active', 'inactive']
    if status not in valid_statuses:
        raise ValueError(f"Status inválido. Debe ser uno de: {valid_statuses}")
    
    return update_machine(machine_id, {'status': status})

def update_machine_filters(machine_id: int, filters_data: dict) -> bool:
    """
    Actualiza los filtros de una máquina
    """
    valid_filters = [
        'filter_active_carbon', 'filter_sand_and_gravel', 'filter_zeolite',
        'filter_reverse_osmosis_membrane', 'filter_mineral_layer'
    ]
    
    # Validar que solo se envíen campos de filtros válidos
    for key in filters_data.keys():
        if key not in valid_filters:
            raise ValueError(f"Filtro inválido: {key}")
    
    # Validar valores numéricos
    for key, value in filters_data.items():
        try:
            filters_data[key] = float(value)
        except (ValueError, TypeError):
            raise ValueError(f"El campo {key} debe ser un número válido")
    
    return update_machine(machine_id, filters_data)

def get_machines_with_low_filters(threshold: float = 20.0) -> list:
    """
    Obtiene máquinas con filtros por debajo del threshold
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    query = """
    SELECT * FROM machines 
    WHERE filter_active_carbon < ? 
       OR filter_sand_and_gravel < ? 
       OR filter_zeolite < ? 
       OR filter_reverse_osmosis_membrane < ? 
       OR filter_mineral_layer < ?
    ORDER BY name
    """
    
    cursor.execute(query, (threshold, threshold, threshold, threshold, threshold))
    machines = cursor.fetchall()
    
    conn.close()
    
    columns = ['id', 'remote_id', 'user_id', 'name', 'location', 'status', 
              'max_water', 'current_level', 'price', 'filter_active_carbon',
              'filter_sand_and_gravel', 'filter_zeolite', 
              'filter_reverse_osmosis_membrane', 'filter_mineral_layer']
    
    return [dict(zip(columns, machine)) for machine in machines]

def update_machine_water_level(machine_id: int, current_level: float) -> bool:
    """Actualiza el nivel actual de agua de una máquina"""
    try:
        current_level = float(current_level)
    except (ValueError, TypeError):
        raise ValueError("El nivel de agua debe ser un número válido")
    
    return update_machine(machine_id, {'current_level': current_level})


# --------------------------
# Funciones específicas para Payments (Actualizadas)
# --------------------------

def create_payment(payment_data: dict) -> int:
    """
    Crea un nuevo pago con validaciones específicas
    """
    # Validaciones
    required_fields = ['date', 'amount', 'user_id']
    for field in required_fields:
        if field not in payment_data:
            raise ValueError(f"Campo requerido faltante: {field}")
    
    # Validar payment_method si se proporciona
    if 'payment_method' in payment_data and payment_data['payment_method']:
        valid_methods = ['bank_transfer', 'cash', 'card']
        if payment_data['payment_method'] not in valid_methods:
            raise ValueError(f"Método de pago inválido. Debe ser uno de: {valid_methods}")
    
    # Validar que el user_id existe
    user = get_user_by_id(payment_data['user_id'])
    if not user:
        raise ValueError("El user_id no existe en la base de datos")
    
    # Validar valores numéricos
    numeric_fields = ['amount', 'recharge']
    for field in numeric_fields:
        if field in payment_data and payment_data[field] is not None:
            try:
                payment_data[field] = float(payment_data[field])
                if payment_data[field] < 0:
                    raise ValueError(f"El campo {field} no puede ser negativo")
            except (ValueError, TypeError):
                raise ValueError(f"El campo {field} debe ser un número válido")
    
    try:
        return insert('payments', payment_data)
    except sqlite3.IntegrityError as e:
        if "FOREIGN KEY constraint failed" in str(e):
            raise ValueError("El user_id no existe en la base de datos")
        raise e

def get_payment_by_id(payment_id: int) -> dict:
    """Obtiene un pago por ID con información del usuario"""
    conn = get_connection()
    cursor = conn.cursor()
    
    query = """
    SELECT p.*, u.first_name, u.last_name, u.email 
    FROM payments p
    LEFT JOIN users u ON p.user_id = u.id
    WHERE p.id = ?
    """
    cursor.execute(query, (payment_id,))
    payment = cursor.fetchone()
    
    conn.close()
    
    if payment:
        columns = ['id', 'remote_id', 'date', 'payment_method', 'bank', 
                  'reference_code', 'amount', 'receipt', 'user_id', 'recharge',
                  'user_first_name', 'user_last_name', 'user_email']
        return dict(zip(columns, payment))
    return None

def get_all_payments() -> list:
    """Obtiene todos los pagos con información de usuario"""
    conn = get_connection()
    cursor = conn.cursor()
    
    query = """
    SELECT p.*, u.first_name, u.last_name, u.email 
    FROM payments p
    LEFT JOIN users u ON p.user_id = u.id
    ORDER BY p.date DESC
    """
    cursor.execute(query)
    payments = cursor.fetchall()
    
    conn.close()
    
    columns = ['id', 'remote_id', 'date', 'payment_method', 'bank', 
              'reference_code', 'amount', 'receipt', 'user_id', 'recharge',
              'user_first_name', 'user_last_name', 'user_email']
    
    return [dict(zip(columns, payment)) for payment in payments]

def get_payments_by_user(user_id: int) -> list:
    """Obtiene todos los pagos de un usuario específico"""
    conn = get_connection()
    cursor = conn.cursor()
    
    query = """
    SELECT p.*, u.first_name, u.last_name, u.email 
    FROM payments p
    LEFT JOIN users u ON p.user_id = u.id
    WHERE p.user_id = ? 
    ORDER BY p.date DESC
    """
    cursor.execute(query, (user_id,))
    payments = cursor.fetchall()
    
    conn.close()
    
    columns = ['id', 'remote_id', 'date', 'payment_method', 'bank', 
              'reference_code', 'amount', 'receipt', 'user_id', 'recharge',
              'user_first_name', 'user_last_name', 'user_email']
    
    return [dict(zip(columns, payment)) for payment in payments]

def get_payments_by_method(payment_method: str) -> list:
    """Obtiene pagos por método de pago"""
    valid_methods = ['bank_transfer', 'cash', 'card']
    if payment_method not in valid_methods:
        raise ValueError(f"Método de pago inválido. Debe ser uno de: {valid_methods}")
    
    conn = get_connection()
    cursor = conn.cursor()
    
    query = """
    SELECT p.*, u.first_name, u.last_name, u.email 
    FROM payments p
    LEFT JOIN users u ON p.user_id = u.id
    WHERE p.payment_method = ? 
    ORDER BY p.date DESC
    """
    cursor.execute(query, (payment_method,))
    payments = cursor.fetchall()
    
    conn.close()
    
    columns = ['id', 'remote_id', 'date', 'payment_method', 'bank', 
              'reference_code', 'amount', 'receipt', 'user_id', 'recharge',
              'user_first_name', 'user_last_name', 'user_email']
    
    return [dict(zip(columns, payment)) for payment in payments]

def get_payments_by_date_range(start_date: str, end_date: str) -> list:
    """Obtiene pagos dentro de un rango de fechas"""
    conn = get_connection()
    cursor = conn.cursor()
    
    query = """
    SELECT p.*, u.first_name, u.last_name, u.email 
    FROM payments p
    LEFT JOIN users u ON p.user_id = u.id
    WHERE p.date BETWEEN ? AND ? 
    ORDER BY p.date DESC
    """
    cursor.execute(query, (start_date, end_date))
    payments = cursor.fetchall()
    
    conn.close()
    
    columns = ['id', 'remote_id', 'date', 'payment_method', 'bank', 
              'reference_code', 'amount', 'receipt', 'user_id', 'recharge',
              'user_first_name', 'user_last_name', 'user_email']
    
    return [dict(zip(columns, payment)) for payment in payments]

def update_payment(payment_id: int, update_data: dict) -> bool:
    """
    Actualiza un pago con validaciones
    """
    # Validar payment_method si se está actualizando
    if 'payment_method' in update_data and update_data['payment_method']:
        valid_methods = ['bank_transfer', 'cash', 'card']
        if update_data['payment_method'] not in valid_methods:
            raise ValueError(f"Método de pago inválido. Debe ser uno de: {valid_methods}")
    
    # Validar user_id si se está actualizando
    if 'user_id' in update_data:
        user = get_user_by_id(update_data['user_id'])
        if not user:
            raise ValueError("El user_id no existe en la base de datos")
    
    # Validar valores numéricos
    numeric_fields = ['amount', 'recharge']
    for field in numeric_fields:
        if field in update_data and update_data[field] is not None:
            try:
                update_data[field] = float(update_data[field])
                if update_data[field] < 0:
                    raise ValueError(f"El campo {field} no puede ser negativo")
            except (ValueError, TypeError):
                raise ValueError(f"El campo {field} debe ser un número válido")
    
    try:
        update('payments', payment_id, update_data)
        return True
    except sqlite3.IntegrityError as e:
        if "FOREIGN KEY constraint failed" in str(e):
            raise ValueError("El user_id no existe en la base de datos")
        raise e

def delete_payment(payment_id: int) -> bool:
    """
    Elimina un pago
    Nota: Si hay sales asociadas, se deben manejar con CASCADE o manualmente
    """
    # Primero verificar si hay sales asociadas
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM sales WHERE payment_id = ?", (payment_id,))
    sales_count = cursor.fetchone()[0]
    conn.close()
    
    if sales_count > 0:
        raise ValueError(f"No se puede eliminar el pago. Tiene {sales_count} ventas asociadas.")
    
    delete('payments', payment_id)
    return True

def get_total_payments_amount(user_id: int = None) -> float:
    """
    Obtiene el monto total de pagos
    :param user_id: Si se especifica, obtiene el total para un usuario específico
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    if user_id:
        query = "SELECT SUM(amount) as total FROM payments WHERE user_id = ?"
        cursor.execute(query, (user_id,))
    else:
        query = "SELECT SUM(amount) as total FROM payments"
        cursor.execute(query)
    
    result = cursor.fetchone()
    conn.close()
    
    return result[0] if result and result[0] is not None else 0.0

def get_total_recharge_amount(user_id: int = None) -> float:
    """
    Obtiene el monto total de recargas
    :param user_id: Si se especifica, obtiene el total para un usuario específico
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    if user_id:
        query = "SELECT SUM(recharge) as total FROM payments WHERE user_id = ? AND recharge IS NOT NULL"
        cursor.execute(query, (user_id,))
    else:
        query = "SELECT SUM(recharge) as total FROM payments WHERE recharge IS NOT NULL"
        cursor.execute(query)
    
    result = cursor.fetchone()
    conn.close()
    
    return result[0] if result and result[0] is not None else 0.0

def get_payment_stats_by_method() -> dict:
    """Obtiene estadísticas de pagos por método de pago"""
    conn = get_connection()
    cursor = conn.cursor()
    
    query = """
    SELECT payment_method, COUNT(*) as count, SUM(amount) as total_amount
    FROM payments 
    WHERE payment_method IS NOT NULL
    GROUP BY payment_method
    """
    
    cursor.execute(query)
    results = cursor.fetchall()
    conn.close()
    
    stats = {}
    for row in results:
        stats[row[0]] = {
            'count': row[1],
            'total_amount': row[2] if row[2] else 0.0
        }
    
    return stats

def get_recent_payments(limit: int = 10) -> list:
    """Obtiene los pagos más recientes con información de usuario"""
    conn = get_connection()
    cursor = conn.cursor()
    
    query = """
    SELECT p.*, u.first_name, u.last_name, u.email 
    FROM payments p
    LEFT JOIN users u ON p.user_id = u.id
    ORDER BY p.date DESC LIMIT ?
    """
    cursor.execute(query, (limit,))
    payments = cursor.fetchall()
    
    conn.close()
    
    columns = ['id', 'remote_id', 'date', 'payment_method', 'bank', 
              'reference_code', 'amount', 'receipt', 'user_id', 'recharge',
              'user_first_name', 'user_last_name', 'user_email']
    
    return [dict(zip(columns, payment)) for payment in payments]

def get_payments_with_sales_count() -> list:
    """
    Obtiene pagos con el conteo de ventas asociadas
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    query = """
    SELECT p.*, u.first_name, u.last_name, u.email,
           COUNT(s.id) as sales_count,
           COALESCE(SUM(s.subtotal), 0) as sales_total
    FROM payments p
    LEFT JOIN users u ON p.user_id = u.id
    LEFT JOIN sales s ON p.id = s.payment_id
    GROUP BY p.id
    ORDER BY p.date DESC
    """
    
    cursor.execute(query)
    results = cursor.fetchall()
    conn.close()
    
    columns = ['id', 'remote_id', 'date', 'payment_method', 'bank', 
              'reference_code', 'amount', 'receipt', 'user_id', 'recharge',
              'user_first_name', 'user_last_name', 'user_email',
              'sales_count', 'sales_total']
    
    return [dict(zip(columns, row)) for row in results]


# --------------------------
# Funciones específicas para Sales
# --------------------------

def create_sale(sale_data: dict) -> int:
    """
    Crea una nueva venta con validaciones específicas
    """
    # Validaciones
    required_fields = ['date', 'product', 'price', 'user_id']
    for field in required_fields:
        if field not in sale_data:
            raise ValueError(f"Campo requerido faltante: {field}")
    
    # Validar valores numéricos
    numeric_fields = ['price', 'quantity', 'subtotal']
    for field in numeric_fields:
        if field in sale_data and sale_data[field] is not None:
            try:
                sale_data[field] = float(sale_data[field])
                if sale_data[field] < 0:
                    raise ValueError(f"El campo {field} no puede ser negativo")
            except (ValueError, TypeError):
                raise ValueError(f"El campo {field} debe ser un número válido")
    
    # Calcular subtotal si no se proporciona
    if 'subtotal' not in sale_data:
        quantity = sale_data.get('quantity', 1)
        sale_data['subtotal'] = sale_data['price'] * quantity
    
    # Validar que el user_id existe
    user = get_user_by_id(sale_data['user_id'])
    if not user:
        raise ValueError("El user_id no existe en la base de datos")
    
    # Validar que el machine_id existe si se proporciona
    if 'machine_id' in sale_data and sale_data['machine_id']:
        machine = get_machine_by_id(sale_data['machine_id'])
        if not machine:
            raise ValueError("El machine_id no existe en la base de datos")
    
    # Validar que el payment_id existe si se proporciona
    if 'payment_id' in sale_data and sale_data['payment_id']:
        payment = get_payment_by_id(sale_data['payment_id'])
        if not payment:
            raise ValueError("El payment_id no existe en la base de datos")
    
    try:
        return insert('sales', sale_data)
    except sqlite3.IntegrityError as e:
        if "FOREIGN KEY constraint failed" in str(e):
            raise ValueError("Error de clave foránea: user_id, machine_id o payment_id no existen")
        raise e

def get_sale_by_id(sale_id: int) -> dict:
    """Obtiene una venta por ID con información relacionada"""
    conn = get_connection()
    cursor = conn.cursor()
    
    query = """
    SELECT s.*, 
           u.first_name as user_first_name, u.last_name as user_last_name,
           m.name as machine_name, m.location as machine_location,
           p.payment_method, p.amount as payment_amount
    FROM sales s
    LEFT JOIN users u ON s.user_id = u.id
    LEFT JOIN machines m ON s.machine_id = m.id
    LEFT JOIN payments p ON s.payment_id = p.id
    WHERE s.id = ?
    """
    cursor.execute(query, (sale_id,))
    sale = cursor.fetchone()
    
    conn.close()
    
    if sale:
        columns = ['id', 'remote_id', 'date', 'product', 'price', 'quantity', 
                  'subtotal', 'user_id', 'machine_id', 'payment_id',
                  'user_first_name', 'user_last_name', 
                  'machine_name', 'machine_location',
                  'payment_method', 'payment_amount']
        return dict(zip(columns, sale))
    return None

def get_all_sales() -> list:
    """Obtiene todas las ventas con información relacionada"""
    conn = get_connection()
    cursor = conn.cursor()
    
    query = """
    SELECT s.*, 
           u.first_name as user_first_name, u.last_name as user_last_name,
           m.name as machine_name, m.location as machine_location,
           p.payment_method, p.amount as payment_amount
    FROM sales s
    LEFT JOIN users u ON s.user_id = u.id
    LEFT JOIN machines m ON s.machine_id = m.id
    LEFT JOIN payments p ON s.payment_id = p.id
    ORDER BY s.date DESC
    """
    cursor.execute(query)
    sales = cursor.fetchall()
    
    conn.close()
    
    columns = ['id', 'remote_id', 'date', 'product', 'price', 'quantity', 
              'subtotal', 'user_id', 'machine_id', 'payment_id',
              'user_first_name', 'user_last_name', 
              'machine_name', 'machine_location',
              'payment_method', 'payment_amount']
    
    return [dict(zip(columns, sale)) for sale in sales]

def get_sales_by_user(user_id: int) -> list:
    """Obtiene todas las ventas de un usuario específico"""
    conn = get_connection()
    cursor = conn.cursor()
    
    query = """
    SELECT s.*, 
           u.first_name as user_first_name, u.last_name as user_last_name,
           m.name as machine_name, m.location as machine_location,
           p.payment_method, p.amount as payment_amount
    FROM sales s
    LEFT JOIN users u ON s.user_id = u.id
    LEFT JOIN machines m ON s.machine_id = m.id
    LEFT JOIN payments p ON s.payment_id = p.id
    WHERE s.user_id = ?
    ORDER BY s.date DESC
    """
    cursor.execute(query, (user_id,))
    sales = cursor.fetchall()
    
    conn.close()
    
    columns = ['id', 'remote_id', 'date', 'product', 'price', 'quantity', 
              'subtotal', 'user_id', 'machine_id', 'payment_id',
              'user_first_name', 'user_last_name', 
              'machine_name', 'machine_location',
              'payment_method', 'payment_amount']
    
    return [dict(zip(columns, sale)) for sale in sales]

def get_sales_by_machine(machine_id: int) -> list:
    """Obtiene todas las ventas de una máquina específica"""
    conn = get_connection()
    cursor = conn.cursor()
    
    query = """
    SELECT s.*, 
           u.first_name as user_first_name, u.last_name as user_last_name,
           m.name as machine_name, m.location as machine_location,
           p.payment_method, p.amount as payment_amount
    FROM sales s
    LEFT JOIN users u ON s.user_id = u.id
    LEFT JOIN machines m ON s.machine_id = m.id
    LEFT JOIN payments p ON s.payment_id = p.id
    WHERE s.machine_id = ?
    ORDER BY s.date DESC
    """
    cursor.execute(query, (machine_id,))
    sales = cursor.fetchall()
    
    conn.close()
    
    columns = ['id', 'remote_id', 'date', 'product', 'price', 'quantity', 
              'subtotal', 'user_id', 'machine_id', 'payment_id',
              'user_first_name', 'user_last_name', 
              'machine_name', 'machine_location',
              'payment_method', 'payment_amount']
    
    return [dict(zip(columns, sale)) for sale in sales]

def get_sales_by_payment(payment_id: int) -> list:
    """Obtiene todas las ventas de un pago específico"""
    conn = get_connection()
    cursor = conn.cursor()
    
    query = """
    SELECT s.*, 
           u.first_name as user_first_name, u.last_name as user_last_name,
           m.name as machine_name, m.location as machine_location,
           p.payment_method, p.amount as payment_amount
    FROM sales s
    LEFT JOIN users u ON s.user_id = u.id
    LEFT JOIN machines m ON s.machine_id = m.id
    LEFT JOIN payments p ON s.payment_id = p.id
    WHERE s.payment_id = ?
    ORDER BY s.date DESC
    """
    cursor.execute(query, (payment_id,))
    sales = cursor.fetchall()
    
    conn.close()
    
    columns = ['id', 'remote_id', 'date', 'product', 'price', 'quantity', 
              'subtotal', 'user_id', 'machine_id', 'payment_id',
              'user_first_name', 'user_last_name', 
              'machine_name', 'machine_location',
              'payment_method', 'payment_amount']
    
    return [dict(zip(columns, sale)) for sale in sales]

def get_sales_by_product(product_name: str) -> list:
    """Obtiene todas las ventas de un producto específico"""
    conn = get_connection()
    cursor = conn.cursor()
    
    query = """
    SELECT s.*, 
           u.first_name as user_first_name, u.last_name as user_last_name,
           m.name as machine_name, m.location as machine_location,
           p.payment_method, p.amount as payment_amount
    FROM sales s
    LEFT JOIN users u ON s.user_id = u.id
    LEFT JOIN machines m ON s.machine_id = m.id
    LEFT JOIN payments p ON s.payment_id = p.id
    WHERE s.product = ?
    ORDER BY s.date DESC
    """
    cursor.execute(query, (product_name,))
    sales = cursor.fetchall()
    
    conn.close()
    
    columns = ['id', 'remote_id', 'date', 'product', 'price', 'quantity', 
              'subtotal', 'user_id', 'machine_id', 'payment_id',
              'user_first_name', 'user_last_name', 
              'machine_name', 'machine_location',
              'payment_method', 'payment_amount']
    
    return [dict(zip(columns, sale)) for sale in sales]

def get_sales_by_date_range(start_date: str, end_date: str) -> list:
    """Obtiene ventas dentro de un rango de fechas"""
    conn = get_connection()
    cursor = conn.cursor()
    
    query = """
    SELECT s.*, 
           u.first_name as user_first_name, u.last_name as user_last_name,
           m.name as machine_name, m.location as machine_location,
           p.payment_method, p.amount as payment_amount
    FROM sales s
    LEFT JOIN users u ON s.user_id = u.id
    LEFT JOIN machines m ON s.machine_id = m.id
    LEFT JOIN payments p ON s.payment_id = p.id
    WHERE s.date BETWEEN ? AND ?
    ORDER BY s.date DESC
    """
    cursor.execute(query, (start_date, end_date))
    sales = cursor.fetchall()
    
    conn.close()
    
    columns = ['id', 'remote_id', 'date', 'product', 'price', 'quantity', 
              'subtotal', 'user_id', 'machine_id', 'payment_id',
              'user_first_name', 'user_last_name', 
              'machine_name', 'machine_location',
              'payment_method', 'payment_amount']
    
    return [dict(zip(columns, sale)) for sale in sales]

def update_sale(sale_id: int, update_data: dict) -> bool:
    """
    Actualiza una venta con validaciones
    """
    # Validar valores numéricos
    numeric_fields = ['price', 'quantity', 'subtotal']
    for field in numeric_fields:
        if field in update_data and update_data[field] is not None:
            try:
                update_data[field] = float(update_data[field])
                if update_data[field] < 0:
                    raise ValueError(f"El campo {field} no puede ser negativo")
            except (ValueError, TypeError):
                raise ValueError(f"El campo {field} debe ser un número válido")
    
    # Recalcular subtotal si se actualiza price o quantity
    if ('price' in update_data or 'quantity' in update_data) and 'subtotal' not in update_data:
        # Obtener la venta actual para los valores que no se están actualizando
        current_sale = get_sale_by_id(sale_id)
        if current_sale:
            new_price = update_data.get('price', current_sale['price'])
            new_quantity = update_data.get('quantity', current_sale['quantity'])
            update_data['subtotal'] = new_price * new_quantity
    
    # Validar que el user_id existe si se está actualizando
    if 'user_id' in update_data:
        user = get_user_by_id(update_data['user_id'])
        if not user:
            raise ValueError("El user_id no existe en la base de datos")
    
    # Validar que el machine_id existe si se está actualizando
    if 'machine_id' in update_data and update_data['machine_id']:
        machine = get_machine_by_id(update_data['machine_id'])
        if not machine:
            raise ValueError("El machine_id no existe en la base de datos")
    
    # Validar que el payment_id existe si se está actualizando
    if 'payment_id' in update_data and update_data['payment_id']:
        payment = get_payment_by_id(update_data['payment_id'])
        if not payment:
            raise ValueError("El payment_id no existe en la base de datos")
    
    try:
        update('sales', sale_id, update_data)
        return True
    except sqlite3.IntegrityError as e:
        if "FOREIGN KEY constraint failed" in str(e):
            raise ValueError("Error de clave foránea: user_id, machine_id o payment_id no existen")
        raise e

def delete_sale(sale_id: int) -> bool:
    """Elimina una venta"""
    delete('sales', sale_id)
    return True

def get_total_sales_amount(user_id: int = None, machine_id: int = None) -> float:
    """
    Obtiene el monto total de ventas
    :param user_id: Filtrar por usuario
    :param machine_id: Filtrar por máquina
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    if user_id and machine_id:
        query = "SELECT SUM(subtotal) as total FROM sales WHERE user_id = ? AND machine_id = ?"
        cursor.execute(query, (user_id, machine_id))
    elif user_id:
        query = "SELECT SUM(subtotal) as total FROM sales WHERE user_id = ?"
        cursor.execute(query, (user_id,))
    elif machine_id:
        query = "SELECT SUM(subtotal) as total FROM sales WHERE machine_id = ?"
        cursor.execute(query, (machine_id,))
    else:
        query = "SELECT SUM(subtotal) as total FROM sales"
        cursor.execute(query)
    
    result = cursor.fetchone()
    conn.close()
    
    return result[0] if result and result[0] is not None else 0.0

def get_total_quantity_sold(product_name: str = None) -> int:
    """
    Obtiene la cantidad total vendida de un producto
    :param product_name: Nombre del producto (opcional)
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    if product_name:
        query = "SELECT SUM(quantity) as total FROM sales WHERE product = ?"
        cursor.execute(query, (product_name,))
    else:
        query = "SELECT SUM(quantity) as total FROM sales"
        cursor.execute(query)
    
    result = cursor.fetchone()
    conn.close()
    
    return int(result[0]) if result and result[0] is not None else 0

def get_sales_stats_by_product() -> dict:
    """Obtiene estadísticas de ventas por producto"""
    conn = get_connection()
    cursor = conn.cursor()
    
    query = """
    SELECT product, 
           COUNT(*) as sales_count,
           SUM(quantity) as total_quantity,
           SUM(subtotal) as total_amount
    FROM sales 
    GROUP BY product
    ORDER BY total_amount DESC
    """
    
    cursor.execute(query)
    results = cursor.fetchall()
    conn.close()
    
    stats = {}
    for row in results:
        stats[row[0]] = {
            'sales_count': row[1],
            'total_quantity': row[2],
            'total_amount': row[3] if row[3] else 0.0
        }
    
    return stats

def get_recent_sales(limit: int = 10) -> list:
    """Obtiene las ventas más recientes"""
    conn = get_connection()
    cursor = conn.cursor()
    
    query = """
    SELECT s.*, 
           u.first_name as user_first_name, u.last_name as user_last_name,
           m.name as machine_name, m.location as machine_location,
           p.payment_method, p.amount as payment_amount
    FROM sales s
    LEFT JOIN users u ON s.user_id = u.id
    LEFT JOIN machines m ON s.machine_id = m.id
    LEFT JOIN payments p ON s.payment_id = p.id
    ORDER BY s.date DESC LIMIT ?
    """
    cursor.execute(query, (limit,))
    sales = cursor.fetchall()
    
    conn.close()
    
    columns = ['id', 'remote_id', 'date', 'product', 'price', 'quantity', 
              'subtotal', 'user_id', 'machine_id', 'payment_id',
              'user_first_name', 'user_last_name', 
              'machine_name', 'machine_location',
              'payment_method', 'payment_amount']
    
    return [dict(zip(columns, sale)) for sale in sales]

def create_sale_with_payment(sale_data: dict, payment_data: dict) -> dict:
    """
    Crea una venta y su pago asociado en una transacción
    Returns: {'sale_id': id, 'payment_id': id}
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        # Crear el pago primero
        cursor.execute('''
            INSERT INTO payments (remote_id, date, payment_method, bank, reference_code, 
                                amount, receipt, user_id, recharge)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            payment_data.get('remote_id'),
            payment_data['date'],
            payment_data.get('payment_method'),
            payment_data.get('bank'),
            payment_data.get('reference_code'),
            payment_data['amount'],
            payment_data.get('receipt'),
            payment_data['user_id'],
            payment_data.get('recharge')
        ))
        
        payment_id = cursor.lastrowid
        
        # Crear la venta linkeada al pago
        sale_data['payment_id'] = payment_id
        sale_data['subtotal'] = sale_data['price'] * sale_data.get('quantity', 1)
        
        cursor.execute('''
            INSERT INTO sales (remote_id, date, product, price, quantity, 
                             subtotal, user_id, machine_id, payment_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            sale_data.get('remote_id'),
            sale_data['date'],
            sale_data['product'],
            sale_data['price'],
            sale_data.get('quantity', 1),
            sale_data['subtotal'],
            sale_data['user_id'],
            sale_data.get('machine_id'),
            sale_data['payment_id']
        ))
        
        sale_id = cursor.lastrowid
        
        conn.commit()
        return {'sale_id': sale_id, 'payment_id': payment_id}
        
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()



# --------------------------
# Funciones específicas para Sales
# --------------------------

def create_sale(sale_data: dict) -> int:
    """
    Crea una nueva venta con validaciones específicas
    """
    # Validaciones
    required_fields = ['date', 'product', 'price', 'user_id']
    for field in required_fields:
        if field not in sale_data:
            raise ValueError(f"Campo requerido faltante: {field}")
    
    # Validar valores numéricos
    numeric_fields = ['price', 'quantity', 'subtotal']
    for field in numeric_fields:
        if field in sale_data and sale_data[field] is not None:
            try:
                sale_data[field] = float(sale_data[field])
                if sale_data[field] < 0:
                    raise ValueError(f"El campo {field} no puede ser negativo")
            except (ValueError, TypeError):
                raise ValueError(f"El campo {field} debe ser un número válido")
    
    # Calcular subtotal si no se proporciona
    if 'subtotal' not in sale_data:
        quantity = sale_data.get('quantity', 1)
        sale_data['subtotal'] = sale_data['price'] * quantity
    
    # Validar que el user_id existe
    user = get_user_by_id(sale_data['user_id'])
    if not user:
        raise ValueError("El user_id no existe en la base de datos")
    
    # Validar que el machine_id existe si se proporciona
    if 'machine_id' in sale_data and sale_data['machine_id']:
        machine = get_machine_by_id(sale_data['machine_id'])
        if not machine:
            raise ValueError("El machine_id no existe en la base de datos")
    
    # Validar que el payment_id existe si se proporciona
    if 'payment_id' in sale_data and sale_data['payment_id']:
        payment = get_payment_by_id(sale_data['payment_id'])
        if not payment:
            raise ValueError("El payment_id no existe en la base de datos")
    
    try:
        return insert('sales', sale_data)
    except sqlite3.IntegrityError as e:
        if "FOREIGN KEY constraint failed" in str(e):
            raise ValueError("Error de clave foránea: user_id, machine_id o payment_id no existen")
        raise e

def get_sale_by_id(sale_id: int) -> dict:
    """Obtiene una venta por ID con información relacionada"""
    conn = get_connection()
    cursor = conn.cursor()
    
    query = """
    SELECT s.*, 
           u.first_name as user_first_name, u.last_name as user_last_name,
           m.name as machine_name, m.location as machine_location,
           p.payment_method, p.amount as payment_amount
    FROM sales s
    LEFT JOIN users u ON s.user_id = u.id
    LEFT JOIN machines m ON s.machine_id = m.id
    LEFT JOIN payments p ON s.payment_id = p.id
    WHERE s.id = ?
    """
    cursor.execute(query, (sale_id,))
    sale = cursor.fetchone()
    
    conn.close()
    
    if sale:
        columns = ['id', 'remote_id', 'date', 'product', 'price', 'quantity', 
                  'subtotal', 'user_id', 'machine_id', 'payment_id',
                  'user_first_name', 'user_last_name', 
                  'machine_name', 'machine_location',
                  'payment_method', 'payment_amount']
        return dict(zip(columns, sale))
    return None

def get_all_sales() -> list:
    """Obtiene todas las ventas con información relacionada"""
    conn = get_connection()
    cursor = conn.cursor()
    
    query = """
    SELECT s.*, 
           u.first_name as user_first_name, u.last_name as user_last_name,
           m.name as machine_name, m.location as machine_location,
           p.payment_method, p.amount as payment_amount
    FROM sales s
    LEFT JOIN users u ON s.user_id = u.id
    LEFT JOIN machines m ON s.machine_id = m.id
    LEFT JOIN payments p ON s.payment_id = p.id
    ORDER BY s.date DESC
    """
    cursor.execute(query)
    sales = cursor.fetchall()
    
    conn.close()
    
    columns = ['id', 'remote_id', 'date', 'product', 'price', 'quantity', 
              'subtotal', 'user_id', 'machine_id', 'payment_id',
              'user_first_name', 'user_last_name', 
              'machine_name', 'machine_location',
              'payment_method', 'payment_amount']
    
    return [dict(zip(columns, sale)) for sale in sales]

def get_sales_by_user(user_id: int) -> list:
    """Obtiene todas las ventas de un usuario específico"""
    conn = get_connection()
    cursor = conn.cursor()
    
    query = """
    SELECT s.*, 
           u.first_name as user_first_name, u.last_name as user_last_name,
           m.name as machine_name, m.location as machine_location,
           p.payment_method, p.amount as payment_amount
    FROM sales s
    LEFT JOIN users u ON s.user_id = u.id
    LEFT JOIN machines m ON s.machine_id = m.id
    LEFT JOIN payments p ON s.payment_id = p.id
    WHERE s.user_id = ?
    ORDER BY s.date DESC
    """
    cursor.execute(query, (user_id,))
    sales = cursor.fetchall()
    
    conn.close()
    
    columns = ['id', 'remote_id', 'date', 'product', 'price', 'quantity', 
              'subtotal', 'user_id', 'machine_id', 'payment_id',
              'user_first_name', 'user_last_name', 
              'machine_name', 'machine_location',
              'payment_method', 'payment_amount']
    
    return [dict(zip(columns, sale)) for sale in sales]

def get_sales_by_machine(machine_id: int) -> list:
    """Obtiene todas las ventas de una máquina específica"""
    conn = get_connection()
    cursor = conn.cursor()
    
    query = """
    SELECT s.*, 
           u.first_name as user_first_name, u.last_name as user_last_name,
           m.name as machine_name, m.location as machine_location,
           p.payment_method, p.amount as payment_amount
    FROM sales s
    LEFT JOIN users u ON s.user_id = u.id
    LEFT JOIN machines m ON s.machine_id = m.id
    LEFT JOIN payments p ON s.payment_id = p.id
    WHERE s.machine_id = ?
    ORDER BY s.date DESC
    """
    cursor.execute(query, (machine_id,))
    sales = cursor.fetchall()
    
    conn.close()
    
    columns = ['id', 'remote_id', 'date', 'product', 'price', 'quantity', 
              'subtotal', 'user_id', 'machine_id', 'payment_id',
              'user_first_name', 'user_last_name', 
              'machine_name', 'machine_location',
              'payment_method', 'payment_amount']
    
    return [dict(zip(columns, sale)) for sale in sales]

def get_sales_by_payment(payment_id: int) -> list:
    """Obtiene todas las ventas de un pago específico"""
    conn = get_connection()
    cursor = conn.cursor()
    
    query = """
    SELECT s.*, 
           u.first_name as user_first_name, u.last_name as user_last_name,
           m.name as machine_name, m.location as machine_location,
           p.payment_method, p.amount as payment_amount
    FROM sales s
    LEFT JOIN users u ON s.user_id = u.id
    LEFT JOIN machines m ON s.machine_id = m.id
    LEFT JOIN payments p ON s.payment_id = p.id
    WHERE s.payment_id = ?
    ORDER BY s.date DESC
    """
    cursor.execute(query, (payment_id,))
    sales = cursor.fetchall()
    
    conn.close()
    
    columns = ['id', 'remote_id', 'date', 'product', 'price', 'quantity', 
              'subtotal', 'user_id', 'machine_id', 'payment_id',
              'user_first_name', 'user_last_name', 
              'machine_name', 'machine_location',
              'payment_method', 'payment_amount']
    
    return [dict(zip(columns, sale)) for sale in sales]

def get_sales_by_product(product_name: str) -> list:
    """Obtiene todas las ventas de un producto específico"""
    conn = get_connection()
    cursor = conn.cursor()
    
    query = """
    SELECT s.*, 
           u.first_name as user_first_name, u.last_name as user_last_name,
           m.name as machine_name, m.location as machine_location,
           p.payment_method, p.amount as payment_amount
    FROM sales s
    LEFT JOIN users u ON s.user_id = u.id
    LEFT JOIN machines m ON s.machine_id = m.id
    LEFT JOIN payments p ON s.payment_id = p.id
    WHERE s.product = ?
    ORDER BY s.date DESC
    """
    cursor.execute(query, (product_name,))
    sales = cursor.fetchall()
    
    conn.close()
    
    columns = ['id', 'remote_id', 'date', 'product', 'price', 'quantity', 
              'subtotal', 'user_id', 'machine_id', 'payment_id',
              'user_first_name', 'user_last_name', 
              'machine_name', 'machine_location',
              'payment_method', 'payment_amount']
    
    return [dict(zip(columns, sale)) for sale in sales]

def get_sales_by_date_range(start_date: str, end_date: str) -> list:
    """Obtiene ventas dentro de un rango de fechas"""
    conn = get_connection()
    cursor = conn.cursor()
    
    query = """
    SELECT s.*, 
           u.first_name as user_first_name, u.last_name as user_last_name,
           m.name as machine_name, m.location as machine_location,
           p.payment_method, p.amount as payment_amount
    FROM sales s
    LEFT JOIN users u ON s.user_id = u.id
    LEFT JOIN machines m ON s.machine_id = m.id
    LEFT JOIN payments p ON s.payment_id = p.id
    WHERE s.date BETWEEN ? AND ?
    ORDER BY s.date DESC
    """
    cursor.execute(query, (start_date, end_date))
    sales = cursor.fetchall()
    
    conn.close()
    
    columns = ['id', 'remote_id', 'date', 'product', 'price', 'quantity', 
              'subtotal', 'user_id', 'machine_id', 'payment_id',
              'user_first_name', 'user_last_name', 
              'machine_name', 'machine_location',
              'payment_method', 'payment_amount']
    
    return [dict(zip(columns, sale)) for sale in sales]

def update_sale(sale_id: int, update_data: dict) -> bool:
    """
    Actualiza una venta con validaciones
    """
    # Validar valores numéricos
    numeric_fields = ['price', 'quantity', 'subtotal']
    for field in numeric_fields:
        if field in update_data and update_data[field] is not None:
            try:
                update_data[field] = float(update_data[field])
                if update_data[field] < 0:
                    raise ValueError(f"El campo {field} no puede ser negativo")
            except (ValueError, TypeError):
                raise ValueError(f"El campo {field} debe ser un número válido")
    
    # Recalcular subtotal si se actualiza price o quantity
    if ('price' in update_data or 'quantity' in update_data) and 'subtotal' not in update_data:
        # Obtener la venta actual para los valores que no se están actualizando
        current_sale = get_sale_by_id(sale_id)
        if current_sale:
            new_price = update_data.get('price', current_sale['price'])
            new_quantity = update_data.get('quantity', current_sale['quantity'])
            update_data['subtotal'] = new_price * new_quantity
    
    # Validar que el user_id existe si se está actualizando
    if 'user_id' in update_data:
        user = get_user_by_id(update_data['user_id'])
        if not user:
            raise ValueError("El user_id no existe en la base de datos")
    
    # Validar que el machine_id existe si se está actualizando
    if 'machine_id' in update_data and update_data['machine_id']:
        machine = get_machine_by_id(update_data['machine_id'])
        if not machine:
            raise ValueError("El machine_id no existe en la base de datos")
    
    # Validar que el payment_id existe si se está actualizando
    if 'payment_id' in update_data and update_data['payment_id']:
        payment = get_payment_by_id(update_data['payment_id'])
        if not payment:
            raise ValueError("El payment_id no existe en la base de datos")
    
    try:
        update('sales', sale_id, update_data)
        return True
    except sqlite3.IntegrityError as e:
        if "FOREIGN KEY constraint failed" in str(e):
            raise ValueError("Error de clave foránea: user_id, machine_id o payment_id no existen")
        raise e

def delete_sale(sale_id: int) -> bool:
    """Elimina una venta"""
    delete('sales', sale_id)
    return True

def get_total_sales_amount(user_id: int = None, machine_id: int = None) -> float:
    """
    Obtiene el monto total de ventas
    :param user_id: Filtrar por usuario
    :param machine_id: Filtrar por máquina
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    if user_id and machine_id:
        query = "SELECT SUM(subtotal) as total FROM sales WHERE user_id = ? AND machine_id = ?"
        cursor.execute(query, (user_id, machine_id))
    elif user_id:
        query = "SELECT SUM(subtotal) as total FROM sales WHERE user_id = ?"
        cursor.execute(query, (user_id,))
    elif machine_id:
        query = "SELECT SUM(subtotal) as total FROM sales WHERE machine_id = ?"
        cursor.execute(query, (machine_id,))
    else:
        query = "SELECT SUM(subtotal) as total FROM sales"
        cursor.execute(query)
    
    result = cursor.fetchone()
    conn.close()
    
    return result[0] if result and result[0] is not None else 0.0

def get_total_quantity_sold(product_name: str = None) -> int:
    """
    Obtiene la cantidad total vendida de un producto
    :param product_name: Nombre del producto (opcional)
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    if product_name:
        query = "SELECT SUM(quantity) as total FROM sales WHERE product = ?"
        cursor.execute(query, (product_name,))
    else:
        query = "SELECT SUM(quantity) as total FROM sales"
        cursor.execute(query)
    
    result = cursor.fetchone()
    conn.close()
    
    return int(result[0]) if result and result[0] is not None else 0

def get_sales_stats_by_product() -> dict:
    """Obtiene estadísticas de ventas por producto"""
    conn = get_connection()
    cursor = conn.cursor()
    
    query = """
    SELECT product, 
           COUNT(*) as sales_count,
           SUM(quantity) as total_quantity,
           SUM(subtotal) as total_amount
    FROM sales 
    GROUP BY product
    ORDER BY total_amount DESC
    """
    
    cursor.execute(query)
    results = cursor.fetchall()
    conn.close()
    
    stats = {}
    for row in results:
        stats[row[0]] = {
            'sales_count': row[1],
            'total_quantity': row[2],
            'total_amount': row[3] if row[3] else 0.0
        }
    
    return stats

def get_recent_sales(limit: int = 10) -> list:
    """Obtiene las ventas más recientes"""
    conn = get_connection()
    cursor = conn.cursor()
    
    query = """
    SELECT s.*, 
           u.first_name as user_first_name, u.last_name as user_last_name,
           m.name as machine_name, m.location as machine_location,
           p.payment_method, p.amount as payment_amount
    FROM sales s
    LEFT JOIN users u ON s.user_id = u.id
    LEFT JOIN machines m ON s.machine_id = m.id
    LEFT JOIN payments p ON s.payment_id = p.id
    ORDER BY s.date DESC LIMIT ?
    """
    cursor.execute(query, (limit,))
    sales = cursor.fetchall()
    
    conn.close()
    
    columns = ['id', 'remote_id', 'date', 'product', 'price', 'quantity', 
              'subtotal', 'user_id', 'machine_id', 'payment_id',
              'user_first_name', 'user_last_name', 
              'machine_name', 'machine_location',
              'payment_method', 'payment_amount']
    
    return [dict(zip(columns, sale)) for sale in sales]

def create_sale_with_payment(sale_data: dict, payment_data: dict) -> dict:
    """
    Crea una venta y su pago asociado en una transacción
    Returns: {'sale_id': id, 'payment_id': id}
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        # Crear el pago primero
        cursor.execute('''
            INSERT INTO payments (remote_id, date, payment_method, bank, reference_code, 
                                amount, receipt, user_id, recharge)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            payment_data.get('remote_id'),
            payment_data['date'],
            payment_data.get('payment_method'),
            payment_data.get('bank'),
            payment_data.get('reference_code'),
            payment_data['amount'],
            payment_data.get('receipt'),
            payment_data['user_id'],
            payment_data.get('recharge')
        ))
        
        payment_id = cursor.lastrowid
        
        # Crear la venta linkeada al pago
        sale_data['payment_id'] = payment_id
        sale_data['subtotal'] = sale_data['price'] * sale_data.get('quantity', 1)
        
        cursor.execute('''
            INSERT INTO sales (remote_id, date, product, price, quantity, 
                             subtotal, user_id, machine_id, payment_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            sale_data.get('remote_id'),
            sale_data['date'],
            sale_data['product'],
            sale_data['price'],
            sale_data.get('quantity', 1),
            sale_data['subtotal'],
            sale_data['user_id'],
            sale_data.get('machine_id'),
            sale_data['payment_id']
        ))
        
        sale_id = cursor.lastrowid
        
        conn.commit()
        return {'sale_id': sale_id, 'payment_id': payment_id}
        
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()


# --------------------------
# Funciones específicas para Water Consumption History
# --------------------------

def create_water_consumption(consumption_data: dict) -> int:
    """
    Crea un nuevo registro de consumo de agua con validaciones
    """
    # Validaciones
    required_fields = ['date', 'consumption', 'recharge', 'balance']
    for field in required_fields:
        if field not in consumption_data:
            raise ValueError(f"Campo requerido faltante: {field}")
    
    # Validar valores numéricos
    numeric_fields = ['consumption', 'recharge', 'balance']
    for field in numeric_fields:
        if field in consumption_data and consumption_data[field] is not None:
            try:
                consumption_data[field] = float(consumption_data[field])
            except (ValueError, TypeError):
                raise ValueError(f"El campo {field} debe ser un número válido")
    
    try:
        return insert('water_consumption_history', consumption_data)
    except sqlite3.Error as e:
        raise ValueError(f"Error creando registro de consumo: {e}")

def get_water_consumption_by_id(record_id: int) -> dict:
    """Obtiene un registro de consumo por ID"""
    record = get_by_id('water_consumption_history', record_id)
    if record:
        columns = ['id', 'remote_id', 'date', 'consumption', 'recharge', 'balance']
        return dict(zip(columns, record))
    return None

def get_all_water_consumption() -> list:
    """Obtiene todos los registros de consumo"""
    records = get_all('water_consumption_history')
    columns = ['id', 'remote_id', 'date', 'consumption', 'recharge', 'balance']
    
    return [dict(zip(columns, record)) for record in records]

def get_water_consumption_by_date_range(start_date: str, end_date: str) -> list:
    """Obtiene registros de consumo dentro de un rango de fechas"""
    conn = get_connection()
    cursor = conn.cursor()
    
    query = "SELECT * FROM water_consumption_history WHERE date BETWEEN ? AND ? ORDER BY date DESC"
    cursor.execute(query, (start_date, end_date))
    records = cursor.fetchall()
    
    conn.close()
    
    columns = ['id', 'remote_id', 'date', 'consumption', 'recharge', 'balance']
    
    return [dict(zip(columns, record)) for record in records]

def get_water_consumption_by_month(year: int, month: int) -> list:
    """Obtiene registros de consumo de un mes específico"""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Formatear las fechas para el rango del mes
    start_date = f"{year:04d}-{month:02d}-01"
    if month == 12:
        end_date = f"{year+1:04d}-01-01"
    else:
        end_date = f"{year:04d}-{month+1:02d}-01"
    
    query = "SELECT * FROM water_consumption_history WHERE date >= ? AND date < ? ORDER BY date"
    cursor.execute(query, (start_date, end_date))
    records = cursor.fetchall()
    
    conn.close()
    
    columns = ['id', 'remote_id', 'date', 'consumption', 'recharge', 'balance']
    
    return [dict(zip(columns, record)) for record in records]

def update_water_consumption(record_id: int, update_data: dict) -> bool:
    """
    Actualiza un registro de consumo con validaciones
    """
    # Validar valores numéricos
    numeric_fields = ['consumption', 'recharge', 'balance']
    for field in numeric_fields:
        if field in update_data and update_data[field] is not None:
            try:
                update_data[field] = float(update_data[field])
            except (ValueError, TypeError):
                raise ValueError(f"El campo {field} debe ser un número válido")
    
    try:
        update('water_consumption_history', record_id, update_data)
        return True
    except sqlite3.Error as e:
        raise ValueError(f"Error actualizando registro de consumo: {e}")

def delete_water_consumption(record_id: int) -> bool:
    """Elimina un registro de consumo"""
    delete('water_consumption_history', record_id)
    return True

def get_total_consumption(start_date: str = None, end_date: str = None) -> float:
    """
    Obtiene el consumo total de agua en un período
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    if start_date and end_date:
        query = "SELECT SUM(consumption) FROM water_consumption_history WHERE date BETWEEN ? AND ?"
        cursor.execute(query, (start_date, end_date))
    elif start_date:
        query = "SELECT SUM(consumption) FROM water_consumption_history WHERE date >= ?"
        cursor.execute(query, (start_date,))
    elif end_date:
        query = "SELECT SUM(consumption) FROM water_consumption_history WHERE date <= ?"
        cursor.execute(query, (end_date,))
    else:
        query = "SELECT SUM(consumption) FROM water_consumption_history"
        cursor.execute(query)
    
    result = cursor.fetchone()
    conn.close()
    
    return result[0] if result and result[0] is not None else 0.0

def get_total_recharge(start_date: str = None, end_date: str = None) -> float:
    """
    Obtiene la recarga total en un período
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    if start_date and end_date:
        query = "SELECT SUM(recharge) FROM water_consumption_history WHERE date BETWEEN ? AND ?"
        cursor.execute(query, (start_date, end_date))
    elif start_date:
        query = "SELECT SUM(recharge) FROM water_consumption_history WHERE date >= ?"
        cursor.execute(query, (start_date,))
    elif end_date:
        query = "SELECT SUM(recharge) FROM water_consumption_history WHERE date <= ?"
        cursor.execute(query, (end_date,))
    else:
        query = "SELECT SUM(recharge) FROM water_consumption_history"
        cursor.execute(query)
    
    result = cursor.fetchone()
    conn.close()
    
    return result[0] if result and result[0] is not None else 0.0

def get_current_balance() -> float:
    """
    Obtiene el balance actual (último registro)
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    query = "SELECT balance FROM water_consumption_history ORDER BY date DESC, id DESC LIMIT 1"
    cursor.execute(query)
    result = cursor.fetchone()
    
    conn.close()
    
    return result[0] if result and result[0] is not None else 0.0

def get_consumption_stats_by_period(period: str = 'month') -> list:
    """
    Obtiene estadísticas de consumo por período (month, week, day)
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    if period == 'month':
        query = """
        SELECT 
            strftime('%Y-%m', date) as period,
            SUM(consumption) as total_consumption,
            SUM(recharge) as total_recharge,
            AVG(balance) as avg_balance
        FROM water_consumption_history 
        GROUP BY strftime('%Y-%m', date)
        ORDER BY period DESC
        """
    elif period == 'week':
        query = """
        SELECT 
            strftime('%Y-%W', date) as period,
            SUM(consumption) as total_consumption,
            SUM(recharge) as total_recharge,
            AVG(balance) as avg_balance
        FROM water_consumption_history 
        GROUP BY strftime('%Y-%W', date)
        ORDER BY period DESC
        """
    else:  # day
        query = """
        SELECT 
            date as period,
            SUM(consumption) as total_consumption,
            SUM(recharge) as total_recharge,
            AVG(balance) as avg_balance
        FROM water_consumption_history 
        GROUP BY date
        ORDER BY period DESC
        """
    
    cursor.execute(query)
    results = cursor.fetchall()
    conn.close()
    
    stats = []
    for row in results:
        stats.append({
            'period': row[0],
            'total_consumption': row[1] if row[1] else 0.0,
            'total_recharge': row[2] if row[2] else 0.0,
            'avg_balance': row[3] if row[3] else 0.0
        })
    
    return stats

def get_daily_consumption_average(days: int = 30) -> float:
    """
    Obtiene el consumo diario promedio de los últimos N días
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
    
    query = """
    SELECT AVG(daily_consumption) 
    FROM (
        SELECT date, SUM(consumption) as daily_consumption
        FROM water_consumption_history 
        WHERE date BETWEEN ? AND ?
        GROUP BY date
    )
    """
    
    cursor.execute(query, (start_date, end_date))
    result = cursor.fetchone()
    conn.close()
    
    return result[0] if result and result[0] is not None else 0.0

def get_consumption_trend(days: int = 30) -> list:
    """
    Obtiene la tendencia de consumo de los últimos N días
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
    
    query = """
    SELECT 
        date,
        SUM(consumption) as daily_consumption,
        SUM(recharge) as daily_recharge,
        AVG(balance) as daily_balance
    FROM water_consumption_history 
    WHERE date BETWEEN ? AND ?
    GROUP BY date
    ORDER BY date
    """
    
    cursor.execute(query, (start_date, end_date))
    results = cursor.fetchall()
    conn.close()
    
    trend = []
    for row in results:
        trend.append({
            'date': row[0],
            'consumption': row[1] if row[1] else 0.0,
            'recharge': row[2] if row[2] else 0.0,
            'balance': row[3] if row[3] else 0.0
        })
    
    return trend

def add_consumption_with_balance_calculation(consumption: float, recharge: float = 0) -> int:
    """
    Agrega un registro de consumo calculando automáticamente el balance
    basado en el último registro
    """
    # Obtener el último balance
    current_balance = get_current_balance()
    
    # Calcular nuevo balance
    new_balance = current_balance - consumption + recharge
    
    # Crear el nuevo registro
    consumption_data = {
        'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'consumption': consumption,
        'recharge': recharge,
        'balance': new_balance
    }
    
    return create_water_consumption(consumption_data)

def get_consumption_alerts(consumption_threshold: float = 100.0, balance_threshold: float = 50.0) -> list:
    """
    Obtiene alertas basadas en consumo alto o balance bajo
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    query = """
    SELECT * FROM water_consumption_history 
    WHERE consumption > ? OR balance < ?
    ORDER BY date DESC
    LIMIT 10
    """
    
    cursor.execute(query, (consumption_threshold, balance_threshold))
    records = cursor.fetchall()
    conn.close()
    
    columns = ['id', 'remote_id', 'date', 'consumption', 'recharge', 'balance']
    
    alerts = []
    for record in records:
        record_dict = dict(zip(columns, record))
        if record_dict['consumption'] > consumption_threshold:
            record_dict['alert_type'] = 'high_consumption'
            record_dict['alert_message'] = f"Consumo alto: {record_dict['consumption']}L"
        elif record_dict['balance'] < balance_threshold:
            record_dict['alert_type'] = 'low_balance'
            record_dict['alert_message'] = f"Balance bajo: {record_dict['balance']}L"
        
        alerts.append(record_dict)
    
    return alerts