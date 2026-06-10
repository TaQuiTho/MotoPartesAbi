import customtkinter as ctk
from datetime import datetime
import sqlite3

from database.db import crear_tablas, conectar
from modules.inventario import mostrar_inventario
from modules.ventas import mostrar_ventas
from modules.clientes import mostrar_clientes
from modules.proveedores import mostrar_proveedores
from modules.apartados import mostrar_apartados
from modules.sucursales import mostrar_sucursales
from modules.reportes import mostrar_reportes
from modules.configuracion import mostrar_configuracion, cargar_config
from config.translations import t


def texto(key, idioma="Español", fallback=None):
    valor = t(key, idioma)
    if valor == key and fallback is not None:
        return fallback
    return valor


config = cargar_config()
idioma = config.get("idioma", "Español")
nombre_negocio = config.get("nombre_negocio", "Moto Partes Abi")
tema = config.get("tema", "dark")

ctk.set_appearance_mode(tema)
ctk.set_default_color_theme("blue")

app = ctk.CTk()
crear_tablas()

app.title(nombre_negocio)
app.geometry("1200x700")
app.minsize(1050, 650)

sidebar = None
main_frame = None
topbar = None
titulo_topbar = None


def limpiar_main():
    if not main_frame:
        return

    for widget in main_frame.winfo_children():
        if widget != topbar:
            widget.destroy()


def actualizar_titulo(titulo):
    global titulo_topbar

    if titulo_topbar:
        titulo_topbar.configure(text=titulo)


def mostrar_alerta(titulo, mensaje):
    ventana = ctk.CTkToplevel(app)
    ventana.title(titulo)
    ventana.geometry("380x160")
    ventana.grab_set()
    ventana.resizable(False, False)

    ctk.CTkLabel(
        ventana,
        text=mensaje,
        text_color="#E8751A",
        font=ctk.CTkFont(size=13, weight="bold"),
        wraplength=340
    ).pack(pady=25)

    ctk.CTkButton(
        ventana,
        text="OK",
        fg_color="#E8751A",
        hover_color="#c45e0e",
        command=ventana.destroy
    ).pack()


def mostrar_panel(funcion, titulo=None):
    limpiar_main()

    if titulo:
        actualizar_titulo(titulo)

    try:
        funcion()
    except Exception as e:
        mostrar_alerta("Error", f"No se pudo abrir el módulo:\n{e}")


def construir_ui():
    global sidebar, main_frame, topbar, titulo_topbar
    global config, idioma, nombre_negocio

    config = cargar_config()
    idioma = config.get("idioma", "Español")
    nombre_negocio = config.get("nombre_negocio", "Moto Partes Abi")

    app.title(nombre_negocio)

    for widget in app.winfo_children():
        widget.destroy()

    sidebar = ctk.CTkFrame(app, width=210, fg_color="#111111")
    sidebar.pack(side="left", fill="y")
    sidebar.pack_propagate(False)

    ctk.CTkLabel(
        sidebar,
        text=nombre_negocio,
        font=ctk.CTkFont(size=15, weight="bold"),
        text_color="#FFFFFF",
        wraplength=180
    ).pack(pady=(22, 4), padx=10)

    ctk.CTkLabel(
        sidebar,
        text=texto("sucursal_matriz", idioma, "📍 Sucursal Matriz"),
        text_color="#E8751A",
        font=ctk.CTkFont(size=11)
    ).pack(pady=(0, 14), padx=10)

    secciones = [
        (
            "PRINCIPAL" if idioma == "Español" else "MAIN",
            [
                (f"⬛  {texto('panel', idioma, 'Panel')}", panel_principal, texto("panel_principal", idioma, "Panel Principal")),
                (f"📦  {texto('inventario', idioma, 'Inventario')}", inventario, texto("inventario", idioma, "Inventario")),
                (f"🛒  {texto('ventas', idioma, 'Ventas')}", ventas, texto("ventas", idioma, "Ventas")),
            ]
        ),
        (
            "GESTIÓN" if idioma == "Español" else "MANAGEMENT",
            [
                (f"🕐  {texto('apartados', idioma, 'Apartados')}", apartados, texto("apartados", idioma, "Apartados")),
                (f"👥  {texto('clientes', idioma, 'Clientes')}", clientes, texto("clientes", idioma, "Clientes")),
                (f"🚚  {texto('proveedores', idioma, 'Proveedores')}", proveedores, texto("proveedores", idioma, "Proveedores")),
            ]
        ),
        (
            "ADMINISTRACIÓN" if idioma == "Español" else "ADMINISTRATION",
            [
                (f"🏪  {texto('sucursales', idioma, 'Sucursales')}", sucursales, texto("sucursales", idioma, "Sucursales")),
                (f"📊  {texto('reportes', idioma, 'Reportes')}", reportes, texto("reportes", idioma, "Reportes")),
                (f"⚙️  {texto('configuracion', idioma, 'Configuración')}", configuracion, texto("configuracion", idioma, "Configuración")),
            ]
        ),
    ]

    for seccion, items in secciones:
        ctk.CTkLabel(
            sidebar,
            text=seccion,
            text_color="#555555",
            font=ctk.CTkFont(size=9, weight="bold")
        ).pack(anchor="w", padx=16, pady=(12, 2))

        for texto_btn, comando, titulo in items:
            ctk.CTkButton(
                sidebar,
                text=texto_btn,
                fg_color="transparent",
                text_color="#AAAAAA",
                hover_color="#222222",
                anchor="w",
                height=34,
                command=lambda c=comando, ti=titulo: mostrar_panel(c, ti)
            ).pack(fill="x", padx=8, pady=1)

    main_frame = ctk.CTkFrame(app, fg_color="#0f0f0f")
    main_frame.pack(side="left", fill="both", expand=True)

    topbar = ctk.CTkFrame(main_frame, height=50, fg_color="#1a1a1a")
    topbar.pack(fill="x", side="top")
    topbar.pack_propagate(False)

    titulo_topbar = ctk.CTkLabel(
        topbar,
        text=texto("panel_principal", idioma, "Panel Principal"),
        font=ctk.CTkFont(size=15, weight="bold"),
        text_color="#FFFFFF"
    )
    titulo_topbar.pack(side="left", padx=20, pady=10)

    ctk.CTkLabel(
        topbar,
        text="🔔",
        text_color="#888888",
        font=ctk.CTkFont(size=16)
    ).pack(side="right", padx=10)

    ctk.CTkLabel(
        topbar,
        text=datetime.now().strftime("%Y-%m-%d"),
        text_color="#888888",
        font=ctk.CTkFont(size=11)
    ).pack(side="right", padx=10)

    panel_principal()


