import sqlite3

# Nombre del archivo donde se guardará la BD local
DB_NAME = "local.db"

def create_tables():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

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
        user_id INTEGER,
        machine_id INTEGER,
        FOREIGN KEY (user_id) REFERENCES users(id),
        FOREIGN KEY (machine_id) REFERENCES machines(id)
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

if __name__ == "__main__":
    create_tables()
