import customtkinter as ctk
from database.db import conectar
from datetime import datetime

def mostrar_apartados(frame):
    content = ctk.CTkFrame(frame, fg_color="#0f0f0f")
    content.pack(fill="both", expand=True, padx=20, pady=20)

    def recargar():
        for widget in content.winfo_children():
            widget.destroy()
        construir(content)

    def construir(c):
        ctk.CTkLabel(c, text="Apartados",
                     font=ctk.CTkFont(size=18, weight="bold"),
                     text_color="#FFFFFF").pack(anchor="w", pady=(0,10))

        ctk.CTkButton(c, text="+ Nuevo Apartado",
                      fg_color="#E8751A", hover_color="#c45e0e",
                      text_color="#FFFFFF",
                      command=lambda: nuevo_apartado(recargar)).pack(anchor="w", pady=(0,15))

        mostrar_tabla(c, recargar)

    construir(content)

def editar_apartado(apartado_id, callback):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM apartados WHERE id=?", (apartado_id,))
    a = cursor.fetchone()
    cursor.execute("SELECT id, nombre FROM productos")
    productos = cursor.fetchall()
    conn.close()

    ventana = ctk.CTkToplevel()
    ventana.title("Editar Apartado")
    ventana.geometry("420x500")
    ventana.grab_set()

    ctk.CTkLabel(ventana, text="Editar Apartado",
                 font=ctk.CTkFont(size=16, weight="bold")).pack(pady=20)

    ctk.CTkLabel(ventana, text="Producto", text_color="#AAAAAA").pack(anchor="w", padx=30)
    nombres = [p[1] for p in productos]
    producto_actual = next((p[1] for p in productos if p[0] == a[2]), nombres[0] if nombres else "")
    seleccion = ctk.StringVar(value=producto_actual)
    ctk.CTkOptionMenu(ventana, values=nombres, variable=seleccion,
                      width=360).pack(padx=30, pady=(2,10))

    campos = ["Cliente", "Cantidad", "Fecha de entrega", "Notas"]
    valores = [a[1], a[3], a[5], a[6]]
    entradas = {}

    for campo, valor in zip(campos, valores):
        ctk.CTkLabel(ventana, text=campo, text_color="#AAAAAA").pack(anchor="w", padx=30)
        entrada = ctk.CTkEntry(ventana, width=360)
        entrada.insert(0, str(valor) if valor else "")
        entrada.pack(padx=30, pady=(2,10))
        entradas[campo] = entrada

    def guardar(event=None):
        producto_id = next((p[0] for p in productos if p[1] == seleccion.get()), None)
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE apartados SET cliente=?, producto_id=?, cantidad=?, fecha_entrega=?, notas=?
            WHERE id=?
        """, (
            entradas["Cliente"].get(),
            producto_id,
            int(entradas["Cantidad"].get() or 1),
            entradas["Fecha de entrega"].get(),
            entradas["Notas"].get(),
            apartado_id,
        ))
        conn.commit()
        conn.close()
        ventana.destroy()
        callback()

    ventana.bind("<Return>", guardar)
    ctk.CTkButton(ventana, text="Guardar Cambios", fg_color="#E8751A",
                  hover_color="#c45e0e", command=guardar).pack(pady=15)

def mostrar_tabla(content, recargar):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT a.id, a.cliente, p.nombre, a.cantidad, a.fecha_entrega, a.estado
        FROM apartados a
        LEFT JOIN productos p ON a.producto_id = p.id
        ORDER BY a.id DESC
    """)
    apartados = cursor.fetchall()
    conn.close()

    tabla = ctk.CTkScrollableFrame(content, fg_color="#1a1a1a", corner_radius=10)
    tabla.pack(fill="both", expand=True)

    if not apartados:
        ctk.CTkLabel(tabla, text="Sin apartados registrados",
                     text_color="#555555").pack(pady=40)
    else:
        for a in apartados:
            fila = ctk.CTkFrame(tabla, fg_color="#222222", corner_radius=6)
            fila.pack(fill="x", padx=8, pady=3)

            ctk.CTkLabel(fila, text=a[1], text_color="#FFFFFF",
                         width=150, anchor="w").pack(side="left", padx=6)
            ctk.CTkLabel(fila, text=a[2] or "", text_color="#888888",
                         width=150, anchor="w").pack(side="left")
            ctk.CTkLabel(fila, text=str(a[3]), text_color="#AAAAAA",
                         width=50, anchor="w").pack(side="left")
            ctk.CTkLabel(fila, text=a[4] or "", text_color="#AAAAAA",
                         width=100, anchor="w").pack(side="left")

            color_estado = "#E8751A" if a[5] == "pendiente" else "#3B6D11"
            ctk.CTkLabel(fila, text=a[5], text_color=color_estado,
                         width=80, anchor="w").pack(side="left")

            ctk.CTkButton(fila, text="Entregar", width=70, height=26,
                          fg_color="#1a3a1a", hover_color="#2a5a2a",
                          command=lambda aid=a[0]: entregar(aid, recargar)
                          ).pack(side="right", padx=4, pady=4)

            ctk.CTkButton(fila, text="Editar", width=60, height=26,
                          fg_color="#333333", hover_color="#444444",
                          command=lambda aid=a[0]: editar_apartado(aid, recargar)
                          ).pack(side="right", padx=4, pady=4)

            ctk.CTkButton(fila, text="Borrar", width=60, height=26,
                          fg_color="#7a1a1a", hover_color="#a02020",
                          command=lambda aid=a[0]: borrar(aid, recargar)
                          ).pack(side="right", padx=4, pady=4)

