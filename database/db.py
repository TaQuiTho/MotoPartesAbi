import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "motopartes.db")

def conectar():
    return sqlite3.connect(DB_PATH)

def crear_tablas():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS apartados (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        cliente TEXT NOT NULL,
        producto_id INTEGER,
        cantidad INTEGER DEFAULT 1,
        fecha TEXT NOT NULL,
        fecha_entrega TEXT,
        notas TEXT,
        estado TEXT DEFAULT 'pendiente',
        FOREIGN KEY (producto_id) REFERENCES productos(id)
    )
""")

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS proveedores (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL,
        telefono TEXT,
        email TEXT,
        direccion TEXT,
        notas TEXT
    )
""")

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS clientes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL,
        telefono TEXT,
        email TEXT,
        direccion TEXT,
        notas TEXT
    )
""")

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS productos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            marca TEXT,
            sku TEXT,
            cantidad INTEGER DEFAULT 0,
            precio_costo REAL DEFAULT 0,
            precio_menudeo REAL DEFAULT 0,
            precio_mayoreo REAL DEFAULT 0,
            stock_minimo INTEGER DEFAULT 5,
            descripcion TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ventas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha TEXT NOT NULL,
            total REAL DEFAULT 0,
            notas TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS venta_detalle (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            venta_id INTEGER,
            producto_id INTEGER,
            cantidad INTEGER,
            precio REAL,
            FOREIGN KEY (venta_id) REFERENCES ventas(id),
            FOREIGN KEY (producto_id) REFERENCES productos(id)
        )
    """)

    conn.commit()
    conn.close()