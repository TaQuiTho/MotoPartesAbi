import customtkinter as ctk
from database.db import conectar

def agregar_producto(callback):
    ventana = ctk.CTkToplevel()
    ventana.title("Agregar Producto")
    ventana.geometry("420x550")
    ventana.grab_set()

    ctk.CTkLabel(ventana, text="Agregar Producto",
                 font=ctk.CTkFont(size=16, weight="bold")).pack(pady=20)

    scroll = ctk.CTkScrollableFrame(ventana, fg_color="transparent")
    scroll.pack(fill="both", expand=True, padx=20)

    campos = ["Nombre", "Marca", "SKU", "Cantidad", "Precio Costo",
              "Precio Menudeo", "Precio Mayoreo", "Descripción"]
    entradas = {}

    for campo in campos:
        ctk.CTkLabel(scroll, text=campo, text_color="#AAAAAA").pack(anchor="w")
        entrada = ctk.CTkEntry(scroll, width=360)
        entrada.pack(pady=(2,10))
        entradas[campo] = entrada

    def guardar():
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO productos (nombre, marca, sku, cantidad, precio_costo,
                                   precio_menudeo, precio_mayoreo, descripcion)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            entradas["Nombre"].get(),
            entradas["Marca"].get(),
            entradas["SKU"].get(),
            int(entradas["Cantidad"].get() or 0),
            float(entradas["Precio Costo"].get() or 0),
            float(entradas["Precio Menudeo"].get() or 0),
            float(entradas["Precio Mayoreo"].get() or 0),
            entradas["Descripción"].get(),
        ))
        conn.commit()
        conn.close()
        ventana.destroy()
        callback()

    ctk.CTkButton(ventana, text="Guardar", fg_color="#E8751A",
                  hover_color="#c45e0e", command=guardar).pack(pady=15)

def editar_producto(producto_id, callback):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM productos WHERE id=?", (producto_id,))
    p = cursor.fetchone()
    conn.close()

    ventana = ctk.CTkToplevel()
    ventana.title("Editar Producto")
    ventana.geometry("420x550")
    ventana.grab_set()

    ctk.CTkLabel(ventana, text="Editar Producto",
                 font=ctk.CTkFont(size=16, weight="bold")).pack(pady=20)

    scroll = ctk.CTkScrollableFrame(ventana, fg_color="transparent")
    scroll.pack(fill="both", expand=True, padx=20)

    campos = ["Nombre", "Marca", "SKU", "Cantidad", "Precio Costo",
              "Precio Menudeo", "Precio Mayoreo", "Descripción"]
    valores = [p[1], p[2], p[3], p[4], p[5], p[6], p[7], p[8] if len(p) > 8 else ""]
    entradas = {}

    for campo, valor in zip(campos, valores):
        ctk.CTkLabel(scroll, text=campo, text_color="#AAAAAA").pack(anchor="w")
        entrada = ctk.CTkEntry(scroll, width=360)
        entrada.insert(0, str(valor) if valor else "")
        entrada.pack(pady=(2,10))
        entradas[campo] = entrada

    def guardar():
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE productos SET nombre=?, marca=?, sku=?, cantidad=?,
            precio_costo=?, precio_menudeo=?, precio_mayoreo=?, descripcion=?
            WHERE id=?
        """, (
            entradas["Nombre"].get(),
            entradas["Marca"].get(),
            entradas["SKU"].get(),
            int(entradas["Cantidad"].get() or 0),
            float(entradas["Precio Costo"].get() or 0),
            float(entradas["Precio Menudeo"].get() or 0),
            float(entradas["Precio Mayoreo"].get() or 0),
            entradas["Descripción"].get(),
            producto_id,
        ))
        conn.commit()
        conn.close()
        ventana.destroy()
        callback()

    ctk.CTkButton(ventana, text="Guardar Cambios", fg_color="#E8751A",
                  hover_color="#c45e0e", command=guardar).pack(pady=15)

def mostrar_inventario(frame):
    content = ctk.CTkFrame(frame, fg_color="#0f0f0f")
    content.pack(fill="both", expand=True, padx=20, pady=20)

    ctk.CTkLabel(content, text="Inventario",
                 font=ctk.CTkFont(size=18, weight="bold"),
                 text_color="#FFFFFF").pack(anchor="w", pady=(0,10))

    def recargar():
        for widget in content.winfo_children():
            widget.destroy()
        construir(content)

    def construir(c):
        ctk.CTkLabel(c, text="Inventario",
                     font=ctk.CTkFont(size=18, weight="bold"),
                     text_color="#FFFFFF").pack(anchor="w", pady=(0,10))

        ctk.CTkButton(c, text="+ Agregar Producto",
                      fg_color="#E8751A", hover_color="#c45e0e",
                      text_color="#FFFFFF",
                      command=lambda: agregar_producto(recargar)).pack(anchor="w", pady=(0,15))

        mostrar_tabla(c, recargar)

    construir(content)

def mostrar_tabla(content, recargar):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT id, nombre, marca, sku, cantidad, precio_menudeo FROM productos")
    productos = cursor.fetchall()
    conn.close()

    tabla = ctk.CTkScrollableFrame(content, fg_color="#1a1a1a", corner_radius=10)
    tabla.pack(fill="both", expand=True)

    if not productos:
        ctk.CTkLabel(tabla, text="Sin productos registrados",
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

            ctk.CTkButton(fila, text="Editar", width=60, height=26,
                          fg_color="#333333", hover_color="#444444",
                          command=lambda pid=p[0]: editar_producto(pid, recargar)
                          ).pack(side="right", padx=4, pady=4)

            ctk.CTkButton(fila, text="Borrar", width=60, height=26,
                          fg_color="#7a1a1a", hover_color="#a02020",
                          command=lambda pid=p[0]: borrar_producto(pid, recargar)
                          ).pack(side="right", padx=4, pady=4)

def borrar_producto(producto_id, callback):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM productos WHERE id=?", (producto_id,))
    conn.commit()
    conn.close()
    callback()