import customtkinter as ctk
from database.db import crear_tablas

def mostrar_panel(frame):
    for widget in main_frame.winfo_children():
        if widget != topbar:
            widget.destroy()
    frame()

def panel_principal():
    content = ctk.CTkFrame(main_frame, fg_color="#0f0f0f")
    content.pack(fill="both", expand=True, padx=20, pady=20)

    stats = [
        ("Total Ventas Hoy", "$0.00"),
        ("Productos en Stock", "0"),
        ("Apartados Pendientes", "0"),
        ("Clientes Atendidos", "0"),
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
    ctk.CTkLabel(alertas_frame, text="Sin alertas por el momento",
                 text_color="#555555").pack(pady=20)

def inventario():
    content = ctk.CTkFrame(main_frame, fg_color="#0f0f0f")
    content.pack(fill="both", expand=True, padx=20, pady=20)
    ctk.CTkLabel(content, text="Módulo de Inventario — en construcción",
                 text_color="#555555").pack(pady=40)

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

app = ctk.CTk()
crear_tablas()
app.title("Moto Partes Abi")
app.geometry("1200x700")

sidebar = ctk.CTkFrame(app, width=200, fg_color="#111111")
sidebar.pack(side="left", fill="y")
sidebar.pack_propagate(False)

ctk.CTkLabel(sidebar, text="Moto Partes Abi",
             font=ctk.CTkFont(size=14, weight="bold"),
             text_color="#FFFFFF").pack(pady=20, padx=10)

botones = [
    ("⬛  Panel", panel_principal),
    ("📦  Inventario", inventario),
    ("🛒  Ventas", None),
    ("🕐  Apartados", None),
    ("👥  Clientes", None),
    ("🚚  Proveedores", None),
    ("🏪  Sucursales", None),
    ("📊  Reportes", None),
    ("⚙️  Configuración", None),
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

app.mainloop()