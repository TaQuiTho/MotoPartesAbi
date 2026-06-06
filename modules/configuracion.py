import customtkinter as ctk
from database.db import conectar
import json
import os

CONFIG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "config", "settings.json")

def cargar_config():
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, "r") as f:
            return json.load(f)
    return {
        "nombre_negocio": "Moto Partes Abi",
        "moneda": "MXN",
        "idioma": "Español",
        "stock_minimo": 5,
        "tema": "dark"
    }

def guardar_config(config):
    with open(CONFIG_PATH, "w") as f:
        json.dump(config, f, indent=4)

def mostrar_configuracion(frame, aplicar_tema=None):
    config = cargar_config()

    content = ctk.CTkFrame(frame, fg_color="#0f0f0f")
    content.pack(fill="both", expand=True, padx=20, pady=20)

    ctk.CTkLabel(content, text="Configuración",
                 font=ctk.CTkFont(size=18, weight="bold"),
                 text_color="#FFFFFF").pack(anchor="w", pady=(0,20))

    panel = ctk.CTkFrame(content, fg_color="#1a1a1a", corner_radius=10)
    panel.pack(fill="x", pady=(0,15))

    ctk.CTkLabel(panel, text="General",
                 font=ctk.CTkFont(size=13, weight="bold"),
                 text_color="#E8751A").pack(anchor="w", padx=15, pady=(12,8))

    campos = [
        ("Nombre del negocio", "nombre_negocio"),
        ("Moneda", "moneda"),
        ("Stock mínimo por defecto", "stock_minimo"),
    ]

    entradas = {}
    for label, key in campos:
        fila = ctk.CTkFrame(panel, fg_color="transparent")
        fila.pack(fill="x", padx=15, pady=4)
        ctk.CTkLabel(fila, text=label, text_color="#AAAAAA",
                     width=200, anchor="w").pack(side="left")
        entrada = ctk.CTkEntry(fila, width=250)
        entrada.insert(0, str(config.get(key, "")))
        entrada.pack(side="left")
        entradas[key] = entrada

    fila_idioma = ctk.CTkFrame(panel, fg_color="transparent")
    fila_idioma.pack(fill="x", padx=15, pady=4)
    ctk.CTkLabel(fila_idioma, text="Idioma", text_color="#AAAAAA",
                 width=200, anchor="w").pack(side="left")
    idioma_var = ctk.StringVar(value=config.get("idioma", "Español"))
    ctk.CTkOptionMenu(fila_idioma, values=["Español", "English"],
                      variable=idioma_var, width=250).pack(side="left")

    fila_tema = ctk.CTkFrame(panel, fg_color="transparent")
    fila_tema.pack(fill="x", padx=15, pady=(4,12))
    ctk.CTkLabel(fila_tema, text="Tema", text_color="#AAAAAA",
                 width=200, anchor="w").pack(side="left")
    tema_var = ctk.StringVar(value=config.get("tema", "dark"))
    ctk.CTkOptionMenu(fila_tema, values=["dark", "light"],
                      variable=tema_var, width=250).pack(side="left")

    def guardar(event=None):
        nueva_config = {
            "nombre_negocio": entradas["nombre_negocio"].get(),
            "moneda": entradas["moneda"].get(),
            "stock_minimo": int(entradas["stock_minimo"].get() or 5),
            "idioma": idioma_var.get(),
            "tema": tema_var.get(),
        }
        guardar_config(nueva_config)

        if aplicar_tema:
            aplicar_tema(nueva_config["tema"])
            return

        exito = ctk.CTkToplevel()
        exito.title("Guardado")
        exito.geometry("300x130")
        exito.grab_set()
        ctk.CTkLabel(exito, text="✅ Configuración guardada",
                     text_color="#FFFFFF",
                     font=ctk.CTkFont(size=14)).pack(pady=30)
        ctk.CTkButton(exito, text="OK", fg_color="#E8751A",
                      command=exito.destroy).pack()

    ctk.CTkButton(content, text="Guardar Configuración",
                  fg_color="#E8751A", hover_color="#c45e0e",
                  command=guardar).pack(anchor="w", pady=15)