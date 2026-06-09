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

def mostrar_clientes(frame):
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
        ctk.CTkLabel(c, text=t("clientes", idioma),
                     font=ctk.CTkFont(size=18, weight="bold"),
                     text_color="#FFFFFF").pack(anchor="w", pady=(0,10))

        ctk.CTkButton(c, text=f"+ {t('nuevo_cliente', idioma)}",
                      fg_color="#E8751A", hover_color="#c45e0e",
                      text_color="#FFFFFF",
                      command=lambda: nuevo_cliente(recargar)).pack(anchor="w", pady=(0,15))

        mostrar_tabla(c, recargar)

    construir(content)

def mostrar_tabla(content, recargar):
    from config.translations import t
    idioma = get_idioma()
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT id, nombre, telefono, email FROM clientes ORDER BY nombre")
    clientes = cursor.fetchall()
    conn.close()

    tabla = ctk.CTkScrollableFrame(content, fg_color="#1a1a1a", corner_radius=10)
    tabla.pack(fill="both", expand=True)

    if not clientes:
        ctk.CTkLabel(tabla, text=t("sin_clientes", idioma),
                     text_color="#555555").pack(pady=40)
    else:
        for c in clientes:
            fila = ctk.CTkFrame(tabla, fg_color="#222222", corner_radius=6)
            fila.pack(fill="x", padx=8, pady=3)

            ctk.CTkLabel(fila, text=c[1], text_color="#FFFFFF",
                         width=200, anchor="w").pack(side="left", padx=6)
            ctk.CTkLabel(fila, text=c[2] or "", text_color="#888888",
                         width=130, anchor="w").pack(side="left")
            ctk.CTkLabel(fila, text=c[3] or "", text_color="#888888",
                         width=180, anchor="w").pack(side="left")

            ctk.CTkButton(fila, text=t("editar", idioma), width=60, height=26,
                          fg_color="#333333", hover_color="#444444",
                          command=lambda cid=c[0]: editar_cliente(cid, recargar)
                          ).pack(side="right", padx=4, pady=4)

            ctk.CTkButton(fila, text=t("borrar", idioma), width=60, height=26,
                          fg_color="#7a1a1a", hover_color="#a02020",
                          command=lambda cid=c[0]: borrar_cliente(cid, recargar)
                          ).pack(side="right", padx=4, pady=4)

def nuevo_cliente(callback):
    from config.translations import t
    idioma = get_idioma()
    ventana = ctk.CTkToplevel()
    ventana.title(t("nuevo_cliente", idioma))
    ventana.geometry("420x500")
    ventana.grab_set()

    ctk.CTkLabel(ventana, text=t("nuevo_cliente", idioma),
                 font=ctk.CTkFont(size=16, weight="bold")).pack(pady=20)

    campos_keys = ["nombre", "telefono", "email", "direccion", "notas"]
    entradas = {}

    for key in campos_keys:
        label = t(key, idioma)
        ctk.CTkLabel(ventana, text=label, text_color="#AAAAAA").pack(anchor="w", padx=30)
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
        cursor.execute("INSERT INTO clientes (nombre, telefono, email, direccion, notas) VALUES (?, ?, ?, ?, ?)",
                       (entradas["nombre"].get(), entradas["telefono"].get(),
                        entradas["email"].get(), entradas["direccion"].get(), entradas["notas"].get()))
        conn.commit()
        conn.close()
        ventana.destroy()
        callback()

    ventana.bind("<Return>", guardar)
    ctk.CTkButton(ventana, text=t("guardar", idioma), fg_color="#E8751A",
                  hover_color="#c45e0e", command=guardar).pack(pady=15)

def editar_cliente(cliente_id, callback):
    from config.translations import t
    idioma = get_idioma()
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM clientes WHERE id=?", (cliente_id,))
    c = cursor.fetchone()
    conn.close()

    ventana = ctk.CTkToplevel()
    ventana.title(t("editar_cliente", idioma))
    ventana.geometry("420x500")
    ventana.grab_set()

    ctk.CTkLabel(ventana, text=t("editar_cliente", idioma),
                 font=ctk.CTkFont(size=16, weight="bold")).pack(pady=20)

    campos_keys = ["nombre", "telefono", "email", "direccion", "notas"]
    valores = [c[1], c[2], c[3], c[4], c[5]]
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
        cursor.execute("UPDATE clientes SET nombre=?, telefono=?, email=?, direccion=?, notas=? WHERE id=?",
                       (entradas["nombre"].get(), entradas["telefono"].get(),
                        entradas["email"].get(), entradas["direccion"].get(),
                        entradas["notas"].get(), cliente_id))
        conn.commit()
        conn.close()
        ventana.destroy()
        callback()

    ventana.bind("<Return>", guardar)
    ctk.CTkButton(ventana, text=t("guardar_cambios", idioma), fg_color="#E8751A",
                  hover_color="#c45e0e", command=guardar).pack(pady=15)

def borrar_cliente(cliente_id, callback):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM clientes WHERE id=?", (cliente_id,))
    conn.commit()
    conn.close()
    callback()