def obtener_datos_panel():
    datos = {
        "ventas_hoy": 0,
        "total_productos": 0,
        "apartados_pendientes": 0,
        "total_clientes": 0,
        "alertas": [],
        "inventario_reciente": [],
    }

    hoy = datetime.now().strftime("%Y-%m-%d")

    try:
        conn = conectar()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT COALESCE(SUM(total), 0) FROM ventas WHERE fecha LIKE ?",
            (f"{hoy}%",)
        )
        datos["ventas_hoy"] = cursor.fetchone()[0] or 0

        cursor.execute("SELECT COUNT(*) FROM productos")
        datos["total_productos"] = cursor.fetchone()[0] or 0

        cursor.execute("SELECT COUNT(*) FROM apartados WHERE estado='pendiente'")
        datos["apartados_pendientes"] = cursor.fetchone()[0] or 0

        cursor.execute("SELECT COUNT(*) FROM clientes")
        datos["total_clientes"] = cursor.fetchone()[0] or 0

        cursor.execute("""
            SELECT nombre, cantidad, stock_minimo
            FROM productos
            WHERE cantidad <= stock_minimo
            ORDER BY cantidad ASC
            LIMIT 10
        """)
        datos["alertas"] = cursor.fetchall()

        cursor.execute("""
            SELECT nombre, sku, cantidad, stock_minimo
            FROM productos
            ORDER BY id DESC
            LIMIT 6
        """)
        datos["inventario_reciente"] = cursor.fetchall()

        conn.close()

    except sqlite3.Error as e:
        print("Error SQLite panel:", e)

    except Exception as e:
        print("Error panel:", e)

    return datos


