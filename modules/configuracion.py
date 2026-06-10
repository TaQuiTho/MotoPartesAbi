import customtkinter as ctk
import json
import os
import shutil
import tkinter.filedialog as filedialog
from datetime import datetime


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_DIR = os.path.join(BASE_DIR, "config")
DATABASE_DIR = os.path.join(BASE_DIR, "database")

CONFIG_PATH = os.path.join(CONFIG_DIR, "settings.json")
DB_PATH = os.path.join(DATABASE_DIR, "motopartes.db")


CONFIG_DEFAULT = {
    "nombre_negocio": "Moto Partes Abi",
    "moneda": "MXN",
    "idioma": "Español",
    "stock_minimo": 5,
    "tema": "dark",
    "ruta_respaldo": ""
}


def asegurar_config():
    os.makedirs(CONFIG_DIR, exist_ok=True)

    if not os.path.exists(CONFIG_PATH):
        guardar_config(CONFIG_DEFAULT.copy())


def cargar_config():
    asegurar_config()

    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            config = json.load(f)

        for key, value in CONFIG_DEFAULT.items():
            if key not in config:
                config[key] = value

        return config

    except Exception:
        guardar_config(CONFIG_DEFAULT.copy())
        return CONFIG_DEFAULT.copy()


def guardar_config(config):
    os.makedirs(CONFIG_DIR, exist_ok=True)

    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=4, ensure_ascii=False)


def get_idioma():
    try:
        return cargar_config().get("idioma", "Español")
    except Exception:
        return "Español"


def entero_seguro(valor, defecto=5):
    try:
        numero = int(str(valor).strip())
        return numero
    except Exception:
        return defecto


def mostrar_alerta(titulo, mensaje, parent=None):
    ventana = ctk.CTkToplevel(parent) if parent else ctk.CTkToplevel()
    ventana.title(titulo)
    ventana.geometry("380x170")
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


def hacer_respaldo(ruta):
    if not ruta:
        return False, "No seleccionaste una carpeta."

    if not os.path.exists(ruta):
        return False, "La carpeta de respaldo no existe."

    if not os.path.exists(DB_PATH):
        return False, "No se encontró la base de datos."

    try:
        nombre = f"motopartes_respaldo_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
        destino = os.path.join(ruta, nombre)

        shutil.copy2(DB_PATH, destino)

        return True, f"Respaldo creado:\n{nombre}"

    except PermissionError:
        return False, "No tienes permiso para guardar en esa carpeta."

    except Exception as e:
        return False, f"No se pudo crear el respaldo:\n{e}"


def restaurar_respaldo(ruta_archivo):
    if not ruta_archivo:
        return False, "No seleccionaste ningún archivo."

    if not os.path.exists(ruta_archivo):
        return False, "El archivo seleccionado no existe."

    if not ruta_archivo.lower().endswith(".db"):
        return False, "Selecciona un archivo .db válido."

    try:
        os.makedirs(DATABASE_DIR, exist_ok=True)

        if os.path.exists(DB_PATH):
            respaldo_actual = os.path.join(
                DATABASE_DIR,
                f"motopartes_antes_restaurar_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
            )
            shutil.copy2(DB_PATH, respaldo_actual)

        shutil.copy2(ruta_archivo, DB_PATH)

        return True, "Base de datos restaurada correctamente.\nReinicia la aplicación."

    except PermissionError:
        return False, "No tienes permiso para restaurar la base de datos."

    except Exception as e:
        return False, f"No se pudo restaurar:\n{e}"


