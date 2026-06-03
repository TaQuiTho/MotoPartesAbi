import customtkinter as ctk
from database.db import conectar
from datetime import datetime, timedelta
import openpyxl
import os

def mostrar_ventas(frame):
    content = ctk.CTkFrame(frame, fg_color="#0f0f0f")
    content.pack(fill="both", expand=True, padx=20, pady=20)

    def recargar(filtro="hoy"):
        for widget in content.winfo_children():
            widget.destroy()
        construir(content, filtro)

    def construir(c, filtro="hoy"):
        ctk.CTkLabel(c, text="Ventas",
                     font=ctk.CTkFont(size=18, weight="bold"),
                     text_color="#FFFFFF").pack(anchor="w", pady=(0,10))

        btn_frame = ctk.CTkFrame(c, fg_color="transparent")
        btn_frame.pack(anchor="w", pady=(0,10))

        for texto, key in [("Hoy", "hoy"), ("Semana", "semana"), ("Mes", "mes"), ("Todas", "todas")]:
            color = "#E8751A" if filtro == key else "#333333"
            ctk.CTkButton(btn_frame, text=texto, width=70, height=28,
                          fg_color=color, hover_color="#c45e0e",
                          command=lambda k=key: recargar(k)).pack(side="left", padx=4)

        ctk.CTkButton(c, text="+ Nueva Venta",
                      fg_color="#E8751A", hover_color="#c45e0e",
                      text_color="#FFFFFF",
                      command=lambda: nueva_venta(lambda: recargar(filtro))).pack(anchor="w", pady=(0,10))

        ctk.CTkButton(c, text="⬇ Exportar Excel",
                      fg_color="#1a3a1a", hover_color="#2a5a2a",
                      text_color="#FFFFFF",
                      command=lambda: exportar_excel(filtro)).pack(anchor="w", pady=(0,15))

        mostrar_historial(c, filtro)

    construir(content)

def mostrar_historial(content, filtro="hoy"):
    conn = conectar()
    cursor = conn.cursor()

    hoy = datetime.now().strftime("%Y-%m-%d")
    semana = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
    mes = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")

    if filtro == "hoy":
        cursor.execute("SELECT id, fecha, total, notas FROM ventas WHERE fecha LIKE ? ORDER BY id DESC", (f"{hoy}%",))
    elif filtro == "semana":
        cursor.execute("SELECT id, fecha, total, notas FROM ventas WHERE fecha >= ? ORDER BY id DESC", (semana,))
    elif filtro == "mes":
        cursor.execute("SELECT id, fecha, total, notas FROM ventas WHERE fecha >= ? ORDER BY id DESC", (mes,))
    else:
        cursor.execute("SELECT id, fecha, total, notas FROM ventas ORDER BY id DESC")

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
            ctk.CTkLabel(fila, text=v[3] or "", text_color="#555555",
                         width=150, anchor="w").pack(side="left")

def exportar_excel(filtro="todas"):
    conn = conectar()
    cursor = conn.cursor()

    hoy = datetime.now().strftime("%Y-%m-%d")
    semana = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
    mes = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")

    if filtro == "hoy":
        cursor.execute("SELECT id, fecha, total, notas FROM ventas WHERE fecha LIKE ?", (f"{hoy}%",))
    elif filtro == "semana":
        cursor.execute("SELECT id, fecha, total, notas FROM ventas WHERE fecha >= ?", (semana,))
    elif filtro == "mes":
        cursor.execute("SELECT id, fecha, total, notas FROM ventas WHERE fecha >= ?", (mes,))
    else:
        cursor.execute("SELECT id, fecha, total, notas FROM ventas ORDER BY id DESC")

    ventas = cursor.fetchall()
    conn.close()

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Ventas"
    ws.append(["#", "Fecha", "Total", "Notas"])

    for v in ventas:
        ws.append([v[0], v[1], v[2], v[3] or ""])

    nombre = f"ventas_{filtro}_{hoy}.xlsx"
    ruta = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "exports", nombre)
    os.makedirs(os.path.dirname(ruta), exist_ok=True)
    wb.save(ruta)

    exito = ctk.CTkToplevel()
    exito.title("Exportado")
    exito.geometry("350x150")
    exito.grab_set()
    ctk.CTkLabel(exito, text=f"Archivo guardado en:\n{ruta}",
                 text_color="#FFFFFF", wraplength=300).pack(pady=30)
    ctk.CTkButton(exito, text="OK", fg_color="#E8751A",
                  command=exito.destroy).pack()

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