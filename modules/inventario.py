import customtkinter as ctk
from database.db import conectar

def mostrar_inventario(frame):
    content = ctk.CTkFrame(frame, fg_color="#0f0f0f")
    content.pack(fill="both", expand=True, padx=20, pady=20)

    ctk.CTkLabel(content, text="Inventario",
                 font=ctk.CTkFont(size=18, weight="bold"),
                 text_color="#FFFFFF").pack(anchor="w", pady=(0,10))

    btn_agregar = ctk.CTkButton(content, text="+ Agregar Producto",
                                fg_color="#E8751A", hover_color="#c45e0e",
                                text_color="#FFFFFF")
    btn_agregar.pack(anchor="w", pady=(0,15))

    tabla = ctk.CTkFrame(content, fg_color="#1a1a1a", corner_radius=10)
    tabla.pack(fill="both", expand=True)

    ctk.CTkLabel(tabla, text="Sin productos registrados",
                 text_color="#555555").pack(pady=40)
