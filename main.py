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

config = cargar_config()
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

    botones = [
        ("⬛  Panel", panel_principal),
        ("📦  Inventario", inventario),
        ("🛒  Ventas", ventas),
        ("🕐  Apartados", apartados),
        ("👥  Clientes", clientes),
        ("🚚  Proveedores", proveedores),
        ("🏪  Sucursales", sucursales),
        ("📊  Reportes", reportes),
        ("⚙️  Configuración", configuracion),
    ]

    for texto, comando in botones:
        btn = ctk.CTkButton(sidebar, text=texto, fg_color="transparent",
                            text_color="#AAAAAA", hover_color="#222222",
                            anchor="w", height=36,
                            command=lambda c=comando: mostrar_panel(c) if c else None)
        btn.pack(fill="x", padx=8, pady=2)

    main_frame = ctk.CTkFrame(app, fg_color="#0f0f0f")
    main_frame.pack(side="left", fill="both", expand=True)

    topbar = ctk.CTkFrame(main_frame, height=50, fg_color="#1a1a1a")
    topbar.pack(fill="x", side="top")
    topbar.pack_propagate(False)

    ctk.CTkLabel(topbar, text="Panel Principal",
                 font=ctk.CTkFont(size=16, weight="bold"),
                 text_color="#FFFFFF").pack(side="left", padx=20, pady=10)

    ctk.CTkLabel(topbar, text="📍 Sucursal Matriz",
                 text_color="#E8751A").pack(side="right", padx=20)

    panel_principal()

def mostrar_panel(frame):
    for widget in main_frame.winfo_children():
        if widget != topbar:
            widget.destroy()
    frame()

def panel_principal():
    from database.db import conectar
    from datetime import datetime

    content = ctk.CTkFrame(main_frame, fg_color="#0f0f0f")
    content.pack(fill="both", expand=True, padx=20, pady=20)

    hoy = datetime.now().strftime("%Y-%m-%d")

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

    conn.close()

    stats = [
        ("Total Ventas Hoy", f"${ventas_hoy:.2f}"),
        ("Productos en Stock", str(total_productos)),
        ("Apartados Pendientes", str(apartados_pendientes)),
        ("Clientes Registrados", str(total_clientes)),
    ]

    stats_frame = ctk.CTkFrame(content, fg_color="transparent")
    stats_frame.pack(fill="x", pady=10)

    for titulo, valor in stats:
        card = ctk.CTkFrame(stats_frame, fg_color="#1a1a1a", corner_radius=10)
        card.pack(side="left", expand=True, fill="x", padx=8)
        ctk.CTkLabel(card, text=titulo, text_color="#888888",
                     font=ctk.CTkFont(size=11)).pack(pady=(12,2))
        ctk.CTkLabel(card, text=valor, text_color="#E8751A",
                     font=ctk.CTkFont(size=22, weight="bold")).pack(pady=(2,12))

    ctk.CTkLabel(content, text="⚠️  Alertas Críticas",
                 font=ctk.CTkFont(size=14, weight="bold"),
                 text_color="#E8751A").pack(anchor="w", pady=(20,8))

    alertas_frame = ctk.CTkFrame(content, fg_color="#1a1a1a", corner_radius=10)
    alertas_frame.pack(fill="x")

    if not alertas:
        ctk.CTkLabel(alertas_frame, text="Sin alertas por el momento",
                     text_color="#555555").pack(pady=20)
    else:
        for a in alertas:
            fila = ctk.CTkFrame(alertas_frame, fg_color="#222222", corner_radius=6)
            fila.pack(fill="x", padx=8, pady=3)
            ctk.CTkLabel(fila, text=a[0], text_color="#FFFFFF",
                         width=200, anchor="w").pack(side="left", padx=8)
            ctk.CTkLabel(fila, text=f"Stock: {a[1]}", text_color="#A32D2D",
                         width=100, anchor="w").pack(side="left")

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

def aplicar_tema(tema):
    ctk.set_appearance_mode(tema)
    construir_ui()

construir_ui()
app.mainloop()