def panel_principal():
    actualizar_titulo(texto("panel_principal", idioma, "Panel Principal"))

    content = ctk.CTkScrollableFrame(main_frame, fg_color="#0f0f0f")
    content.pack(fill="both", expand=True, padx=0, pady=0)

    hoy = datetime.now().strftime("%Y-%m-%d")
    hora = datetime.now().strftime("%H:%M")

    datos = obtener_datos_panel()

    banner = ctk.CTkFrame(content, fg_color="#1a1a1a", corner_radius=12)
    banner.pack(fill="x", padx=20, pady=(20, 10))

    ctk.CTkLabel(
        banner,
        text=texto("resumen_operaciones", idioma, "Resumen de Operaciones"),
        font=ctk.CTkFont(size=20, weight="bold"),
        text_color="#FFFFFF"
    ).pack(anchor="w", padx=20, pady=(18, 4))

    ctk.CTkLabel(
        banner,
        text=f"{texto('bienvenido', idioma, 'Bienvenido. Aquí tienes una vista rápida del estado actual.')} — {hoy} {hora}",
        font=ctk.CTkFont(size=11),
        text_color="#666666",
        wraplength=850
    ).pack(anchor="w", padx=20, pady=(0, 18))

    stats_data = [
        (
            texto("total_ventas_hoy", idioma, "TOTAL VENTAS HOY"),
            f"${datos['ventas_hoy']:.2f}",
            texto("actualizado", idioma, "Actualizado") + f" {hora}",
            "#E8751A"
        ),
        (
            texto("productos_stock", idioma, "PRODUCTOS EN STOCK"),
            str(datos["total_productos"]),
            texto("actualizado", idioma, "Actualizado") + f" {hora}",
            "#3B8BEB"
        ),
        (
            texto("apartados_pendientes", idioma, "APARTADOS PENDIENTES"),
            str(datos["apartados_pendientes"]),
            texto("ver_todos", idioma, "Ver todos"),
            "#E8751A"
        ),
        (
            texto("clientes_registrados", idioma, "CLIENTES REGISTRADOS"),
            str(datos["total_clientes"]),
            texto("actualizado", idioma, "Actualizado") + f" {hora}",
            "#888888"
        ),
    ]

    stats_frame = ctk.CTkFrame(content, fg_color="transparent")
    stats_frame.pack(fill="x", padx=20, pady=(0, 10))

    for titulo, valor, subtexto, color in stats_data:
        card = ctk.CTkFrame(stats_frame, fg_color="#1a1a1a", corner_radius=10)
        card.pack(side="left", expand=True, fill="x", padx=6)

        ctk.CTkLabel(
            card,
            text=subtexto,
            text_color="#555555",
            font=ctk.CTkFont(size=10)
        ).pack(anchor="e", padx=10, pady=(10, 0))

        ctk.CTkLabel(
            card,
            text=titulo,
            text_color="#888888",
            font=ctk.CTkFont(size=10, weight="bold")
        ).pack(anchor="w", padx=14, pady=(4, 0))

        ctk.CTkLabel(
            card,
            text=valor,
            text_color=color,
            font=ctk.CTkFont(size=24, weight="bold")
        ).pack(anchor="w", padx=14, pady=(2, 14))

    bottom_frame = ctk.CTkFrame(content, fg_color="transparent")
    bottom_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))

    left = ctk.CTkFrame(bottom_frame, fg_color="#1a1a1a", corner_radius=10)
    left.pack(side="left", fill="both", expand=True, padx=(0, 8))

    ctk.CTkLabel(
        left,
        text=texto("alertas_criticas", idioma, "⚠️ Alertas Críticas"),
        font=ctk.CTkFont(size=13, weight="bold"),
        text_color="#E8751A"
    ).pack(anchor="w", padx=15, pady=(14, 8))

    if not datos["alertas"]:
        ctk.CTkLabel(
            left,
            text=texto("sin_alertas", idioma, "✔ Sin alertas por el momento."),
            text_color="#555555",
            font=ctk.CTkFont(size=11),
            wraplength=360
        ).pack(pady=20)
    else:
        for nombre, cantidad, minimo in datos["alertas"]:
            fila = ctk.CTkFrame(left, fg_color="#222222", corner_radius=6)
            fila.pack(fill="x", padx=10, pady=3)

            estado = "Agotado" if cantidad <= 0 else texto("stock_bajo", idioma, "Stock Bajo")

            ctk.CTkLabel(
                fila,
                text=nombre,
                text_color="#FFFFFF",
                width=190,
                anchor="w"
            ).pack(side="left", padx=8, pady=8)

            ctk.CTkLabel(
                fila,
                text=f"{estado}: {cantidad} / Min: {minimo}",
                text_color="#A32D2D" if cantidad <= 0 else "#E8751A",
                width=160,
                anchor="w"
            ).pack(side="left")

    right = ctk.CTkFrame(bottom_frame, fg_color="#1a1a1a", corner_radius=10)
    right.pack(side="left", fill="both", expand=True, padx=(8, 0))

    header_right = ctk.CTkFrame(right, fg_color="transparent")
    header_right.pack(fill="x", padx=15, pady=(14, 8))

    ctk.CTkLabel(
        header_right,
        text=texto("inventario_reciente", idioma, "Inventario Reciente"),
        font=ctk.CTkFont(size=13, weight="bold"),
        text_color="#FFFFFF"
    ).pack(side="left")

    ctk.CTkButton(
        header_right,
        text=texto("agregar_producto", idioma, "Agregar Producto"),
        width=130,
        height=26,
        fg_color="#E8751A",
        hover_color="#c45e0e",
        font=ctk.CTkFont(size=11),
        command=lambda: mostrar_panel(inventario, texto("inventario", idioma, "Inventario"))
    ).pack(side="right")

    cols = ctk.CTkFrame(right, fg_color="transparent")
    cols.pack(fill="x", padx=15, pady=(0, 4))

    columnas = [
        (texto("producto", idioma, "PRODUCTO").upper(), 180),
        (texto("sku", idioma, "SKU").upper(), 90),
        (texto("cantidad", idioma, "STOCK").upper(), 60),
        (texto("estado", idioma, "ESTADO").upper(), 90),
    ]

    for col, w in columnas:
        ctk.CTkLabel(
            cols,
            text=col,
            text_color="#444444",
            font=ctk.CTkFont(size=10, weight="bold"),
            width=w,
            anchor="w"
        ).pack(side="left")

    if not datos["inventario_reciente"]:
        ctk.CTkLabel(
            right,
            text=texto("sin_productos", idioma, "Sin productos registrados"),
            text_color="#555555"
        ).pack(pady=10)
    else:
        for nombre, sku, cantidad, stock_minimo in datos["inventario_reciente"]:
            fila = ctk.CTkFrame(right, fg_color="#222222", corner_radius=6)
            fila.pack(fill="x", padx=10, pady=2)

            if cantidad <= 0:
                estado_color = "#A32D2D"
                estado_txt = "Agotado"
            elif cantidad <= stock_minimo:
                estado_color = "#E8751A"
                estado_txt = texto("stock_bajo", idioma, "Stock Bajo")
            else:
                estado_color = "#3B6D11"
                estado_txt = texto("stock_alto", idioma, "Stock Alto")

            ctk.CTkLabel(
                fila,
                text=nombre,
                text_color="#FFFFFF",
                width=180,
                anchor="w"
            ).pack(side="left", padx=8, pady=7)

            ctk.CTkLabel(
                fila,
                text=sku or "-",
                text_color="#888888",
                width=90,
                anchor="w"
            ).pack(side="left")

            ctk.CTkLabel(
                fila,
                text=str(cantidad),
                text_color="#888888",
                width=60,
                anchor="w"
            ).pack(side="left")

            ctk.CTkLabel(
                fila,
                text=estado_txt,
                text_color=estado_color,
                width=90,
                anchor="w"
            ).pack(side="left")

    accion = ctk.CTkFrame(right, fg_color="#E8751A", corner_radius=8)
    accion.pack(fill="x", padx=10, pady=(10, 14))

    mensaje_accion = texto(
        "mensaje_accion",
        idioma,
        "Gestiona tu tienda de manera eficiente con un solo toque."
    )

    ctk.CTkLabel(
        accion,
        text=mensaje_accion,
        text_color="#FFFFFF",
        font=ctk.CTkFont(size=10),
        wraplength=240
    ).pack(side="left", padx=12, pady=10)

    ctk.CTkButton(
        accion,
        text=texto("realizar_venta", idioma, "Realizar Venta →"),
        fg_color="#c45e0e",
        hover_color="#a04a00",
        text_color="#FFFFFF",
        font=ctk.CTkFont(size=12, weight="bold"),
        command=lambda: mostrar_panel(ventas, texto("ventas", idioma, "Ventas"))
    ).pack(side="right", padx=12, pady=10)


def inventario():
    mostrar_inventario(main_frame)


def ventas():
    mostrar_ventas(main_frame)


def clientes():
    mostrar_clientes(main_frame)


def proveedores():
    mostrar_proveedores(main_frame)


def apartados():
    mostrar_apartados(main_frame)


def sucursales():
    mostrar_sucursales(main_frame)


def reportes():
    mostrar_reportes(main_frame)


def configuracion():
    mostrar_configuracion(main_frame, aplicar_tema)


def aplicar_tema(nuevo_tema, nuevo_idioma=None):
    global idioma, config, nombre_negocio

    try:
        ctk.set_appearance_mode(nuevo_tema)

        config = cargar_config()
        idioma = nuevo_idioma or config.get("idioma", "Español")
        nombre_negocio = config.get("nombre_negocio", "Moto Partes Abi")

        construir_ui()

    except Exception as e:
        mostrar_alerta("Error", f"No se pudo aplicar la configuración:\n{e}")


construir_ui()
app.mainloop()