import customtkinter as ctk
from database.db import conectar
import json
import os
import shutil
import tkinter.filedialog as filedialog
from datetime import datetime

CONFIG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "config", "settings.json")
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "database", "motopartes.db")

def get_idioma():
    try:
        with open(CONFIG_PATH) as f:
            return json.load(f).get("idioma", "Español")
    except:
        return "Español"

def cargar_config():
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, "r") as f:
            return json.load(f)
    return {
        "nombre_negocio": "Moto Partes Abi",
        "moneda": "MXN",
        "idioma": "Español",
        "stock_minimo": 5,
        "tema": "dark",
        "ruta_respaldo": ""
    }

def guardar_config(config):
    with open(CONFIG_PATH, "w") as f:
        json.dump(config, f, indent=4)

def hacer_respaldo(ruta):
    if not ruta or not os.path.exists(ruta):
        return False
    try:
        nombre = f"motopartes_respaldo_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
        destino = os.path.join(ruta, nombre)
        shutil.copy2(DB_PATH, destino)
        return True
    except:
        return False

def mostrar_configuracion(frame, aplicar_tema=None):
    from config.translations import t
    idioma = get_idioma()
    config = cargar_config()

    content = ctk.CTkFrame(frame, fg_color="#0f0f0f")
    content.pack(fill="both", expand=True, padx=20, pady=20)

    ctk.CTkLabel(content, text=t("configuracion", idioma),
                 font=ctk.CTkFont(size=18, weight="bold"),
                 text_color="#FFFFFF").pack(anchor="w", pady=(0,20))

    panel = ctk.CTkFrame(content, fg_color="#1a1a1a", corner_radius=10)
    panel.pack(fill="x", pady=(0,15))

    ctk.CTkLabel(panel, text="General",
                 font=ctk.CTkFont(size=13, weight="bold"),
                 text_color="#E8751A").pack(anchor="w", padx=15, pady=(12,8))

    campos = [
        (t("nombre_negocio", idioma), "nombre_negocio"),
        (t("moneda", idioma), "moneda"),
        (t("stock_minimo", idioma), "stock_minimo"),
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
    ctk.CTkLabel(fila_idioma, text=t("idioma", idioma), text_color="#AAAAAA",
                 width=200, anchor="w").pack(side="left")
    idioma_var = ctk.StringVar(value=config.get("idioma", "Español"))
    ctk.CTkOptionMenu(fila_idioma, values=["Español", "English"],
                      variable=idioma_var, width=250).pack(side="left")

    fila_tema = ctk.CTkFrame(panel, fg_color="transparent")
    fila_tema.pack(fill="x", padx=15, pady=(4,12))
    ctk.CTkLabel(fila_tema, text=t("tema", idioma), text_color="#AAAAAA",
                 width=200, anchor="w").pack(side="left")
    tema_var = ctk.StringVar(value=config.get("tema", "dark"))
    ctk.CTkOptionMenu(fila_tema, values=["dark", "light"],
                      variable=tema_var, width=250).pack(side="left")

    panel_respaldo = ctk.CTkFrame(content, fg_color="#1a1a1a", corner_radius=10)
    panel_respaldo.pack(fill="x", pady=(0,15))

    ctk.CTkLabel(panel_respaldo, text=t("respaldo_nube", idioma),
                 font=ctk.CTkFont(size=13, weight="bold"),
                 text_color="#E8751A").pack(anchor="w", padx=15, pady=(12,8))

    fila_ruta = ctk.CTkFrame(panel_respaldo, fg_color="transparent")
    fila_ruta.pack(fill="x", padx=15, pady=4)

    ctk.CTkLabel(fila_ruta, text=t("carpeta_respaldo", idioma), text_color="#AAAAAA",
                 width=200, anchor="w").pack(side="left")

    entrada_ruta = ctk.CTkEntry(fila_ruta, width=180)
    entrada_ruta.insert(0, config.get("ruta_respaldo", ""))
    entrada_ruta.pack(side="left", padx=(0,8))

    def seleccionar_carpeta():
        carpeta = filedialog.askdirectory(title="Selecciona carpeta")
        if carpeta:
            entrada_ruta.delete(0, "end")
            entrada_ruta.insert(0, carpeta)

    ctk.CTkButton(fila_ruta, text=t("seleccionar", idioma), width=80,
                  fg_color="#333333", hover_color="#444444",
                  command=seleccionar_carpeta).pack(side="left")

    fila_respaldo_btn = ctk.CTkFrame(panel_respaldo, fg_color="transparent")
    fila_respaldo_btn.pack(fill="x", padx=15, pady=(4,12))

    respaldo_status = ctk.CTkLabel(fila_respaldo_btn, text="",
                                   text_color="#888888", font=ctk.CTkFont(size=11))
    respaldo_status.pack(side="right", padx=8)

    def respaldar_ahora():
        ruta = entrada_ruta.get()
        if hacer_respaldo(ruta):
            respaldo_status.configure(text="✅ OK", text_color="#3B6D11")
        else:
            respaldo_status.configure(text="❌ Error", text_color="#A32D2D")

    ctk.CTkButton(fila_respaldo_btn, text=t("respaldar_ahora", idioma), width=130,
                  fg_color="#1a3a1a", hover_color="#2a5a2a",
                  command=respaldar_ahora).pack(side="left")

    def guardar(event=None):
        nueva_config = {
            "nombre_negocio": entradas["nombre_negocio"].get(),
            "moneda": entradas["moneda"].get(),
            "stock_minimo": int(entradas["stock_minimo"].get() or 5),
            "idioma": idioma_var.get(),
            "tema": tema_var.get(),
            "ruta_respaldo": entrada_ruta.get(),
        }
        guardar_config(nueva_config)

        if aplicar_tema:
            aplicar_tema(nueva_config["tema"], nueva_config["idioma"])
            return

        exito = ctk.CTkToplevel()
        exito.title("OK")
        exito.geometry("300x130")
        exito.grab_set()
        ctk.CTkLabel(exito, text=t("config_guardada", idioma),
                     text_color="#FFFFFF", font=ctk.CTkFont(size=14)).pack(pady=30)
        ctk.CTkButton(exito, text="OK", fg_color="#E8751A", command=exito.destroy).pack()

    ctk.CTkButton(content, text=t("guardar_config", idioma),
                  fg_color="#E8751A", hover_color="#c45e0e",
                  command=guardar).pack(anchor="w", pady=15)