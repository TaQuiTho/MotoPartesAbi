import customtkinter as ctk
from database.db import conectar
from datetime import datetime, timedelta
import openpyxl
import os
import matplotlib.pyplot as plt
import matplotlib.backends.backend_tkagg as tkagg
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

def mostrar_reportes(frame):
    content = ctk.CTkFrame(frame, fg_color="#0f0f0f")
    content.pack(fill="both", expand=True, padx=20, pady=20)

    ctk.CTkLabel(content, text="Reportes",
                 font=ctk.CTkFont(size=18, weight="bold"),
                 text_color="#FFFFFF").pack(anchor="w", pady=(0,15))

    botones_frame = ctk.CTkFrame(content, fg_color="transparent")
    botones_frame.pack(fill="x", pady=(0,15))

    reportes = [
        ("📊 Ventas", lambda: mostrar_reporte_ventas(content)),
        ("📦 Stock Bajo", lambda: mostrar_stock_bajo(content)),
        ("👥 Clientes Frecuentes", lambda: mostrar_clientes_frecuentes(content)),
        ("⬇ Exportar Todo", lambda: exportar_todo()),
    ]

    for texto, comando in reportes:
        ctk.CTkButton(botones_frame, text=texto, fg_color="#1a1a1a",
                      hover_color="#2a2a2a", text_color="#FFFFFF",
                      border_color="#E8751A", border_width=1,
                      command=comando).pack(side="left", padx=6)

    mostrar_reporte_ventas(content)

def limpiar_contenido(content):
    for widget in content.winfo_children():
        if hasattr(widget, '_es_reporte'):
            widget.destroy()

def mostrar_reporte_ventas(content):
    limpiar_contenido(content)

    frame = ctk.CTkFrame(content, fg_color="#1a1a1a", corner_radius=10)
    frame._es_reporte = True
    frame.pack(fill="both", expand=True, pady=(10,0))

    hoy = datetime.now().strftime("%Y-%m-%d")
    semana = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
    mes = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*), SUM(total) FROM ventas WHERE fecha LIKE ?", (f"{hoy}%",))
    v_hoy = cursor.fetchone()

    cursor.execute("SELECT COUNT(*), SUM(total) FROM ventas WHERE fecha >= ?", (semana,))
    v_semana = cursor.fetchone()

    cursor.execute("SELECT COUNT(*), SUM(total) FROM ventas WHERE fecha >= ?", (mes,))
    v_mes = cursor.fetchone()

    cursor.execute("""
        SELECT DATE(fecha) as dia, SUM(total)
        FROM ventas
        WHERE fecha >= ?
        GROUP BY dia
        ORDER BY dia ASC
    """, (semana,))
    datos_grafica = cursor.fetchall()

    conn.close()

    ctk.CTkLabel(frame, text="Resumen de Ventas",
                 font=ctk.CTkFont(size=14, weight="bold"),
                 text_color="#E8751A").pack(anchor="w", padx=15, pady=(12,8))

    stats = [
        ("Hoy", v_hoy[0] or 0, v_hoy[1] or 0),
        ("Esta semana", v_semana[0] or 0, v_semana[1] or 0),
        ("Este mes", v_mes[0] or 0, v_mes[1] or 0),
    ]

    stats_frame = ctk.CTkFrame(frame, fg_color="transparent")
    stats_frame.pack(fill="x", padx=15, pady=(0,12))

    for periodo, cantidad, total in stats:
        card = ctk.CTkFrame(stats_frame, fg_color="#222222", corner_radius=8)
        card.pack(side="left", expand=True, fill="x", padx=6)
        ctk.CTkLabel(card, text=periodo, text_color="#888888",
                     font=ctk.CTkFont(size=11)).pack(pady=(10,2))
        ctk.CTkLabel(card, text=f"${total:.2f}", text_color="#E8751A",
                     font=ctk.CTkFont(size=18, weight="bold")).pack()
        ctk.CTkLabel(card, text=f"{cantidad} ventas", text_color="#555555",
                     font=ctk.CTkFont(size=11)).pack(pady=(2,10))

    if datos_grafica:
        dias = [d[0] for d in datos_grafica]
        totales = [d[1] for d in datos_grafica]

        fig, ax = plt.subplots(figsize=(8, 2.5))
        fig.patch.set_facecolor("#1a1a1a")
        ax.set_facecolor("#1a1a1a")

        ax.bar(dias, totales, color="#E8751A", alpha=0.85)
        ax.set_ylabel("Total $", color="#888888", fontsize=9)
        ax.tick_params(colors="#888888", labelsize=8)
        ax.spines['bottom'].set_color("#333333")
        ax.spines['left'].set_color("#333333")
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)

        for label in ax.get_xticklabels():
            label.set_rotation(30)

        fig.tight_layout()

        canvas = FigureCanvasTkAgg(fig, master=frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="x", padx=15, pady=(0,12))

