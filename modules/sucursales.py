import customtkinter as ctk
from database.db import conectar

def mostrar_sucursales(frame):
    content = ctk.CTkFrame(frame, fg_color="#0f0f0f")
    content.pack(fill="both", expand=True, padx=20, pady=20)

    def recargar():
        for widget in content.winfo_children():
            widget.destroy()
        construir(content)

    def construir(c):
        ctk.CTkLabel(c, text="Sucursales",
                     font=ctk.CTkFont(size=18, weight="bold"),
                     text_color="#FFFFFF").pack(anchor="w", pady=(0,10))

        ctk.CTkButton(c, text="+ Nueva Sucursal",
                      fg_color="#E8751A", hover_color="#c45e0e",
                      text_color="#FFFFFF",
                      command=lambda: nueva_sucursal(recargar)).pack(anchor="w", pady=(0,15))

        mostrar_tabla(c, recargar)

    construir(content)

def mostrar_tabla(content, recargar):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT id, nombre, direccion, telefono, gerente, activa FROM sucursales ORDER BY nombre")
    sucursales = cursor.fetchall()
    conn.close()

    tabla = ctk.CTkScrollableFrame(content, fg_color="#1a1a1a", corner_radius=10)
    tabla.pack(fill="both", expand=True)

    if not sucursales:
        ctk.CTkLabel(tabla, text="Sin sucursales registradas",
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
            estado = "Activa" if s[5] else "Inactiva"
            ctk.CTkLabel(fila, text=estado, text_color=color,
                         width=70, anchor="w").pack(side="left")

            ctk.CTkButton(fila, text="Editar", width=60, height=26,
                          fg_color="#333333", hover_color="#444444",
                          command=lambda sid=s[0]: editar_sucursal(sid, recargar)
                          ).pack(side="right", padx=4, pady=4)

            ctk.CTkButton(fila, text="Borrar", width=60, height=26,
                          fg_color="#7a1a1a", hover_color="#a02020",
                          command=lambda sid=s[0]: borrar_sucursal(sid, recargar)
                          ).pack(side="right", padx=4, pady=4)

def nueva_sucursal(callback):
    ventana = ctk.CTkToplevel()
    ventana.title("Nueva Sucursal")
    ventana.geometry("420x450")
    ventana.grab_set()

    ctk.CTkLabel(ventana, text="Nueva Sucursal",
                 font=ctk.CTkFont(size=16, weight="bold")).pack(pady=20)

    campos = ["Nombre", "Dirección", "Teléfono", "Gerente"]
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
            INSERT INTO sucursales (nombre, direccion, telefono, gerente)
            VALUES (?, ?, ?, ?)
        """, (
            entradas["Nombre"].get(),
            entradas["Dirección"].get(),
            entradas["Teléfono"].get(),
            entradas["Gerente"].get(),
        ))
        conn.commit()
        conn.close()
        ventana.destroy()
        callback()

    ventana.bind("<Return>", guardar)
    ctk.CTkButton(ventana, text="Guardar", fg_color="#E8751A",
                  hover_color="#c45e0e", command=guardar).pack(pady=15)

def editar_sucursal(sucursal_id, callback):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM sucursales WHERE id=?", (sucursal_id,))
    s = cursor.fetchone()
    conn.close()

    ventana = ctk.CTkToplevel()
    ventana.title("Editar Sucursal")
    ventana.geometry("420x500")
    ventana.grab_set()

    ctk.CTkLabel(ventana, text="Editar Sucursal",
                 font=ctk.CTkFont(size=16, weight="bold")).pack(pady=20)

    campos = ["Nombre", "Dirección", "Teléfono", "Gerente"]
    valores = [s[1], s[2], s[3], s[4]]
    entradas = {}

    for campo, valor in zip(campos, valores):
        ctk.CTkLabel(ventana, text=campo, text_color="#AAAAAA").pack(anchor="w", padx=30)
        entrada = ctk.CTkEntry(ventana, width=360)
        entrada.insert(0, str(valor) if valor else "")
        entrada.pack(padx=30, pady=(2,10))
        entradas[campo] = entrada

    ctk.CTkLabel(ventana, text="Estado", text_color="#AAAAAA").pack(anchor="w", padx=30)
    activa_var = ctk.BooleanVar(value=bool(s[5]))
    ctk.CTkCheckBox(ventana, text="Sucursal activa", variable=activa_var,
                    text_color="#FFFFFF").pack(anchor="w", padx=30, pady=(2,10))

    def guardar(event=None):
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE sucursales SET nombre=?, direccion=?, telefono=?, gerente=?, activa=?
            WHERE id=?
        """, (
            entradas["Nombre"].get(),
            entradas["Dirección"].get(),
            entradas["Teléfono"].get(),
            entradas["Gerente"].get(),
            int(activa_var.get()),
            sucursal_id,
        ))
        conn.commit()
        conn.close()
        ventana.destroy()
        callback()

    ventana.bind("<Return>", guardar)
    ctk.CTkButton(ventana, text="Guardar Cambios", fg_color="#E8751A",
                  hover_color="#c45e0e", command=guardar).pack(pady=15)

def borrar_sucursal(sucursal_id, callback):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM sucursales WHERE id=?", (sucursal_id,))
    conn.commit()
    conn.close()
    callback()