def mostrar_configuracion(frame, aplicar_tema=None):
    from config.translations import t

    idioma = get_idioma()
    config = cargar_config()

    content = ctk.CTkFrame(frame, fg_color="#0f0f0f")
    content.pack(fill="both", expand=True, padx=20, pady=20)

    ctk.CTkLabel(
        content,
        text=t("configuracion", idioma),
        font=ctk.CTkFont(size=18, weight="bold"),
        text_color="#FFFFFF"
    ).pack(anchor="w", pady=(0, 20))

    panel = ctk.CTkFrame(content, fg_color="#1a1a1a", corner_radius=10)
    panel.pack(fill="x", pady=(0, 15))

    ctk.CTkLabel(
        panel,
        text="General",
        font=ctk.CTkFont(size=13, weight="bold"),
        text_color="#E8751A"
    ).pack(anchor="w", padx=15, pady=(12, 8))

    campos = [
        (t("nombre_negocio", idioma), "nombre_negocio"),
        (t("moneda", idioma), "moneda"),
        (t("stock_minimo", idioma), "stock_minimo"),
    ]

    entradas = {}

    for label, key in campos:
        fila = ctk.CTkFrame(panel, fg_color="transparent")
        fila.pack(fill="x", padx=15, pady=4)

        ctk.CTkLabel(
            fila,
            text=label,
            text_color="#AAAAAA",
            width=200,
            anchor="w"
        ).pack(side="left")

        entrada = ctk.CTkEntry(fila, width=250)
        entrada.insert(0, str(config.get(key, CONFIG_DEFAULT.get(key, ""))))
        entrada.pack(side="left")

        entradas[key] = entrada

    fila_idioma = ctk.CTkFrame(panel, fg_color="transparent")
    fila_idioma.pack(fill="x", padx=15, pady=4)

    ctk.CTkLabel(
        fila_idioma,
        text=t("idioma", idioma),
        text_color="#AAAAAA",
        width=200,
        anchor="w"
    ).pack(side="left")

    idioma_var = ctk.StringVar(value=config.get("idioma", "Español"))

    ctk.CTkOptionMenu(
        fila_idioma,
        values=["Español", "English"],
        variable=idioma_var,
        width=250
    ).pack(side="left")

    fila_tema = ctk.CTkFrame(panel, fg_color="transparent")
    fila_tema.pack(fill="x", padx=15, pady=(4, 12))

    ctk.CTkLabel(
        fila_tema,
        text=t("tema", idioma),
        text_color="#AAAAAA",
        width=200,
        anchor="w"
    ).pack(side="left")

    tema_var = ctk.StringVar(value=config.get("tema", "dark"))

    ctk.CTkOptionMenu(
        fila_tema,
        values=["dark", "light"],
        variable=tema_var,
        width=250
    ).pack(side="left")

    panel_respaldo = ctk.CTkFrame(content, fg_color="#1a1a1a", corner_radius=10)
    panel_respaldo.pack(fill="x", pady=(0, 15))

    ctk.CTkLabel(
        panel_respaldo,
        text=t("respaldo_nube", idioma),
        font=ctk.CTkFont(size=13, weight="bold"),
        text_color="#E8751A"
    ).pack(anchor="w", padx=15, pady=(12, 8))

    fila_ruta = ctk.CTkFrame(panel_respaldo, fg_color="transparent")
    fila_ruta.pack(fill="x", padx=15, pady=4)

    ctk.CTkLabel(
        fila_ruta,
        text=t("carpeta_respaldo", idioma),
        text_color="#AAAAAA",
        width=200,
        anchor="w"
    ).pack(side="left")

    entrada_ruta = ctk.CTkEntry(fila_ruta, width=250)
    entrada_ruta.insert(0, config.get("ruta_respaldo", ""))
    entrada_ruta.pack(side="left", padx=(0, 8))

    def seleccionar_carpeta():
        carpeta = filedialog.askdirectory(title="Selecciona carpeta")
        if carpeta:
            entrada_ruta.delete(0, "end")
            entrada_ruta.insert(0, carpeta)

    ctk.CTkButton(
        fila_ruta,
        text=t("seleccionar", idioma),
        width=90,
        fg_color="#333333",
        hover_color="#444444",
        command=seleccionar_carpeta
    ).pack(side="left")

    fila_respaldo_btn = ctk.CTkFrame(panel_respaldo, fg_color="transparent")
    fila_respaldo_btn.pack(fill="x", padx=15, pady=(8, 12))

    respaldo_status = ctk.CTkLabel(
        fila_respaldo_btn,
        text="",
        text_color="#888888",
        font=ctk.CTkFont(size=11)
    )
    respaldo_status.pack(side="right", padx=8)

    def respaldar_ahora():
        ok, mensaje = hacer_respaldo(entrada_ruta.get().strip())

        if ok:
            respaldo_status.configure(text="✅ OK", text_color="#3B6D11")
            mostrar_alerta("Respaldo", mensaje, content)
        else:
            respaldo_status.configure(text="❌ Error", text_color="#A32D2D")
            mostrar_alerta("Error", mensaje, content)

    ctk.CTkButton(
        fila_respaldo_btn,
        text=t("respaldar_ahora", idioma),
        width=140,
        fg_color="#1a3a1a",
        hover_color="#2a5a2a",
        command=respaldar_ahora
    ).pack(side="left")

    def restaurar():
        archivo = filedialog.askopenfilename(
            title="Selecciona respaldo",
            filetypes=[("SQLite DB", "*.db"), ("Todos los archivos", "*.*")]
        )

        ok, mensaje = restaurar_respaldo(archivo)

        if ok:
            mostrar_alerta("Restaurar", mensaje, content)
        else:
            mostrar_alerta("Error", mensaje, content)

    ctk.CTkButton(
        fila_respaldo_btn,
        text="Restaurar respaldo",
        width=150,
        fg_color="#333333",
        hover_color="#444444",
        command=restaurar
    ).pack(side="left", padx=8)

    def guardar(event=None):
        nombre_negocio = entradas["nombre_negocio"].get().strip() or CONFIG_DEFAULT["nombre_negocio"]
        moneda = entradas["moneda"].get().strip() or CONFIG_DEFAULT["moneda"]
        stock_minimo = entero_seguro(
            entradas["stock_minimo"].get(),
            CONFIG_DEFAULT["stock_minimo"]
        )

        if stock_minimo < 0:
            mostrar_alerta(
                "Error",
                "El stock mínimo no puede ser negativo.",
                content
            )
            return

        nueva_config = {
            "nombre_negocio": nombre_negocio,
            "moneda": moneda,
            "stock_minimo": stock_minimo,
            "idioma": idioma_var.get(),
            "tema": tema_var.get(),
            "ruta_respaldo": entrada_ruta.get().strip(),
        }

        try:
            guardar_config(nueva_config)

            if aplicar_tema:
                aplicar_tema(nueva_config["tema"], nueva_config["idioma"])
                return

            mostrar_alerta(
                "OK",
                t("config_guardada", idioma),
                content
            )

        except Exception as e:
            mostrar_alerta(
                "Error",
                f"No se pudo guardar la configuración:\n{e}",
                content
            )

    ctk.CTkButton(
        content,
        text=t("guardar_config", idioma),
        fg_color="#E8751A",
        hover_color="#c45e0e",
        command=guardar
    ).pack(anchor="w", pady=15)