def mostrar_stock_bajo(content):
    limpiar_contenido(content)

    frame = ctk.CTkFrame(content, fg_color="#1a1a1a", corner_radius=10)
    frame._es_reporte = True
    frame.pack(fill="both", expand=True, pady=(10,0))

    ctk.CTkLabel(frame, text="Productos con Stock Bajo",
                 font=ctk.CTkFont(size=14, weight="bold"),
                 text_color="#E8751A").pack(anchor="w", padx=15, pady=(12,8))

    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT nombre, marca, cantidad, stock_minimo
        FROM productos
        WHERE cantidad <= stock_minimo
        ORDER BY cantidad ASC
    """)
    productos = cursor.fetchall()
    conn.close()

    if productos:
        nombres = [p[0][:15] for p in productos]
        cantidades = [p[2] for p in productos]
        minimos = [p[3] for p in productos]

        fig, ax = plt.subplots(figsize=(8, 2.5))
        fig.patch.set_facecolor("#1a1a1a")
        ax.set_facecolor("#1a1a1a")

        x = range(len(nombres))
        ax.bar(x, cantidades, color="#A32D2D", alpha=0.85, label="Stock actual")
        ax.bar(x, minimos, color="#555555", alpha=0.4, label="Mínimo")
        ax.set_xticks(list(x))
        ax.set_xticklabels(nombres, rotation=30, fontsize=8)
        ax.tick_params(colors="#888888", labelsize=8)
        ax.spines['bottom'].set_color("#333333")
        ax.spines['left'].set_color("#333333")
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.legend(facecolor="#222222", labelcolor="#888888", fontsize=8)

        fig.tight_layout()

        canvas = FigureCanvasTkAgg(fig, master=frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="x", padx=15, pady=(0,8))

    tabla = ctk.CTkScrollableFrame(frame, fg_color="transparent")
    tabla.pack(fill="both", expand=True, padx=10, pady=(0,10))

    if not productos:
        ctk.CTkLabel(tabla, text="Sin productos con stock bajo",
                     text_color="#555555").pack(pady=20)
    else:
        for p in productos:
            fila = ctk.CTkFrame(tabla, fg_color="#222222", corner_radius=6)
            fila.pack(fill="x", pady=3)
            ctk.CTkLabel(fila, text=p[0], text_color="#FFFFFF",
                         width=200, anchor="w").pack(side="left", padx=8)
            ctk.CTkLabel(fila, text=p[1] or "", text_color="#888888",
                         width=120, anchor="w").pack(side="left")
            ctk.CTkLabel(fila, text=f"Stock: {p[2]}", text_color="#A32D2D",
                         width=80, anchor="w").pack(side="left")
            ctk.CTkLabel(fila, text=f"Mín: {p[3]}", text_color="#555555",
                         width=70, anchor="w").pack(side="left")

def mostrar_clientes_frecuentes(content):
    limpiar_contenido(content)

    frame = ctk.CTkFrame(content, fg_color="#1a1a1a", corner_radius=10)
    frame._es_reporte = True
    frame.pack(fill="both", expand=True, pady=(10,0))

    ctk.CTkLabel(frame, text="Clientes Frecuentes",
                 font=ctk.CTkFont(size=14, weight="bold"),
                 text_color="#E8751A").pack(anchor="w", padx=15, pady=(12,8))

    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT a.cliente, COUNT(*) as total
        FROM apartados a
        GROUP BY a.cliente
        ORDER BY total DESC
        LIMIT 10
    """)
    clientes = cursor.fetchall()
    conn.close()

    if clientes:
        nombres = [c[0][:12] for c in clientes]
        totales = [c[1] for c in clientes]

        fig, ax = plt.subplots(figsize=(8, 2.5))
        fig.patch.set_facecolor("#1a1a1a")
        ax.set_facecolor("#1a1a1a")

        ax.barh(nombres, totales, color="#E8751A", alpha=0.85)
        ax.tick_params(colors="#888888", labelsize=8)
        ax.spines['bottom'].set_color("#333333")
        ax.spines['left'].set_color("#333333")
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)

        fig.tight_layout()

        canvas = FigureCanvasTkAgg(fig, master=frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="x", padx=15, pady=(0,8))

    tabla = ctk.CTkScrollableFrame(frame, fg_color="transparent")
    tabla.pack(fill="both", expand=True, padx=10, pady=(0,10))

    if not clientes:
        ctk.CTkLabel(tabla, text="Sin datos de clientes",
                     text_color="#555555").pack(pady=20)
    else:
        for i, c in enumerate(clientes):
            fila = ctk.CTkFrame(tabla, fg_color="#222222", corner_radius=6)
            fila.pack(fill="x", pady=3)
            ctk.CTkLabel(fila, text=f"#{i+1}", text_color="#E8751A",
                         width=40, anchor="w").pack(side="left", padx=8)
            ctk.CTkLabel(fila, text=c[0], text_color="#FFFFFF",
                         width=200, anchor="w").pack(side="left")
            ctk.CTkLabel(fila, text=f"{c[1]} apartados", text_color="#888888",
                         width=100, anchor="w").pack(side="left")

