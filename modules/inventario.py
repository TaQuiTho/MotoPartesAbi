import customtkinter as ctk
from database.db import conectar
from config.translations import t

def get_idioma():
    try:
        import json, os
        config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "config", "settings.json")
        with open(config_path) as f:
            return json.load(f).get("idioma", "Español")
    except:
        return "Español"

def agregar_producto(callback):
    idioma = get_idioma()
    ventana = ctk.CTkToplevel()
    ventana.title(t("agregar_producto", idioma))
    ventana.geometry("420x700")
    ventana.grab_set()

    ctk.CTkLabel(ventana, text=t("agregar_producto", idioma),
                 font=ctk.CTkFont(size=16, weight="bold")).pack(pady=20)

    scroll = ctk.CTkFrame(ventana, fg_color="transparent")
    scroll.pack(fill="both", expand=True, padx=20)

    campos_keys = ["nombre", "marca", "sku", "cantidad", "precio_costo", "precio_menudeo", "precio_mayoreo", "descripcion"]
    campos_labels = [t(k, idioma) for k in campos_keys]
    entradas = {}

    for campo in campos_labels:
        ctk.CTkLabel(scroll, text=campo, text_color="#AAAAAA").pack(anchor="w")
        entrada = ctk.CTkEntry(scroll, width=360)
        entrada.pack(pady=(2,10))
        entradas[campo] = entrada

    def guardar(event=None):
        nombre_key = t("nombre", idioma)
        cantidad_key = t("cantidad", idioma)
        menudeo_key = t("precio_menudeo", idioma)

        campos_requeridos = {
            nombre_key: entradas[nombre_key].get(),
            cantidad_key: entradas[cantidad_key].get(),
            menudeo_key: entradas[menudeo_key].get(),
        }

        for campo, valor in campos_requeridos.items():
            if not valor.strip():
                error = ctk.CTkToplevel()
                error.title(t("campo_requerido", idioma))
                error.geometry("300x150")
                error.grab_set()
                ctk.CTkLabel(error, text=f"{t('falta_llenar', idioma)}: {campo}",
                             text_color="#E8751A",
                             font=ctk.CTkFont(size=14)).pack(pady=30)
                ctk.CTkButton(error, text="OK", fg_color="#E8751A",
                              command=error.destroy).pack()
                return

        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO productos (nombre, marca, sku, cantidad, precio_costo,
                                   precio_menudeo, precio_mayoreo, descripcion)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            entradas[t("nombre", idioma)].get(),
            entradas[t("marca", idioma)].get(),
            entradas[t("sku", idioma)].get(),
            int(entradas[t("cantidad", idioma)].get() or 0),
            float(entradas[t("precio_costo", idioma)].get() or 0),
            float(entradas[t("precio_menudeo", idioma)].get() or 0),
            float(entradas[t("precio_mayoreo", idioma)].get() or 0),
            entradas[t("descripcion", idioma)].get(),
        ))
        conn.commit()
        conn.close()
        ventana.destroy()
        callback()

    ventana.bind("<Return>", guardar)
    ctk.CTkButton(ventana, text=t("guardar", idioma), fg_color="#E8751A",
                  hover_color="#c45e0e", command=guardar).pack(pady=15)