def nuevo_apartado(callback):
    ventana = ctk.CTkToplevel()
    ventana.title("Nuevo Apartado")
    ventana.geometry("420x500")
    ventana.grab_set()

    ctk.CTkLabel(ventana, text="Nuevo Apartado",
                 font=ctk.CTkFont(size=16, weight="bold")).pack(pady=20)

    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT id, nombre FROM productos")
    productos = cursor.fetchall()
    conn.close()

    campos_labels = ["Cliente", "Cantidad", "Fecha de entrega", "Notas"]
    entradas = {}

    ctk.CTkLabel(ventana, text="Producto", text_color="#AAAAAA").pack(anchor="w", padx=30)
    nombres = [p[1] for p in productos]
    seleccion = ctk.StringVar(value=nombres[0] if nombres else "")
    ctk.CTkOptionMenu(ventana, values=nombres, variable=seleccion,
                      width=360).pack(padx=30, pady=(2,10))

    for campo in campos_labels:
        ctk.CTkLabel(ventana, text=campo, text_color="#AAAAAA").pack(anchor="w", padx=30)
        entrada = ctk.CTkEntry(ventana, width=360)
        entrada.pack(padx=30, pady=(2,10))
        entradas[campo] = entrada

    def guardar(event=None):
        if not entradas["Cliente"].get().strip():
            error = ctk.CTkToplevel()
            error.title("Campo requerido")
            error.geometry("300x150")
            error.grab_set()
            ctk.CTkLabel(error, text="Falta llenar: Cliente",
                         text_color="#E8751A",
                         font=ctk.CTkFont(size=14)).pack(pady=30)
            ctk.CTkButton(error, text="OK", fg_color="#E8751A",
                          command=error.destroy).pack()
            return

        producto_id = next((p[0] for p in productos if p[1] == seleccion.get()), None)
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO apartados (cliente, producto_id, cantidad, fecha, fecha_entrega, notas)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            entradas["Cliente"].get(),
            producto_id,
            int(entradas["Cantidad"].get() or 1),
            datetime.now().strftime("%Y-%m-%d %H:%M"),
            entradas["Fecha de entrega"].get(),
            entradas["Notas"].get(),
        ))
        conn.commit()
        conn.close()
        ventana.destroy()
        callback()

    ventana.bind("<Return>", guardar)
    ctk.CTkButton(ventana, text="Guardar", fg_color="#E8751A",
                  hover_color="#c45e0e", command=guardar).pack(pady=15)

def entregar(apartado_id, callback):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("UPDATE apartados SET estado='entregado' WHERE id=?", (apartado_id,))
    conn.commit()
    conn.close()
    callback()

def borrar(apartado_id, callback):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM apartados WHERE id=?", (apartado_id,))
    conn.commit()
    conn.close()
    callback()