def exportar_todo():
    conn = conectar()
    cursor = conn.cursor()

    wb = openpyxl.Workbook()

    ws_ventas = wb.active
    ws_ventas.title = "Ventas"
    ws_ventas.append(["#", "Fecha", "Total", "Notas"])
    cursor.execute("SELECT id, fecha, total, notas FROM ventas ORDER BY id DESC")
    for v in cursor.fetchall():
        ws_ventas.append([v[0], v[1], v[2], v[3] or ""])

    ws_inv = wb.create_sheet("Inventario")
    ws_inv.append(["Nombre", "Marca", "SKU", "Cantidad", "Precio Menudeo", "Precio Mayoreo"])
    cursor.execute("SELECT nombre, marca, sku, cantidad, precio_menudeo, precio_mayoreo FROM productos")
    for p in cursor.fetchall():
        ws_inv.append(list(p))

    ws_clientes = wb.create_sheet("Clientes")
    ws_clientes.append(["Nombre", "Teléfono", "Email", "Dirección"])
    cursor.execute("SELECT nombre, telefono, email, direccion FROM clientes")
    for c in cursor.fetchall():
        ws_clientes.append(list(c))

    conn.close()

    hoy = datetime.now().strftime("%Y-%m-%d")
    nombre = f"reporte_completo_{hoy}.xlsx"
    ruta = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "exports", nombre)
    os.makedirs(os.path.dirname(ruta), exist_ok=True)
    wb.save(ruta)

    exito = ctk.CTkToplevel()
    exito.title("Exportado")
    exito.geometry("350x150")
    exito.grab_set()
    ctk.CTkLabel(exito, text=f"Reporte guardado en:\nexports/{nombre}",
                 text_color="#FFFFFF", wraplength=300).pack(pady=30)
    ctk.CTkButton(exito, text="OK", fg_color="#E8751A",
                  command=exito.destroy).pack()