import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "motopartes.db")


def conectar():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def crear_tablas():
    conn = conectar()
    cursor = conn.cursor()

    def agregar_columna_si_no_existe(tabla, columna_sql):
        try:
            nombre_columna = columna_sql.split()[0]

            cursor.execute(f"PRAGMA table_info({tabla})")
            columnas = [c[1] for c in cursor.fetchall()]

            if nombre_columna not in columnas:
                cursor.execute(
                    f"ALTER TABLE {tabla} ADD COLUMN {columna_sql}"
                )
        except Exception:
            pass

    # =========================
    # PRODUCTOS
    # =========================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS productos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            marca TEXT,
            sku TEXT UNIQUE,
            cantidad INTEGER DEFAULT 0 CHECK(cantidad >= 0),
            precio_costo REAL DEFAULT 0 CHECK(precio_costo >= 0),
            precio_menudeo REAL DEFAULT 0 CHECK(precio_menudeo >= 0),
            precio_mayoreo REAL DEFAULT 0 CHECK(precio_mayoreo >= 0),
            stock_minimo INTEGER DEFAULT 5 CHECK(stock_minimo >= 0),
            descripcion TEXT
        )
    """)

    agregar_columna_si_no_existe(
        "productos",
        "categoria TEXT"
    )

    agregar_columna_si_no_existe(
        "productos",
        "imagen TEXT"
    )

    # =========================
    # CLIENTES
    # =========================

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

    agregar_columna_si_no_existe(
        "clientes",
        "whatsapp TEXT"
    )

    agregar_columna_si_no_existe(
        "clientes",
        "credito REAL DEFAULT 0"
    )

    agregar_columna_si_no_existe(
        "clientes",
        "limite_credito REAL DEFAULT 0"
    )

    # =========================
    # PROVEEDORES
    # =========================

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

    agregar_columna_si_no_existe(
        "proveedores",
        "whatsapp TEXT"
    )

    agregar_columna_si_no_existe(
        "proveedores",
        "categoria TEXT"
    )

    # =========================
    # SUCURSALES
    # =========================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sucursales (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            direccion TEXT,
            telefono TEXT,
            gerente TEXT,
            activa INTEGER DEFAULT 1 CHECK(activa IN (0, 1))
        )
    """)

    # =========================
    # VENTAS
    # =========================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS ventas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha TEXT NOT NULL,
            total REAL DEFAULT 0 CHECK(total >= 0),
            notas TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS venta_detalle (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            venta_id INTEGER,
            producto_id INTEGER,
            cantidad INTEGER NOT NULL CHECK(cantidad > 0),
            precio REAL NOT NULL CHECK(precio >= 0),
            FOREIGN KEY (venta_id) REFERENCES ventas(id) ON DELETE CASCADE,
            FOREIGN KEY (producto_id) REFERENCES productos(id) ON DELETE SET NULL
        )
    """)

    # =========================
    # APARTADOS
    # =========================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS apartados (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cliente TEXT NOT NULL,
            producto_id INTEGER,
            cantidad INTEGER DEFAULT 1 CHECK(cantidad > 0),
            fecha TEXT NOT NULL,
            fecha_entrega TEXT,
            notas TEXT,
            estado TEXT DEFAULT 'pendiente',
            FOREIGN KEY (producto_id) REFERENCES productos(id) ON DELETE SET NULL
        )
    """)

    agregar_columna_si_no_existe(
        "apartados",
        "anticipo REAL DEFAULT 0"
    )

    agregar_columna_si_no_existe(
        "apartados",
        "total REAL DEFAULT 0"
    )

    # =========================
    # MOVIMIENTOS INVENTARIO
    # =========================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS movimientos_inventario (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            producto_id INTEGER,
            tipo TEXT NOT NULL,
            cantidad INTEGER NOT NULL,
            fecha TEXT NOT NULL,
            notas TEXT,
            FOREIGN KEY (producto_id) REFERENCES productos(id) ON DELETE SET NULL
        )
    """)

    # =========================
    # COMPATIBILIDADES
    # =========================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS compatibilidades (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            producto_id INTEGER NOT NULL,
            vehiculo TEXT NOT NULL,
            FOREIGN KEY(producto_id)
            REFERENCES productos(id)
            ON DELETE CASCADE
        )
    """)

    # =========================
    # COMPRAS
    # =========================

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS compras (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            proveedor_id INTEGER,
            fecha TEXT NOT NULL,
            subtotal REAL DEFAULT 0,
            iva REAL DEFAULT 0,
            total REAL DEFAULT 0,
            referencia TEXT,
            notas TEXT,
            FOREIGN KEY(proveedor_id)
            REFERENCES proveedores(id)
            ON DELETE SET NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS compra_detalle (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            compra_id INTEGER,
            producto_id INTEGER,
            cantidad INTEGER,
            costo REAL,
            subtotal REAL,
            FOREIGN KEY(compra_id)
            REFERENCES compras(id)
            ON DELETE CASCADE,
            FOREIGN KEY(producto_id)
            REFERENCES productos(id)
            ON DELETE SET NULL
        )
    """)

    # =========================
    # ÍNDICES
    # =========================

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_productos_nombre
        ON productos(nombre)
    """)

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_productos_sku
        ON productos(sku)
    """)

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_ventas_fecha
        ON ventas(fecha)
    """)

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_apartados_estado
        ON apartados(estado)
    """)

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_apartados_producto
        ON apartados(producto_id)
    """)

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_venta_detalle_producto
        ON venta_detalle(producto_id)
    """)

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_movimientos_producto
        ON movimientos_inventario(producto_id)
    """)

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_compat_producto
        ON compatibilidades(producto_id)
    """)

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_compras_fecha
        ON compras(fecha)
    """)

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_compra_detalle_producto
        ON compra_detalle(producto_id)
    """)

    conn.commit()
    conn.close()