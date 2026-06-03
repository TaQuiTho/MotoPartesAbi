import customtkinter as ctk
from database.db import conectar
from datetime import datetime

def mostrar_ventas(frame):
    content = ctk.CTkFrame(frame, fg_color="#0f0f0f")
    content.pack(fill="both", expand=True, padx=20, pady=20)

    def recargar():
        for widget in content.winfo_children():
            widget.destroy()
        construir(content)

    def construir(c):
        ctk.CTkLabel(c, text="Ventas",
                     font=ctk.CTkFont(size=18, weight="bold"),
                     text_color="#FFFFFF").pack(anchor="w", pady=(0,10))

        ctk.CTkButton(c, text="+ Nueva Venta",
                      fg_color="#E8751A", hover_color="#c45e0e",
                      text_color="#FFFFFF",
                      command=lambda: nueva_venta(recargar)).pack(anchor="w", pady=(0,15))

        mostrar_historial(c)

    construir(content)

def mostrar_historial(content):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT id, fecha, total FROM ventas ORDER BY id DESC")
    ventas = cursor.fetchall()
    conn.close()

    tabla = ctk.CTkScrollableFrame(content, fg_color="#1a1a1a", corner_radius=10)
    tabla.pack(fill="both", expand=True)

    if not ventas:
        ctk.CTkLabel(tabla, text="Sin ventas registradas",
                     text_color="#555555").pack(pady=40)
    else:
        for v in ventas:
            fila = ctk.CTkFrame(tabla, fg_color="#222222", corner_radius=6)
            fila.pack(fill="x", padx=8, pady=3)
            ctk.CTkLabel(fila, text=f"Venta #{v[0]}", text_color="#FFFFFF",
                         width=100, anchor="w").pack(side="left", padx=6)
            ctk.CTkLabel(fila, text=v[1], text_color="#888888",
                         width=180, anchor="w").pack(side="left")
            ctk.CTkLabel(fila, text=f"${v[2]:.2f}", text_color="#E8751A",
                         width=100, anchor="w").pack(side="left")

def nueva_venta(callback):
    ventana = ctk.CTkToplevel()
    ventana.title("Nueva Venta")
    ventana.geometry("500x550")
    ventana.grab_set()

    ctk.CTkLabel(ventana, text="Nueva Venta",
                 font=ctk.CTkFont(size=16, weight="bold")).pack(pady=15)

    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT id, nombre, precio_menudeo, cantidad FROM productos")
    productos = cursor.fetchall()
    conn.close()

    if not productos:
        ctk.CTkLabel(ventana, text="No hay productos en inventario",
                     text_color="#888888").pack(pady=20)
        return

    nombres = [f"{p[1]} - ${p[2]:.2f}" for p in productos]
    seleccion = ctk.StringVar(value=nombres[0])

    ctk.CTkLabel(ventana, text="Producto", text_color="#AAAAAA").pack(anchor="w", padx=30)
    ctk.CTkOptionMenu(ventana, values=nombres, variable=seleccion,
                      width=440).pack(padx=30, pady=(2,10))

    ctk.CTkLabel(ventana, text="Cantidad", text_color="#AAAAAA").pack(anchor="w", padx=30)
    entrada_cantidad = ctk.CTkEntry(ventana, width=440)
    entrada_cantidad.pack(padx=30, pady=(2,10))

    ctk.CTkLabel(ventana, text="Notas", text_color="#AAAAAA").pack(anchor="w", padx=30)
    entrada_notas = ctk.CTkEntry(ventana, width=440)
    entrada_notas.pack(padx=30, pady=(2,10))

    total_label = ctk.CTkLabel(ventana, text="Total: $0.00",
                               font=ctk.CTkFont(size=16, weight="bold"),
                               text_color="#E8751A")
    total_label.pack(pady=10)

    def calcular_total(*args):
        idx = nombres.index(seleccion.get())
        cantidad = int(entrada_cantidad.get() or 0)
        total = productos[idx][2] * cantidad
        total_label.configure(text=f"Total: ${total:.2f}")

    entrada_cantidad.bind("<KeyRelease>", calcular_total)

    def guardar(event=None):
        idx = nombres.index(seleccion.get())
        producto = productos[idx]
        cantidad = int(entrada_cantidad.get() or 0)
        total = producto[2] * cantidad
        fecha = datetime.now().strftime("%Y-%m-%d %H:%M")

        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO ventas (fecha, total, notas) VALUES (?, ?, ?)",
                       (fecha, total, entrada_notas.get()))
        venta_id = cursor.lastrowid
        cursor.execute("""INSERT INTO venta_detalle (venta_id, producto_id, cantidad, precio)
                          VALUES (?, ?, ?, ?)""",
                       (venta_id, producto[0], cantidad, producto[2]))
        cursor.execute("UPDATE productos SET cantidad = cantidad - ? WHERE id = ?",
                       (cantidad, producto[0]))
        conn.commit()
        conn.close()
        ventana.destroy()
        callback()

    ventana.bind("<Return>", guardar)
    ctk.CTkButton(ventana, text="Registrar Venta", fg_color="#E8751A",
                  hover_color="#c45e0e", command=guardar).pack(pady=15)