def editar_producto(producto_id, callback):
    idioma = get_idioma()
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM productos WHERE id=?", (producto_id,))
    p = cursor.fetchone()
    conn.close()

    ventana = ctk.CTkToplevel()
    ventana.title(t("editar_producto", idioma))
    ventana.geometry("420x700")
    ventana.grab_set()

    ctk.CTkLabel(ventana, text=t("editar_producto", idioma),
                 font=ctk.CTkFont(size=16, weight="bold")).pack(pady=20)

    scroll = ctk.CTkFrame(ventana, fg_color="transparent")
    scroll.pack(fill="both", expand=True, padx=20)

    campos_keys = ["nombre", "marca", "sku", "cantidad", "precio_costo", "precio_menudeo", "precio_mayoreo", "descripcion"]
    campos_labels = [t(k, idioma) for k in campos_keys]
    valores = [p[1], p[2], p[3], p[4], p[5], p[6], p[7], p[8] if len(p) > 8 else ""]
    entradas = {}

    for campo, valor in zip(campos_labels, valores):
        ctk.CTkLabel(scroll, text=campo, text_color="#AAAAAA").pack(anchor="w")
        entrada = ctk.CTkEntry(scroll, width=360)
        entrada.insert(0, str(valor) if valor else "")
        entrada.pack(pady=(2,10))
        entradas[campo] = entrada

    def guardar(event=None):
        nombre_key = t("nombre", idioma)
        cantidad_key = t("cantidad", idioma)
        menudeo_key = t("precio_menudeo", idioma)

        campos_requeridos = {
            nombre_key: entradas[nombre_key].get(),
            cantidad_key: entradas[cantidad_key].get(),
            menudeo_key: entradas[menudeo_key].get(),
        }

        for campo, valor in campos_requeridos.items():
            if not valor.strip():
                error = ctk.CTkToplevel()
                error.title(t("campo_requerido", idioma))
                error.geometry("300x150")
                error.grab_set()
                ctk.CTkLabel(error, text=f"{t('falta_llenar', idioma)}: {campo}",
                             text_color="#E8751A",
                             font=ctk.CTkFont(size=14)).pack(pady=30)
                ctk.CTkButton(error, text="OK", fg_color="#E8751A",
                              command=error.destroy).pack()
                return

        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE productos SET nombre=?, marca=?, sku=?, cantidad=?,
            precio_costo=?, precio_menudeo=?, precio_mayoreo=?, descripcion=?
            WHERE id=?
        """, (
            entradas[t("nombre", idioma)].get(),
            entradas[t("marca", idioma)].get(),
            entradas[t("sku", idioma)].get(),
            int(entradas[t("cantidad", idioma)].get() or 0),
            float(entradas[t("precio_costo", idioma)].get() or 0),
            float(entradas[t("precio_menudeo", idioma)].get() or 0),
            float(entradas[t("precio_mayoreo", idioma)].get() or 0),
            entradas[t("descripcion", idioma)].get(),
            producto_id,
        ))
        conn.commit()
        conn.close()
        ventana.destroy()
        callback()

    ventana.bind("<Return>", guardar)
    ctk.CTkButton(ventana, text=t("guardar_cambios", idioma), fg_color="#E8751A",
                  hover_color="#c45e0e", command=guardar).pack(pady=15)

def borrar_producto(producto_id, callback):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM productos WHERE id=?", (producto_id,))
    conn.commit()
    conn.close()
    callback()

def mostrar_inventario(frame):
    idioma = get_idioma()
    content = ctk.CTkFrame(frame, fg_color="#0f0f0f")
    content.pack(fill="both", expand=True, padx=20, pady=20)

    def recargar():
        for widget in content.winfo_children():
            widget.destroy()
        construir(content)

    def construir(c):
        ctk.CTkLabel(c, text=t("inventario", idioma),
                     font=ctk.CTkFont(size=18, weight="bold"),
                     text_color="#FFFFFF").pack(anchor="w", pady=(0,10))

        ctk.CTkButton(c, text=f"+ {t('agregar_producto', idioma)}",
                      fg_color="#E8751A", hover_color="#c45e0e",
                      text_color="#FFFFFF",
                      command=lambda: agregar_producto(recargar)).pack(anchor="w", pady=(0,15))

        mostrar_tabla(c, recargar)

    construir(content)

def mostrar_tabla(content, recargar):
    idioma = get_idioma()
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT id, nombre, marca, sku, cantidad, precio_menudeo FROM productos")
    productos = cursor.fetchall()
    conn.close()

    tabla = ctk.CTkScrollableFrame(content, fg_color="#1a1a1a", corner_radius=10)
    tabla.pack(fill="both", expand=True)

    if not productos:
        ctk.CTkLabel(tabla, text=t("sin_productos_reg", idioma),
                     text_color="#555555").pack(pady=40)
    else:
        for p in productos:
            fila = ctk.CTkFrame(tabla, fg_color="#222222", corner_radius=6)
            fila.pack(fill="x", padx=8, pady=3)

            ctk.CTkLabel(fila, text=p[1], text_color="#FFFFFF",
                         width=180, anchor="w").pack(side="left", padx=6)
            ctk.CTkLabel(fila, text=p[2] or "", text_color="#888888",
                         width=100, anchor="w").pack(side="left")
            ctk.CTkLabel(fila, text=p[3] or "", text_color="#888888",
                         width=90, anchor="w").pack(side="left")
            ctk.CTkLabel(fila, text=str(p[4]), text_color="#E8751A",
                         width=50, anchor="w").pack(side="left")
            ctk.CTkLabel(fila, text=f"${p[5]:.2f}", text_color="#AAAAAA",
                         width=80, anchor="w").pack(side="left")

            ctk.CTkButton(fila, text=t("editar", idioma), width=60, height=26,
                          fg_color="#333333", hover_color="#444444",
                          command=lambda pid=p[0]: editar_producto(pid, recargar)
                          ).pack(side="right", padx=4, pady=4)

            ctk.CTkButton(fila, text=t("borrar", idioma), width=60, height=26,
                          fg_color="#7a1a1a", hover_color="#a02020",
                          command=lambda pid=p[0]: borrar_producto(pid, recargar)
                          ).pack(side="right", padx=4, pady=4)