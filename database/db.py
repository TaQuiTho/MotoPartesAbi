import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "motopartes.db")

def conectar():
    return sqlite3.connect(DB_PATH)

def crear_tablas():
    conn = conectar()
    cursor = conn.cursor()

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

    conn.commit()
    conn.close()
