import customtkinter as ctk
from database.db import conectar

def agregar_producto(callback):
    ventana = ctk.CTkToplevel()
    ventana.title("Agregar Producto")
    ventana.geometry("400x450")
    ventana.grab_set()

    ctk.CTkLabel(ventana, text="Agregar Producto",
                 font=ctk.CTkFont(size=16, weight="bold")).pack(pady=20)

    campos = ["Nombre", "Marca", "SKU", "Cantidad", "Precio Costo",
              "Precio Menudeo", "Precio Mayoreo"]
    entradas = {}

    for campo in campos:
        ctk.CTkLabel(ventana, text=campo, text_color="#AAAAAA").pack(anchor="w", padx=30)
        entrada = ctk.CTkEntry(ventana, width=340)
        entrada.pack(pady=(2,8))
        entradas[campo] = entrada

    def guardar():
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO productos (nombre, marca, sku, cantidad, precio_costo,
                                   precio_menudeo, precio_mayoreo)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            entradas["Nombre"].get(),
            entradas["Marca"].get(),
            entradas["SKU"].get(),
            int(entradas["Cantidad"].get() or 0),
            float(entradas["Precio Costo"].get() or 0),
            float(entradas["Precio Menudeo"].get() or 0),
            float(entradas["Precio Mayoreo"].get() or 0),
        ))
        conn.commit()
        conn.close()
        ventana.destroy()
        callback()

    ctk.CTkButton(ventana, text="Guardar", fg_color="#E8751A",
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
        mostrar_tabla(content)

    btn_agregar = ctk.CTkButton(content, text="+ Agregar Producto",
                                fg_color="#E8751A", hover_color="#c45e0e",
                                text_color="#FFFFFF",
                                command=lambda: agregar_producto(recargar))
    btn_agregar.pack(anchor="w", pady=(0,15))

    mostrar_tabla(content)

def mostrar_tabla(content):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT nombre, marca, sku, cantidad, precio_menudeo FROM productos")
    productos = cursor.fetchall()
    conn.close()

    tabla = ctk.CTkFrame(content, fg_color="#1a1a1a", corner_radius=10)
    tabla.pack(fill="both", expand=True)

    if not productos:
        ctk.CTkLabel(tabla, text="Sin productos registrados",
                     text_color="#555555").pack(pady=40)
    else:
        for p in productos:
            fila = ctk.CTkFrame(tabla, fg_color="transparent")
            fila.pack(fill="x", padx=10, pady=4)
            ctk.CTkLabel(fila, text=p[0], text_color="#FFFFFF", width=200,
                         anchor="w").pack(side="left")
            ctk.CTkLabel(fila, text=p[1] or "", text_color="#888888",
                         width=120, anchor="w").pack(side="left")
            ctk.CTkLabel(fila, text=p[2] or "", text_color="#888888",
                         width=100, anchor="w").pack(side="left")
            ctk.CTkLabel(fila, text=str(p[3]), text_color="#E8751A",
                         width=60, anchor="w").pack(side="left")
            ctk.CTkLabel(fila, text=f"${p[4]:.2f}", text_color="#AAAAAA",
                         width=80, anchor="w").pack(side="left")