import customtkinter as ctk
from database.db import conectar

def mostrar_clientes(frame):
    content = ctk.CTkFrame(frame, fg_color="#0f0f0f")
    content.pack(fill="both", expand=True, padx=20, pady=20)

    def recargar():
        for widget in content.winfo_children():
            widget.destroy()
        construir(content)

    def construir(c):
        ctk.CTkLabel(c, text="Clientes",
                     font=ctk.CTkFont(size=18, weight="bold"),
                     text_color="#FFFFFF").pack(anchor="w", pady=(0,10))

        ctk.CTkButton(c, text="+ Nuevo Cliente",
                      fg_color="#E8751A", hover_color="#c45e0e",
                      text_color="#FFFFFF",
                      command=lambda: nuevo_cliente(recargar)).pack(anchor="w", pady=(0,15))

        mostrar_tabla(c, recargar)

    construir(content)

def mostrar_tabla(content, recargar):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT id, nombre, telefono, email FROM clientes ORDER BY nombre")
    clientes = cursor.fetchall()
    conn.close()

    tabla = ctk.CTkScrollableFrame(content, fg_color="#1a1a1a", corner_radius=10)
    tabla.pack(fill="both", expand=True)

    if not clientes:
        ctk.CTkLabel(tabla, text="Sin clientes registrados",
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

            ctk.CTkButton(fila, text="Editar", width=60, height=26,
                          fg_color="#333333", hover_color="#444444",
                          command=lambda cid=c[0]: editar_cliente(cid, recargar)
                          ).pack(side="right", padx=4, pady=4)

            ctk.CTkButton(fila, text="Borrar", width=60, height=26,
                          fg_color="#7a1a1a", hover_color="#a02020",
                          command=lambda cid=c[0]: borrar_cliente(cid, recargar)
                          ).pack(side="right", padx=4, pady=4)

def nuevo_cliente(callback):
    ventana = ctk.CTkToplevel()
    ventana.title("Nuevo Cliente")
    ventana.geometry("420x500")
    ventana.grab_set()

    ctk.CTkLabel(ventana, text="Nuevo Cliente",
                 font=ctk.CTkFont(size=16, weight="bold")).pack(pady=20)

    campos = ["Nombre", "Teléfono", "Email", "Dirección", "Notas"]
    entradas = {}

    for campo in campos:
        ctk.CTkLabel(ventana, text=campo, text_color="#AAAAAA").pack(anchor="w", padx=30)
        entrada = ctk.CTkEntry(ventana, width=360)
        entrada.pack(padx=30, pady=(2,10))
        entradas[campo] = entrada

    def guardar(event=None):
        if not entradas["Nombre"].get().strip():
            error = ctk.CTkToplevel()
            error.title("Campo requerido")
            error.geometry("300x150")
            error.grab_set()
            ctk.CTkLabel(error, text="Falta llenar: Nombre",
                         text_color="#E8751A",
                         font=ctk.CTkFont(size=14)).pack(pady=30)
            ctk.CTkButton(error, text="OK", fg_color="#E8751A",
                          command=error.destroy).pack()
            return

        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO clientes (nombre, telefono, email, direccion, notas)
            VALUES (?, ?, ?, ?, ?)
        """, (
            entradas["Nombre"].get(),
            entradas["Teléfono"].get(),
            entradas["Email"].get(),
            entradas["Dirección"].get(),
            entradas["Notas"].get(),
        ))
        conn.commit()
        conn.close()
        ventana.destroy()
        callback()

    ventana.bind("<Return>", guardar)
    ctk.CTkButton(ventana, text="Guardar", fg_color="#E8751A",
                  hover_color="#c45e0e", command=guardar).pack(pady=15)

def editar_cliente(cliente_id, callback):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM clientes WHERE id=?", (cliente_id,))
    c = cursor.fetchone()
    conn.close()

    ventana = ctk.CTkToplevel()
    ventana.title("Editar Cliente")
    ventana.geometry("420x500")
    ventana.grab_set()

    ctk.CTkLabel(ventana, text="Editar Cliente",
                 font=ctk.CTkFont(size=16, weight="bold")).pack(pady=20)

    campos = ["Nombre", "Teléfono", "Email", "Dirección", "Notas"]
    valores = [c[1], c[2], c[3], c[4], c[5]]
    entradas = {}

    for campo, valor in zip(campos, valores):
        ctk.CTkLabel(ventana, text=campo, text_color="#AAAAAA").pack(anchor="w", padx=30)
        entrada = ctk.CTkEntry(ventana, width=360)
        entrada.insert(0, str(valor) if valor else "")
        entrada.pack(padx=30, pady=(2,10))
        entradas[campo] = entrada

    def guardar(event=None):
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE clientes SET nombre=?, telefono=?, email=?, direccion=?, notas=?
            WHERE id=?
        """, (
            entradas["Nombre"].get(),
            entradas["Teléfono"].get(),
            entradas["Email"].get(),
            entradas["Dirección"].get(),
            entradas["Notas"].get(),
            cliente_id,
        ))
        conn.commit()
        conn.close()
        ventana.destroy()
        callback()

    ventana.bind("<Return>", guardar)
    ctk.CTkButton(ventana, text="Guardar Cambios", fg_color="#E8751A",
                  hover_color="#c45e0e", command=guardar).pack(pady=15)

def borrar_cliente(cliente_id, callback):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM clientes WHERE id=?", (cliente_id,))
    conn.commit()
    conn.close()
    callback()