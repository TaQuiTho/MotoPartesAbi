import customtkinter as ctk
from modules.inventario import mostrar_inventario
from modules.apartados import mostrar_apartados
from modules.proveedores import mostrar_proveedores
from modules.clientes import mostrar_clientes
from modules.ventas import mostrar_ventas
from database.db import crear_tablas
from modules.sucursales import mostrar_sucursales
from modules.reportes import mostrar_reportes
from modules.configuracion import mostrar_configuracion, cargar_config
from config.translations import t

config = cargar_config()
idioma = config.get("idioma", "Español")
ctk.set_appearance_mode(config.get("tema", "dark"))
ctk.set_default_color_theme("blue")

app = ctk.CTk()
crear_tablas()
app.title("Moto Partes Abi")
app.geometry("1200x700")

sidebar = None
main_frame = None
topbar = None

def construir_ui():
    global sidebar, main_frame, topbar

    for widget in app.winfo_children():
        widget.destroy()

    sidebar = ctk.CTkFrame(app, width=200, fg_color="#111111")
    sidebar.pack(side="left", fill="y")
    sidebar.pack_propagate(False)

    ctk.CTkLabel(sidebar, text="Moto Partes Abi",
                 font=ctk.CTkFont(size=14, weight="bold"),
                 text_color="#FFFFFF").pack(pady=20, padx=10)

    secciones = [
        ("PRINCIPAL" if idioma == "Español" else "MAIN", [
            (f"⬛  {t('panel', idioma)}", panel_principal),
            (f"📦  {t('inventario', idioma)}", inventario),
            (f"🛒  {t('ventas', idioma)}", ventas),
        ]),
        ("GESTIÓN" if idioma == "Español" else "MANAGEMENT", [
            (f"🕐  {t('apartados', idioma)}", apartados),
            (f"👥  {t('clientes', idioma)}", clientes),
            (f"🚚  {t('proveedores', idioma)}", proveedores),
        ]),
        ("ADMINISTRACIÓN" if idioma == "Español" else "ADMINISTRATION", [
            (f"🏪  {t('sucursales', idioma)}", sucursales),
            (f"📊  {t('reportes', idioma)}", reportes),
            (f"⚙️  {t('configuracion', idioma)}", configuracion),
        ]),
    ]

    for seccion, items in secciones:
        ctk.CTkLabel(sidebar, text=seccion, text_color="#555555",
                     font=ctk.CTkFont(size=9, weight="bold")).pack(anchor="w", padx=16, pady=(12,2))
        for texto, comando in items:
            btn = ctk.CTkButton(sidebar, text=texto, fg_color="transparent",
                                text_color="#AAAAAA", hover_color="#222222",
                                anchor="w", height=34,
                                command=lambda c=comando: mostrar_panel(c) if c else None)
            btn.pack(fill="x", padx=8, pady=1)

    main_frame = ctk.CTkFrame(app, fg_color="#0f0f0f")
    main_frame.pack(side="left", fill="both", expand=True)

    topbar = ctk.CTkFrame(main_frame, height=50, fg_color="#1a1a1a")
    topbar.pack(fill="x", side="top")
    topbar.pack_propagate(False)

    ctk.CTkLabel(topbar, text=t("panel_principal", idioma),
                 font=ctk.CTkFont(size=15, weight="bold"),
                 text_color="#FFFFFF").pack(side="left", padx=20, pady=10)

    ctk.CTkLabel(topbar, text="🔔", text_color="#888888",
                 font=ctk.CTkFont(size=16)).pack(side="right", padx=10)

    ctk.CTkLabel(topbar, text=t("sucursal_matriz", idioma),
                 text_color="#E8751A").pack(side="right", padx=10)

    panel_principal()

def mostrar_panel(frame):
    for widget in main_frame.winfo_children():
        if widget != topbar:
            widget.destroy()
    frame()

