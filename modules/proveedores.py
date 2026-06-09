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

def mostrar_proveedores(frame):
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
        ctk.CTkLabel(c, text=t("proveedores", idioma),
                     font=ctk.CTkFont(size=18, weight="bold"),
                     text_color="#FFFFFF").pack(anchor="w", pady=(0,10))

        ctk.CTkButton(c, text=f"+ {t('nuevo_proveedor', idioma)}",
                      fg_color="#E8751A", hover_color="#c45e0e",
                      text_color="#FFFFFF",
                      command=lambda: nuevo_proveedor(recargar)).pack(anchor="w", pady=(0,15))

        mostrar_tabla(c, recargar)

    construir(content)

def mostrar_tabla(content, recargar):
    from config.translations import t
    idioma = get_idioma()
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT id, nombre, telefono, email FROM proveedores ORDER BY nombre")
    proveedores = cursor.fetchall()
    conn.close()

    tabla = ctk.CTkScrollableFrame(content, fg_color="#1a1a1a", corner_radius=10)
    tabla.pack(fill="both", expand=True)

    if not proveedores:
        ctk.CTkLabel(tabla, text=t("sin_proveedores", idioma),
                     text_color="#555555").pack(pady=40)
    else:
        for p in proveedores:
            fila = ctk.CTkFrame(tabla, fg_color="#222222", corner_radius=6)
            fila.pack(fill="x", padx=8, pady=3)

            ctk.CTkLabel(fila, text=p[1], text_color="#FFFFFF",
                         width=200, anchor="w").pack(side="left", padx=6)
            ctk.CTkLabel(fila, text=p[2] or "", text_color="#888888",
                         width=130, anchor="w").pack(side="left")
            ctk.CTkLabel(fila, text=p[3] or "", text_color="#888888",
                         width=180, anchor="w").pack(side="left")

            ctk.CTkButton(fila, text=t("editar", idioma), width=60, height=26,
                          fg_color="#333333", hover_color="#444444",
                          command=lambda pid=p[0]: editar_proveedor(pid, recargar)
                          ).pack(side="right", padx=4, pady=4)

            ctk.CTkButton(fila, text=t("borrar", idioma), width=60, height=26,
                          fg_color="#7a1a1a", hover_color="#a02020",
                          command=lambda pid=p[0]: borrar_proveedor(pid, recargar)
                          ).pack(side="right", padx=4, pady=4)

def nuevo_proveedor(callback):
    from config.translations import t
    idioma = get_idioma()
    ventana = ctk.CTkToplevel()
    ventana.title(t("nuevo_proveedor", idioma))
    ventana.geometry("420x500")
    ventana.grab_set()

    ctk.CTkLabel(ventana, text=t("nuevo_proveedor", idioma),
                 font=ctk.CTkFont(size=16, weight="bold")).pack(pady=20)

    campos_keys = ["nombre", "telefono", "email", "direccion", "notas"]
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
        cursor.execute("INSERT INTO proveedores (nombre, telefono, email, direccion, notas) VALUES (?, ?, ?, ?, ?)",
                       (entradas["nombre"].get(), entradas["telefono"].get(),
                        entradas["email"].get(), entradas["direccion"].get(), entradas["notas"].get()))
        conn.commit()
        conn.close()
        ventana.destroy()
        callback()

    ventana.bind("<Return>", guardar)
    ctk.CTkButton(ventana, text=t("guardar", idioma), fg_color="#E8751A",
                  hover_color="#c45e0e", command=guardar).pack(pady=15)

def editar_proveedor(proveedor_id, callback):
    from config.translations import t
    idioma = get_idioma()
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM proveedores WHERE id=?", (proveedor_id,))
    p = cursor.fetchone()
    conn.close()

    ventana = ctk.CTkToplevel()
    ventana.title(t("editar_proveedor", idioma))
    ventana.geometry("420x500")
    ventana.grab_set()

    ctk.CTkLabel(ventana, text=t("editar_proveedor", idioma),
                 font=ctk.CTkFont(size=16, weight="bold")).pack(pady=20)

    campos_keys = ["nombre", "telefono", "email", "direccion", "notas"]
    valores = [p[1], p[2], p[3], p[4], p[5]]
    entradas = {}

    for key, valor in zip(campos_keys, valores):
        ctk.CTkLabel(ventana, text=t(key, idioma), text_color="#AAAAAA").pack(anchor="w", padx=30)
        entrada = ctk.CTkEntry(ventana, width=360)
        entrada.insert(0, str(valor) if valor else "")
        entrada.pack(padx=30, pady=(2,10))
        entradas[key] = entrada

    def guardar(event=None):
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("UPDATE proveedores SET nombre=?, telefono=?, email=?, direccion=?, notas=? WHERE id=?",
                       (entradas["nombre"].get(), entradas["telefono"].get(),
                        entradas["email"].get(), entradas["direccion"].get(),
                        entradas["notas"].get(), proveedor_id))
        conn.commit()
        conn.close()
        ventana.destroy()
        callback()

    ventana.bind("<Return>", guardar)
    ctk.CTkButton(ventana, text=t("guardar_cambios", idioma), fg_color="#E8751A",
                  hover_color="#c45e0e", command=guardar).pack(pady=15)

def borrar_proveedor(proveedor_id, callback):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM proveedores WHERE id=?", (proveedor_id,))
    conn.commit()
    conn.close()
    callback()