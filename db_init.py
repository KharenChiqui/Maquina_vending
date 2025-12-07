import sqlite3
from controller import *
from datetime import datetime, timedelta

# Nombre del archivo donde se guardará la BD local
DB_NAME = "local.db"

def create_tables():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('DROP TABLE sales')

    # Ejecutamos cada CREATE TABLE
    cursor.executescript("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        remote_id TEXT,
        first_name TEXT NOT NULL,
        last_name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        role TEXT NOT NULL CHECK(role IN ('owner', 'client', 'admin')),
        id_document_number TEXT,
        phone TEXT,
        city TEXT,
        gender TEXT CHECK(gender IN ('male', 'female', 'other')),
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        status TEXT DEFAULT 'active'
    );

    CREATE TABLE IF NOT EXISTS machines (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        remote_id TEXT,
        user_id INTEGER,
        name TEXT NOT NULL,
        location TEXT,
        status TEXT NOT NULL CHECK(status IN ('available', 'active', 'inactive')),
        max_water REAL,
        current_level REAL,
        price REAL,
        filter_active_carbon REAL,
        filter_sand_and_gravel REAL,
        filter_zeolite REAL,
        filter_reverse_osmosis_membrane REAL,
        filter_mineral_layer REAL,
        FOREIGN KEY (user_id) REFERENCES users(id)
    );

    CREATE TABLE IF NOT EXISTS payments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        remote_id TEXT,
        date DATETIME NOT NULL,
        payment_method TEXT CHECK(payment_method IN ('bank_transfer','cash','card')),
        bank TEXT,
        reference_code TEXT,
        amount REAL NOT NULL,
        receipt TEXT,
        user_id INTEGER,
        recharge REAL,
        FOREIGN KEY (user_id) REFERENCES users(id)
    );

    CREATE TABLE IF NOT EXISTS sales (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        remote_id TEXT,
        date DATETIME NOT NULL,
        product TEXT NOT NULL,
        price REAL NOT NULL,
        quantity INTEGER NOT NULL DEFAULT 1,
        subtotal REAL NOT NULL,
        user_id INTEGER,
        machine_id INTEGER,
        payment_id INTEGER,
        FOREIGN KEY (user_id) REFERENCES users(id),
        FOREIGN KEY (machine_id) REFERENCES machines(id),
        FOREIGN KEY (payment_id) REFERENCES payments(id)
    );

    CREATE TABLE IF NOT EXISTS water_consumption_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        remote_id TEXT,
        date DATETIME NOT NULL,
        consumption REAL,
        recharge REAL,
        balance REAL
    );
    """)

    conn.commit()
    conn.close()
    print("✅ Tablas creadas correctamente en local.db")

def crud_users():
    # Ejemplo de creación de usuario
    try:
        new_user = {
            'first_name': 'María',
            'last_name': 'García',
            'email': 'maria@email.com',
            'password': 'secure_password_123',
            'role': 'client',
            'phone': '+34678901234',
            'city': 'Barcelona',
            'gender': 'female'
        }
        
        user_id = create_user(new_user)
        print(f"✅ Usuario creado con ID: {user_id}")
        
    except ValueError as e:
        print(f"❌ Error: {e}")
    
    # Obtener usuario por ID
    user = get_user_by_id(1)
    if user:
        print(f"👤 Usuario: {user['first_name']} {user['last_name']} - {user['email']}")
    
    # Obtener usuarios por rol
    clients = get_users_by_role('client')
    print(f"👥 Total clientes: {len(clients)}")
    
    # Actualizar usuario
    try:
        update_success = update_user(1, {'city': 'Valencia', 'phone': '+34666666666'})
        if update_success:
            print("✏️ Usuario actualizado")
    except ValueError as e:
        print(f"❌ Error al actualizar: {e}")
    
    # Obtener usuarios activos
    active_users = get_active_users()
    print(f"🟢 Usuarios activos: {len(active_users)}")
    
    # Desactivar usuario
    deactivate_user(1)
    print("⏸️ Usuario desactivado")

def crud_machines():
    """Demostración de las funciones de máquinas"""
    
    # Primero creamos un usuario de prueba si no existe
    try:
        user_data = {
            'first_name': 'Empresa',
            'last_name': 'Agua Pura',
            'email': 'empresa@aguapura.com',
            'password': 'password123',
            'role': 'owner',
            'phone': '+1234567890',
            'city': 'Ciudad'
        }
        user_id = create_user(user_data)
        print(f"✅ Usuario creado con ID: {user_id}")
    except ValueError as e:
        print(f"⚠️  {e}")
        # Si el usuario ya existe, obtenemos su ID
        user = get_user_by_email('empresa@aguapura.com')
        user_id = user['id']
        print(f"✅ Usuario existente con ID: {user_id}")
    
    # 1. Crear una nueva máquina
    try:
        machine_data = {
            'user_id': user_id,
            'name': 'Máquina Central',
            'location': 'Plaza Principal',
            'status': 'available',
            'max_water': 1000.0,
            'current_level': 750.5,
            'price': 0.50,
            'filter_active_carbon': 85.0,
            'filter_sand_and_gravel': 90.0,
            'filter_zeolite': 78.0,
            'filter_reverse_osmosis_membrane': 92.0,
            'filter_mineral_layer': 88.0
        }
        
        machine_id = create_machine(machine_data)
        print(f"✅ Máquina creada con ID: {machine_id}")
        
    except ValueError as e:
        print(f"❌ Error creando máquina: {e}")
        return
    
    # 2. Obtener máquina por ID
    machine = get_machine_by_id(machine_id)
    if machine:
        print(f"🔧 Máquina: {machine['name']} - Status: {machine['status']}")
        print(f"   Nivel de agua: {machine['current_level']}L / {machine['max_water']}L")
    
    # 3. Obtener máquinas por usuario
    user_machines = get_machines_by_user(user_id)
    print(f"👤 Máquinas del usuario {user_id}: {len(user_machines)}")
    
    # 4. Obtener máquinas disponibles
    available_machines = get_machines_by_status('available')
    print(f"🟢 Máquinas disponibles: {len(available_machines)}")
    
    # 5. Actualizar status de la máquina
    try:
        update_machine_status(machine_id, 'active')
        print("✏️ Status de máquina actualizado a 'active'")
    except ValueError as e:
        print(f"❌ Error actualizando status: {e}")
    
    # 6. Actualizar filtros
    try:
        new_filters = {
            'filter_active_carbon': 70.0,
            'filter_zeolite': 65.0
        }
        update_machine_filters(machine_id, new_filters)
        print("✏️ Filtros actualizados")
    except ValueError as e:
        print(f"❌ Error actualizando filtros: {e}")
    
    # 7. Verificar máquinas con filtros bajos
    low_filter_machines = get_machines_with_low_filters(30.0)
    print(f"⚠️  Máquinas con filtros bajos (<30%): {len(low_filter_machines)}")
    
    # 8. Obtener todas las máquinas
    all_machines = get_all_machines()
    print(f"📊 Total de máquinas en sistema: {len(all_machines)}")

def crud_payments():
    """Demostración de las funciones de pagos"""
    
    print("=== DEMOSTRACIÓN DE FUNCIONES PAYMENTS ===\n")
    
    # Obtener un usuario existente
    users = get_all_users()
    if not users:
        print("❌ No hay usuarios en la base de datos")
        return
    
    user = users[0]
    user_id = user['id']
    print(f"👤 Usando usuario: {user['first_name']} {user['last_name']} (ID: {user_id})")
    
    # 1. Crear un nuevo pago
    try:
        payment_data = {
            'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'payment_method': 'card',
            'amount': 45.50,
            'user_id': user_id,
            'recharge': 36.00,
            'bank': 'Visa',
            'reference_code': 'CARD-789012'
        }
        
        payment_id = create_payment(payment_data)
        print(f"✅ Pago creado con ID: {payment_id}")
        
    except ValueError as e:
        print(f"❌ Error creando pago: {e}")
        return
    
    # 2. Crear otro pago con método diferente
    try:
        payment_data2 = {
            'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'payment_method': 'bank_transfer',
            'bank': 'Banco Nacional',
            'reference_code': 'TRF-123456',
            'amount': 100.00,
            'user_id': user_id,
            'recharge': 80.0
        }
        
        payment_id2 = create_payment(payment_data2)
        print(f"✅ Segundo pago creado con ID: {payment_id2}")
        
    except ValueError as e:
        print(f"⚠️  Error creando segundo pago: {e}")
    
    # 3. Obtener pago por ID con información de usuario
    payment = get_payment_by_id(payment_id)
    if payment:
        print(f"\n💰 Pago ID {payment_id}:")
        print(f"   Monto: ${payment['amount']:.2f}")
        print(f"   Método: {payment['payment_method']}")
        print(f"   Recarga: ${payment['recharge']:.2f}" if payment['recharge'] else "   Sin recarga")
        print(f"   Usuario: {payment['user_first_name']} {payment['user_last_name']}")
        print(f"   Fecha: {payment['date']}")
    
    # 4. Obtener pagos por usuario
    user_payments = get_payments_by_user(user_id)
    print(f"\n📊 Total pagos del usuario: {len(user_payments)}")
    
    # 5. Obtener estadísticas por método de pago
    stats = get_payment_stats_by_method()
    print(f"\n📊 Estadísticas por método de pago:")
    for method, data in stats.items():
        print(f"   {method}: {data['count']} pagos, ${data['total_amount']:.2f}")
    
    # 6. Obtener totales
    total_amount = get_total_payments_amount()
    total_user_amount = get_total_payments_amount(user_id)
    total_recharge = get_total_recharge_amount(user_id)
    
    print(f"\n📈 Monto total de todos los pagos: ${total_amount:.2f}")
    print(f"📈 Monto total del usuario: ${total_user_amount:.2f}")
    print(f"🔋 Recarga total del usuario: ${total_recharge:.2f}")
    
    # 7. Pagos recientes
    recent_payments = get_recent_payments(3)
    print(f"\n🕒 Últimos 3 pagos:")
    for i, pay in enumerate(recent_payments, 1):
        print(f"   {i}. ${pay['amount']:.2f} - {pay['payment_method']} - {pay['date']}")
    
    # 8. Obtener pagos con conteo de ventas
    payments_with_sales = get_payments_with_sales_count()
    print(f"\n🧾 Pagos con ventas asociadas: {len(payments_with_sales)}")
    for pay in payments_with_sales[:2]:  # Mostrar solo 2
        print(f"   Pago ${pay['amount']:.2f}: {pay['sales_count']} ventas (${pay['sales_total']:.2f})")
    
    # 9. Actualizar un pago
    try:
        update_data = {
            'amount': 50.00,
            'recharge': 40.0,
            'reference_code': 'CARD-UPDATED-001'
        }
        success = update_payment(payment_id, update_data)
        if success:
            print(f"\n✏️ Pago {payment_id} actualizado correctamente")
    except ValueError as e:
        print(f"❌ Error actualizando pago: {e}")
    
    # 10. Intentar eliminar un pago (debería fallar si hay ventas asociadas)
    try:
        success = delete_payment(payment_id)
        if success:
            print(f"🗑️ Pago {payment_id} eliminado")
    except ValueError as e:
        print(f"⚠️  No se pudo eliminar: {e}")

def crud_sales():
    """Demostración de las funciones de ventas"""
    
    print("=== DEMOSTRACIÓN DE FUNCIONES SALES ===\n")
    
    # Obtener datos existentes
    users = get_all_users()
    machines = get_all_machines()
    
    if not users or not machines:
        print("❌ Se necesitan usuarios y máquinas para la demo")
        return
    
    user = users[0]
    machine = machines[0]
    
    print(f"👤 Usuario: {user['first_name']} {user['last_name']}")
    print(f"🔧 Máquina: {machine['name']} - {machine['location']}\n")
    
    # 1. Crear una nueva venta
    try:
        sale_data = {
            'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'product': 'Botellón 19L',
            'price': 2.50,
            'quantity': 3,
            'user_id': user['id'],
            'machine_id': machine['id']
            # payment_id se puede añadir después o crear junto con el pago
        }
        
        sale_id = create_sale(sale_data)
        print(f"✅ Venta creada con ID: {sale_id}")
        
    except ValueError as e:
        print(f"❌ Error creando venta: {e}")
        return
    
    # 2. Crear otra venta de diferente producto
    try:
        sale_data2 = {
            'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'product': 'Botellón 5L',
            'price': 1.00,
            'quantity': 2,
            'user_id': user['id'],
            'machine_id': machine['id']
        }
        
        sale_id2 = create_sale(sale_data2)
        print(f"✅ Segunda venta creada con ID: {sale_id2}")
        
    except ValueError as e:
        print(f"⚠️  Error creando segunda venta: {e}")
    
    # 3. Obtener venta por ID
    sale = get_sale_by_id(sale_id)
    if sale:
        print(f"\n🛒 Venta ID {sale_id}:")
        print(f"   Producto: {sale['product']}")
        print(f"   Cantidad: {sale['quantity']}")
        print(f"   Precio unitario: ${sale['price']:.2f}")
        print(f"   Subtotal: ${sale['subtotal']:.2f}")
        print(f"   Máquina: {sale['machine_name']}")
        print(f"   Fecha: {sale['date']}")
    
    # 4. Obtener ventas por usuario
    user_sales = get_sales_by_user(user['id'])
    print(f"\n📊 Total ventas del usuario: {len(user_sales)}")
    
    # 5. Obtener ventas por producto
    bottle_sales = get_sales_by_product('Botellón 19L')
    print(f"🍶 Ventas de Botellón 19L: {len(bottle_sales)}")
    
    # 6. Estadísticas por producto
    stats = get_sales_stats_by_product()
    print(f"\n📊 Estadísticas por producto:")
    for product, data in stats.items():
        print(f"   {product}: {data['total_quantity']} unidades, ${data['total_amount']:.2f}")
    
    # 7. Totales
    total_sales = get_total_sales_amount()
    user_total = get_total_sales_amount(user_id=user['id'])
    machine_total = get_total_sales_amount(machine_id=machine['id'])
    
    print(f"\n📈 Monto total de todas las ventas: ${total_sales:.2f}")
    print(f"📈 Monto total del usuario: ${user_total:.2f}")
    print(f"📈 Monto total de la máquina: ${machine_total:.2f}")
    
    # 8. Cantidad total vendida
    total_bottles = get_total_quantity_sold('Botellón 19L')
    print(f"🍶 Total Botellones 19L vendidos: {total_bottles}")
    
    # 9. Ventas recientes
    recent_sales = get_recent_sales(3)
    print(f"\n🕒 Últimas 3 ventas:")
    for i, sale in enumerate(recent_sales, 1):
        print(f"   {i}. {sale['product']} x{sale['quantity']} - ${sale['subtotal']:.2f}")
    
    # 10. Crear venta con pago asociado (transacción completa)
    try:
        sale_data3 = {
            'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'product': 'Botellón 19L',
            'price': 2.50,
            'quantity': 5,
            'user_id': user['id'],
            'machine_id': machine['id']
        }
        
        payment_data = {
            'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'payment_method': 'card',
            'amount': 12.50,  # 5 * 2.50
            'user_id': user['id'],
            'recharge': 10.00
        }
        
        result = create_sale_with_payment(sale_data3, payment_data)
        print(f"\n💳 Venta con pago creada:")
        print(f"   Sale ID: {result['sale_id']}")
        print(f"   Payment ID: {result['payment_id']}")
        
    except Exception as e:
        print(f"❌ Error creando venta con pago: {e}")
    
    # 11. Actualizar una venta
    try:
        update_data = {
            'quantity': 4,
            'price': 2.75  # Se recalculará automáticamente el subtotal
        }
        success = update_sale(sale_id, update_data)
        if success:
            print(f"\n✏️ Venta {sale_id} actualizada correctamente")
            
            # Verificar los cambios
            updated_sale = get_sale_by_id(sale_id)
            if updated_sale:
                print(f"   Nuevo subtotal: ${updated_sale['subtotal']:.2f}")
                
    except ValueError as e:
        print(f"❌ Error actualizando venta: {e}")

def demo_water_consumption():
    """Demostración de las funciones de consumo de agua"""
    
    print("=== DEMOSTRACIÓN DE FUNCIONES WATER CONSUMPTION ===\n")
    
    # 1. Crear registros de consumo
    try:
        # Registro inicial
        consumption_data1 = {
            'date': (datetime.now() - timedelta(days=2)).strftime('%Y-%m-%d %H:%M:%S'),
            'consumption': 85.5,
            'recharge': 100.0,
            'balance': 100.0  # Balance inicial
        }
        
        record_id1 = create_water_consumption(consumption_data1)
        print(f"✅ Registro de consumo creado con ID: {record_id1}")
        
        # Segundo registro
        consumption_data2 = {
            'date': (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d %H:%M:%S'),
            'consumption': 120.3,
            'recharge': 0.0,
            'balance': -20.3  # 100 - 120.3
        }
        
        record_id2 = create_water_consumption(consumption_data2)
        print(f"✅ Segundo registro creado con ID: {record_id2}")
        
        # Tercer registro con recarga
        consumption_data3 = {
            'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'consumption': 65.8,
            'recharge': 100.0,
            'balance': 13.9  # -20.3 - 65.8 + 100
        }
        
        record_id3 = create_water_consumption(consumption_data3)
        print(f"✅ Tercer registro creado con ID: {record_id3}")
        
    except ValueError as e:
        print(f"❌ Error creando registros: {e}")
        return
    
    # 2. Obtener registro por ID
    record = get_water_consumption_by_id(record_id1)
    if record:
        print(f"\n💧 Registro ID {record_id1}:")
        print(f"   Consumo: {record['consumption']}L")
        print(f"   Recarga: {record['recharge']}L")
        print(f"   Balance: {record['balance']}L")
        print(f"   Fecha: {record['date']}")
    
    # 3. Obtener todos los registros
    all_records = get_all_water_consumption()
    print(f"\n📊 Total registros: {len(all_records)}")
    
    # 4. Obtener consumo total
    total_consumption = get_total_consumption()
    total_recharge = get_total_recharge()
    print(f"📈 Consumo total: {total_consumption}L")
    print(f"📈 Recarga total: {total_recharge}L")
    
    # 5. Obtener balance actual
    current_balance = get_current_balance()
    print(f"💰 Balance actual: {current_balance}L")
    
    # 6. Estadísticas por mes
    current_year = datetime.now().year
    current_month = datetime.now().month
    
    monthly_stats = get_consumption_stats_by_period('month')
    print(f"\n📅 Estadísticas mensuales:")
    for stat in monthly_stats[:3]:  # Mostrar últimos 3 meses
        print(f"   {stat['period']}: Consumo {stat['total_consumption']}L, Recarga {stat['total_recharge']}L")
    
    # 7. Tendencia de consumo (últimos 7 días)
    trend = get_consumption_trend(7)
    print(f"\n📈 Tendencia últimos 7 días: {len(trend)} registros")
    
    # 8. Consumo diario promedio
    daily_avg = get_daily_consumption_average(30)
    print(f"📊 Consumo diario promedio (30 días): {daily_avg:.2f}L")
    
    # 9. Usar función automática de balance
    try:
        new_record_id = add_consumption_with_balance_calculation(
            consumption=45.2, 
            recharge=50.0
        )
        print(f"\n🤖 Registro automático creado con ID: {new_record_id}")
        
        # Verificar el nuevo balance
        new_balance = get_current_balance()
        print(f"   Nuevo balance: {new_balance}L")
        
    except ValueError as e:
        print(f"❌ Error en registro automático: {e}")
    
    # 10. Buscar alertas
    alerts = get_consumption_alerts(consumption_threshold=100.0, balance_threshold=20.0)
    print(f"\n⚠️  Alertas encontradas: {len(alerts)}")
    
    for alert in alerts:
        print(f"   {alert['date']}: {alert['alert_message']}")
    
    # 11. Obtener registros por rango de fechas
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=5)).strftime('%Y-%m-%d')
    
    date_range_records = get_water_consumption_by_date_range(start_date, end_date)
    print(f"\n📅 Registros últimos 5 días: {len(date_range_records)}")
    
    # 12. Actualizar un registro
    try:
        update_data = {
            'consumption': 95.0,
            'recharge': 10.0
        }
        success = update_water_consumption(record_id1, update_data)
        if success:
            print(f"\n✏️ Registro {record_id1} actualizado correctamente")
    except ValueError as e:
        print(f"❌ Error actualizando registro: {e}")


if __name__ == "__main__":
    create_tables()
    # crud_users()