def panel_principal():
    from database.db import conectar
    from datetime import datetime

    content = ctk.CTkScrollableFrame(main_frame, fg_color="#0f0f0f")
    content.pack(fill="both", expand=True, padx=0, pady=0)

    hoy = datetime.now().strftime("%Y-%m-%d")
    hora = datetime.now().strftime("%H:%M")

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("SELECT COALESCE(SUM(total), 0) FROM ventas WHERE fecha LIKE ?", (f"{hoy}%",))
    ventas_hoy = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM productos")
    total_productos = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM apartados WHERE estado='pendiente'")
    apartados_pendientes = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM clientes")
    total_clientes = cursor.fetchone()[0]

    cursor.execute("SELECT nombre, cantidad FROM productos WHERE cantidad <= stock_minimo")
    alertas = cursor.fetchall()

    cursor.execute("SELECT nombre, sku, cantidad FROM productos ORDER BY id DESC LIMIT 5")
    inventario_reciente = cursor.fetchall()

    conn.close()

    banner = ctk.CTkFrame(content, fg_color="#1a1a1a", corner_radius=12)
    banner.pack(fill="x", padx=20, pady=(20,10))

    ctk.CTkLabel(banner, text=t("resumen_operaciones", idioma),
                 font=ctk.CTkFont(size=20, weight="bold"),
                 text_color="#FFFFFF").pack(anchor="w", padx=20, pady=(18,4))
    ctk.CTkLabel(banner, text=f"{t('bienvenido', idioma)} — {hoy} {hora}",
                 font=ctk.CTkFont(size=11),
                 text_color="#666666").pack(anchor="w", padx=20, pady=(0,18))

    stats_data = [
        (t("total_ventas_hoy", idioma), f"${ventas_hoy:.2f}", "+12% vs ayer", "#E8751A"),
        (t("productos_stock", idioma), str(total_productos), f"{t('actualizado', idioma)} {hora}", "#3B8BEB"),
        (t("apartados_pendientes", idioma), str(apartados_pendientes), t("ver_todos", idioma), "#E8751A"),
        (t("clientes_registrados", idioma), str(total_clientes), "Nuevos: 0", "#888888"),
    ]

    stats_frame = ctk.CTkFrame(content, fg_color="transparent")
    stats_frame.pack(fill="x", padx=20, pady=(0,10))

    for titulo, valor, subtexto, color in stats_data:
        card = ctk.CTkFrame(stats_frame, fg_color="#1a1a1a", corner_radius=10)
        card.pack(side="left", expand=True, fill="x", padx=6)
        ctk.CTkLabel(card, text=subtexto, text_color="#555555",
                     font=ctk.CTkFont(size=10)).pack(anchor="e", padx=10, pady=(10,0))
        ctk.CTkLabel(card, text=titulo, text_color="#888888",
                     font=ctk.CTkFont(size=10, weight="bold")).pack(anchor="w", padx=14, pady=(4,0))
        ctk.CTkLabel(card, text=valor, text_color=color,
                     font=ctk.CTkFont(size=24, weight="bold")).pack(anchor="w", padx=14, pady=(2,14))

    bottom_frame = ctk.CTkFrame(content, fg_color="transparent")
    bottom_frame.pack(fill="both", expand=True, padx=20, pady=(0,20))

    left = ctk.CTkFrame(bottom_frame, fg_color="#1a1a1a", corner_radius=10)
    left.pack(side="left", fill="both", expand=True, padx=(0,8))

    ctk.CTkLabel(left, text=t("alertas_criticas", idioma),
                 font=ctk.CTkFont(size=13, weight="bold"),
                 text_color="#E8751A").pack(anchor="w", padx=15, pady=(14,8))

    if not alertas:
        ctk.CTkLabel(left, text=t("sin_alertas", idioma),
                     text_color="#555555", font=ctk.CTkFont(size=11)).pack(pady=20)
    else:
        for a in alertas:
            fila = ctk.CTkFrame(left, fg_color="#222222", corner_radius=6)
            fila.pack(fill="x", padx=10, pady=3)
            ctk.CTkLabel(fila, text=a[0], text_color="#FFFFFF",
                         width=180, anchor="w").pack(side="left", padx=8, pady=8)
            ctk.CTkLabel(fila, text=f"Stock: {a[1]}", text_color="#A32D2D",
                         width=80, anchor="w").pack(side="left")

    right = ctk.CTkFrame(bottom_frame, fg_color="#1a1a1a", corner_radius=10)
    right.pack(side="left", fill="both", expand=True, padx=(8,0))

    header_right = ctk.CTkFrame(right, fg_color="transparent")
    header_right.pack(fill="x", padx=15, pady=(14,8))

    ctk.CTkLabel(header_right, text=t("inventario_reciente", idioma),
                 font=ctk.CTkFont(size=13, weight="bold"),
                 text_color="#FFFFFF").pack(side="left")

    ctk.CTkButton(header_right, text=t("agregar_producto", idioma), width=120, height=26,
                  fg_color="#E8751A", hover_color="#c45e0e",
                  font=ctk.CTkFont(size=11),
                  command=lambda: mostrar_panel(inventario)).pack(side="right")

    cols = ctk.CTkFrame(right, fg_color="transparent")
    cols.pack(fill="x", padx=15, pady=(0,4))
    for col, w in [("PRODUCTO", 180), ("CÓDIGO", 90), ("STOCK", 60), ("ESTADO", 80)]:
        ctk.CTkLabel(cols, text=col, text_color="#444444",
                     font=ctk.CTkFont(size=10, weight="bold"),
                     width=w, anchor="w").pack(side="left")

    if not inventario_reciente:
        ctk.CTkLabel(right, text=t("sin_productos", idioma),
                     text_color="#555555").pack(pady=10)
    else:
        for p in inventario_reciente:
            fila = ctk.CTkFrame(right, fg_color="#222222", corner_radius=6)
            fila.pack(fill="x", padx=10, pady=2)
            ctk.CTkLabel(fila, text=p[0], text_color="#FFFFFF",
                         width=180, anchor="w").pack(side="left", padx=8, pady=7)
            ctk.CTkLabel(fila, text=p[1] or "-", text_color="#888888",
                         width=90, anchor="w").pack(side="left")
            ctk.CTkLabel(fila, text=str(p[2]), text_color="#888888",
                         width=60, anchor="w").pack(side="left")
            estado_color = "#A32D2D" if p[2] <= 5 else "#3B6D11"
            estado_txt = t("stock_bajo", idioma) if p[2] <= 5 else t("stock_alto", idioma)
            ctk.CTkLabel(fila, text=estado_txt, text_color=estado_color,
                         width=80, anchor="w").pack(side="left")

    accion = ctk.CTkFrame(right, fg_color="#E8751A", corner_radius=8)
    accion.pack(fill="x", padx=10, pady=(10,14))
    ctk.CTkLabel(accion, text="Gestiona tu tienda de manera eficiente con un solo toque.",
                 text_color="#FFFFFF", font=ctk.CTkFont(size=10),
                 wraplength=200).pack(side="left", padx=12, pady=10)
    ctk.CTkButton(accion, text=t("realizar_venta", idioma), fg_color="#c45e0e",
                  hover_color="#a04a00", text_color="#FFFFFF",
                  font=ctk.CTkFont(size=12, weight="bold"),
                  command=lambda: mostrar_panel(ventas)).pack(side="right", padx=12, pady=10)

def inventario():
    mostrar_inventario(main_frame)

def sucursales():
    mostrar_sucursales(main_frame)

def ventas():
    mostrar_ventas(main_frame)

def reportes():
    mostrar_reportes(main_frame)

def proveedores():
    mostrar_proveedores(main_frame)

def clientes():
    mostrar_clientes(main_frame)

def configuracion():
    mostrar_configuracion(main_frame, aplicar_tema)

def apartados():
    mostrar_apartados(main_frame)

def aplicar_tema(tema, nuevo_idioma=None):
    global idioma
    ctk.set_appearance_mode(tema)
    if nuevo_idioma:
        idioma = nuevo_idioma
    construir_ui()

construir_ui()
app.mainloop()