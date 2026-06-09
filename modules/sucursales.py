import customtkinter as ctk
from database.db import conectar
import os

def get_idioma():
    try:
        import json
        config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "config", "settings.json")
        with open(config_path) as f:
            return json.load(f).get("idioma", "Español")
    except:
        return "Español"

def mostrar_sucursales(frame):
    from config.translations import t
    idioma = get_idioma()
    content = ctk.CTkFrame(frame, fg_color="#0f0f0f")
    content.pack(fill="both", expand=True, padx=20, pady=20)

    def recargar():
        for widget in content.winfo_children():
            widget.destroy()
        construir(content)

    def construir(c):
        from config.translations import t
        idioma = get_idioma()
        ctk.CTkLabel(c, text=t("sucursales", idioma),
                     font=ctk.CTkFont(size=18, weight="bold"),
                     text_color="#FFFFFF").pack(anchor="w", pady=(0,10))

        ctk.CTkButton(c, text=f"+ {t('nueva_sucursal', idioma)}",
                      fg_color="#E8751A", hover_color="#c45e0e",
                      text_color="#FFFFFF",
                      command=lambda: nueva_sucursal(recargar)).pack(anchor="w", pady=(0,15))

        mostrar_tabla(c, recargar)

    construir(content)

def mostrar_tabla(content, recargar):
    from config.translations import t
    idioma = get_idioma()
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT id, nombre, direccion, telefono, gerente, activa FROM sucursales ORDER BY nombre")
    sucursales = cursor.fetchall()
    conn.close()

    tabla = ctk.CTkScrollableFrame(content, fg_color="#1a1a1a", corner_radius=10)
    tabla.pack(fill="both", expand=True)

    if not sucursales:
        ctk.CTkLabel(tabla, text=t("sin_sucursales", idioma),
                     text_color="#555555").pack(pady=40)
    else:
        for s in sucursales:
            fila = ctk.CTkFrame(tabla, fg_color="#222222", corner_radius=6)
            fila.pack(fill="x", padx=8, pady=3)

            ctk.CTkLabel(fila, text=s[1], text_color="#FFFFFF",
                         width=150, anchor="w").pack(side="left", padx=6)
            ctk.CTkLabel(fila, text=s[2] or "", text_color="#888888",
                         width=180, anchor="w").pack(side="left")
            ctk.CTkLabel(fila, text=s[4] or "", text_color="#888888",
                         width=130, anchor="w").pack(side="left")

            color = "#3B6D11" if s[5] else "#A32D2D"
            estado = t("activa", idioma) if s[5] else t("inactiva", idioma)
            ctk.CTkLabel(fila, text=estado, text_color=color,
                         width=70, anchor="w").pack(side="left")

            ctk.CTkButton(fila, text=t("editar", idioma), width=60, height=26,
                          fg_color="#333333", hover_color="#444444",
                          command=lambda sid=s[0]: editar_sucursal(sid, recargar)
                          ).pack(side="right", padx=4, pady=4)

            ctk.CTkButton(fila, text=t("borrar", idioma), width=60, height=26,
                          fg_color="#7a1a1a", hover_color="#a02020",
                          command=lambda sid=s[0]: borrar_sucursal(sid, recargar)
                          ).pack(side="right", padx=4, pady=4)

def nueva_sucursal(callback):
    from config.translations import t
    idioma = get_idioma()
    ventana = ctk.CTkToplevel()
    ventana.title(t("nueva_sucursal", idioma))
    ventana.geometry("420x450")
    ventana.grab_set()

    ctk.CTkLabel(ventana, text=t("nueva_sucursal", idioma),
                 font=ctk.CTkFont(size=16, weight="bold")).pack(pady=20)

    campos_keys = ["nombre", "direccion", "telefono", "gerente"]
    entradas = {}

    for key in campos_keys:
        ctk.CTkLabel(ventana, text=t(key, idioma), text_color="#AAAAAA").pack(anchor="w", padx=30)
        entrada = ctk.CTkEntry(ventana, width=360)
        entrada.pack(padx=30, pady=(2,10))
        entradas[key] = entrada

    def guardar(event=None):
        if not entradas["nombre"].get().strip():
            error = ctk.CTkToplevel()
            error.title(t("campo_requerido", idioma))
            error.geometry("300x150")
            error.grab_set()
            ctk.CTkLabel(error, text=f"{t('falta_llenar', idioma)}: {t('nombre', idioma)}",
                         text_color="#E8751A", font=ctk.CTkFont(size=14)).pack(pady=30)
            ctk.CTkButton(error, text="OK", fg_color="#E8751A", command=error.destroy).pack()
            return

        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO sucursales (nombre, direccion, telefono, gerente) VALUES (?, ?, ?, ?)",
                       (entradas["nombre"].get(), entradas["direccion"].get(),
                        entradas["telefono"].get(), entradas["gerente"].get()))
        conn.commit()
        conn.close()
        ventana.destroy()
        callback()

    ventana.bind("<Return>", guardar)
    ctk.CTkButton(ventana, text=t("guardar", idioma), fg_color="#E8751A",
                  hover_color="#c45e0e", command=guardar).pack(pady=15)

def editar_sucursal(sucursal_id, callback):
    from config.translations import t
    idioma = get_idioma()
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM sucursales WHERE id=?", (sucursal_id,))
    s = cursor.fetchone()
    conn.close()

    ventana = ctk.CTkToplevel()
    ventana.title(t("editar_sucursal", idioma))
    ventana.geometry("420x500")
    ventana.grab_set()

    ctk.CTkLabel(ventana, text=t("editar_sucursal", idioma),
                 font=ctk.CTkFont(size=16, weight="bold")).pack(pady=20)

    campos_keys = ["nombre", "direccion", "telefono", "gerente"]
    valores = [s[1], s[2], s[3], s[4]]
    entradas = {}

    for key, valor in zip(campos_keys, valores):
        ctk.CTkLabel(ventana, text=t(key, idioma), text_color="#AAAAAA").pack(anchor="w", padx=30)
        entrada = ctk.CTkEntry(ventana, width=360)
        entrada.insert(0, str(valor) if valor else "")
        entrada.pack(padx=30, pady=(2,10))
        entradas[key] = entrada

    ctk.CTkLabel(ventana, text=t("estado", idioma), text_color="#AAAAAA").pack(anchor="w", padx=30)
    activa_var = ctk.BooleanVar(value=bool(s[5]))
    ctk.CTkCheckBox(ventana, text=t("activa", idioma), variable=activa_var,
                    text_color="#FFFFFF").pack(anchor="w", padx=30, pady=(2,10))

    def guardar(event=None):
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("UPDATE sucursales SET nombre=?, direccion=?, telefono=?, gerente=?, activa=? WHERE id=?",
                       (entradas["nombre"].get(), entradas["direccion"].get(),
                        entradas["telefono"].get(), entradas["gerente"].get(),
                        int(activa_var.get()), sucursal_id))
        conn.commit()
        conn.close()
        ventana.destroy()
        callback()

    ventana.bind("<Return>", guardar)
    ctk.CTkButton(ventana, text=t("guardar_cambios", idioma), fg_color="#E8751A",
                  hover_color="#c45e0e", command=guardar).pack(pady=15)

def borrar_sucursal(sucursal_id, callback):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM sucursales WHERE id=?", (sucursal_id,))
    conn.commit()
    conn.close()
    callback()