import customtkinter as ctk

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

app = ctk.CTk()
app.title("Moto Partes Abi")
app.geometry("1200x700")

sidebar = ctk.CTkFrame(app, width=200, fg_color="#111111")
sidebar.pack(side="left", fill="y")
sidebar.pack_propagate(False)

logo_label = ctk.CTkLabel(sidebar, text="Moto Partes Abi",
                           font=ctk.CTkFont(size=14, weight="bold"),
                           text_color="#FFFFFF")
logo_label.pack(pady=20, padx=10)

botones = ["⬛  Panel", "📦  Inventario", "🛒  Ventas", "🕐  Apartados",
           "👥  Clientes", "🚚  Proveedores", "🏪  Sucursales",
           "📊  Reportes", "⚙️  Configuración"]

for boton in botones:
    btn = ctk.CTkButton(sidebar, text=boton, fg_color="transparent",
                        text_color="#AAAAAA", hover_color="#222222",
                        anchor="w", height=36)
    btn.pack(fill="x", padx=8, pady=2)

main_frame = ctk.CTkFrame(app, fg_color="#0f0f0f")
main_frame.pack(side="left", fill="both", expand=True)

topbar = ctk.CTkFrame(main_frame, height=50, fg_color="#1a1a1a")
topbar.pack(fill="x", side="top")
topbar.pack_propagate(False)

titulo = ctk.CTkLabel(topbar, text="Panel Principal",
                      font=ctk.CTkFont(size=16, weight="bold"),
                      text_color="#FFFFFF")
titulo.pack(side="left", padx=20, pady=10)

sucursal = ctk.CTkLabel(topbar, text="📍 Sucursal Matriz",
                        text_color="#E8751A")
sucursal.pack(side="right", padx=20)

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

alertas_label = ctk.CTkLabel(content, text="⚠️  Alertas Críticas",
                              font=ctk.CTkFont(size=14, weight="bold"),
                              text_color="#E8751A")
alertas_label.pack(anchor="w", pady=(20, 8))

alertas_frame = ctk.CTkFrame(content, fg_color="#1a1a1a", corner_radius=10)
alertas_frame.pack(fill="x")

sin_alertas = ctk.CTkLabel(alertas_frame, text="Sin alertas por el momento",
                            text_color="#555555",
                            font=ctk.CTkFont(size=12))
sin_alertas.pack(pady=20)

app.mainloop()