import customtkinter as ctk
from database.db import conectar
from datetime import datetime, timedelta
import os
import json
import sqlite3

try:
    from PIL import Image
except Exception:
    Image = None


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def get_idioma():
    try:
        config_path = os.path.join(BASE_DIR, "config", "settings.json")
        with open(config_path, "r", encoding="utf-8") as f:
            return json.load(f).get("idioma", "Español")
    except Exception:
        return "Español"


def mostrar_alerta(titulo, mensaje, parent=None):
    alerta = ctk.CTkToplevel(parent) if parent else ctk.CTkToplevel()
    alerta.title(titulo)
    alerta.geometry("390x170")
    alerta.lift()
    alerta.attributes("-topmost", True)
    alerta.grab_set()
    alerta.resizable(False, False)

    ctk.CTkLabel(
        alerta,
        text=mensaje,
        text_color="#E8751A",
        font=ctk.CTkFont(size=13, weight="bold"),
        wraplength=350
    ).pack(pady=25)

    ctk.CTkButton(
        alerta,
        text="OK",
        fg_color="#E8751A",
        hover_color="#c45e0e",
        command=alerta.destroy
    ).pack()


def registrar_movimiento(producto_id, tipo, cantidad, notas=""):
    try:
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO movimientos_inventario
            (producto_id, tipo, cantidad, fecha, notas)
            VALUES (?, ?, ?, ?, ?)
        """, (
            producto_id,
            tipo,
            cantidad,
            datetime.now().strftime("%Y-%m-%d %H:%M"),
            notas
        ))
        conn.commit()
        conn.close()
    except Exception as e:
        print("ERROR registrando movimiento:", e)


def resolver_ruta_imagen(ruta):
    if not ruta:
        return ""
    if os.path.isabs(ruta):
        return ruta
    return os.path.join(BASE_DIR, ruta)


def cargar_ctk_imagen(ruta, size=(70, 70)):
    if not ruta or Image is None:
        return None

    ruta_abs = resolver_ruta_imagen(ruta)

    if not os.path.exists(ruta_abs):
        return None

    try:
        img = Image.open(ruta_abs)
        return ctk.CTkImage(light_image=img, dark_image=img, size=size)
    except Exception:
        return None


def obtener_productos_disponibles():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, nombre, sku, cantidad, precio_menudeo, categoria, imagen
        FROM productos
        WHERE cantidad > 0
        ORDER BY nombre ASC
    """)
    productos = cursor.fetchall()
    conn.close()
    return productos


def cargar_ventas(filtro):
    try:
        conn = conectar()
        cursor = conn.cursor()

        query = "SELECT id, fecha, total, notas FROM ventas"
        params = []

        if filtro == "hoy":
            query += " WHERE fecha LIKE ?"
            params.append(f"{datetime.now().strftime('%Y-%m-%d')}%")
        elif filtro == "semana":
            desde = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
            query += " WHERE fecha >= ?"
            params.append(desde)
        elif filtro == "mes":
            query += " WHERE fecha LIKE ?"
            params.append(f"{datetime.now().strftime('%Y-%m')}%")

        query += " ORDER BY id DESC"

        cursor.execute(query, params)
        ventas = cursor.fetchall()
        conn.close()
        return ventas

    except Exception as e:
        print("ERROR cargando ventas:", e)
        return []


def mostrar_ventas(frame):
    from config.translations import t
    idioma = get_idioma()

    content = ctk.CTkFrame(frame, fg_color="#0f0f0f")
    content.pack(fill="both", expand=True, padx=20, pady=20)

    def recargar(filtro="hoy"):
        for widget in content.winfo_children():
            widget.destroy()
        construir(content, filtro)

    def construir(c, filtro="hoy"):
        idioma = get_idioma()

        ctk.CTkLabel(
            c,
            text=t("ventas", idioma),
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#FFFFFF"
        ).pack(anchor="w", pady=(0, 10))

        btn_frame = ctk.CTkFrame(c, fg_color="transparent")
        btn_frame.pack(fill="x", pady=(0, 10))

        filtros = [
            ("hoy", t("hoy", idioma), 80),
            ("semana", t("esta_semana", idioma), 110),
            ("mes", t("este_mes", idioma), 90),
            ("todos", t("ver_todos", idioma), 90),
        ]

        for valor, texto, ancho in filtros:
            ctk.CTkButton(
                btn_frame,
                text=texto,
                width=ancho,
                fg_color="#E8751A" if filtro == valor else "#333333",
                hover_color="#c45e0e" if filtro == valor else "#444444",
                command=lambda f=valor: recargar(f)
            ).pack(side="left", padx=2)

        ctk.CTkButton(
            btn_frame,
            text=f"+ {t('registrar_venta', idioma)}",
            fg_color="#E8751A",
            hover_color="#c45e0e",
            command=lambda: nueva_venta(frame, lambda: recargar(filtro))
        ).pack(side="left", padx=(20, 0))

        ctk.CTkButton(
            btn_frame,
            text=t("exportar_excel", idioma),
            fg_color="#1a3a1a",
            hover_color="#2a5a2a",
            command=lambda: exportar_ventas(filtro, c)
        ).pack(side="right", padx=2)

        tabla = ctk.CTkScrollableFrame(c, fg_color="#1a1a1a", corner_radius=10)
        tabla.pack(fill="both", expand=True)

        ventas = cargar_ventas(filtro)

        if not ventas:
            ctk.CTkLabel(
                tabla,
                text=t("sin_ventas", idioma),
                text_color="#555555"
            ).pack(pady=40)
            return

        encabezado = ctk.CTkFrame(tabla, fg_color="#111111", corner_radius=6)
        encabezado.pack(fill="x", padx=8, pady=(8, 4))

        columnas = [
            ("ID", 70),
            ("Fecha", 150),
            (t("total", idioma), 110),
            (t("notas", idioma), 520),
        ]

        for texto, ancho in columnas:
            ctk.CTkLabel(
                encabezado,
                text=texto,
                text_color="#777777",
                width=ancho,
                anchor="w",
                font=ctk.CTkFont(size=10, weight="bold")
            ).pack(side="left", padx=6, pady=6)

        for v in ventas:
            fila = ctk.CTkFrame(tabla, fg_color="#222222", corner_radius=6)
            fila.pack(fill="x", padx=8, pady=3)

            ctk.CTkLabel(
                fila,
                text=f"#{v[0]}",
                text_color="#E8751A",
                font=ctk.CTkFont(weight="bold"),
                width=70,
                anchor="w"
            ).pack(side="left", padx=6, pady=7)

            ctk.CTkLabel(
                fila,
                text=v[1],
                text_color="#FFFFFF",
                width=150,
                anchor="w"
            ).pack(side="left", padx=6)

            ctk.CTkLabel(
                fila,
                text=f"${(v[2] or 0):.2f}",
                text_color="#FFFFFF",
                font=ctk.CTkFont(weight="bold"),
                width=110,
                anchor="w"
            ).pack(side="left", padx=6)

            ctk.CTkLabel(
                fila,
                text=v[3] or "",
                text_color="#888888",
                anchor="w",
                width=520
            ).pack(side="left", padx=6)

    construir(content)


def nueva_venta(parent_frame, callback):
    root = parent_frame.winfo_toplevel()
    ventana = ctk.CTkToplevel(root)
    ventana.title("Nueva Venta")
    ventana.geometry("980x650")
    ventana.lift()
    ventana.attributes("-topmost", True)
    ventana.grab_set()
    ventana.resizable(False, False)

    productos_db = obtener_productos_disponibles()
    productos = []

    for p_id, nombre, sku, stock, precio, categoria, imagen in productos_db:
        productos.append({
            "id": p_id,
            "nombre": nombre or "",
            "sku": sku or "",
            "stock": stock or 0,
            "precio": precio or 0,
            "categoria": categoria or "General",
            "imagen": imagen or ""
        })

    carrito = {}

    root_frame = ctk.CTkFrame(ventana, fg_color="#0f0f0f")
    root_frame.pack(fill="both", expand=True)

    header = ctk.CTkFrame(root_frame, fg_color="#151515", height=52)
    header.pack(fill="x")
    header.pack_propagate(False)

    ctk.CTkLabel(
        header,
        text="Nueva Venta",
        text_color="#FFFFFF",
        font=ctk.CTkFont(size=18, weight="bold")
    ).pack(side="left", padx=18)

    main = ctk.CTkFrame(root_frame, fg_color="#0f0f0f")
    main.pack(fill="both", expand=True, padx=16, pady=14)

    left = ctk.CTkFrame(main, fg_color="#0f0f0f")
    left.pack(side="left", fill="both", expand=True, padx=(0, 12))

    right = ctk.CTkFrame(main, fg_color="#1a1a1a", corner_radius=14, width=310)
    right.pack(side="right", fill="y")
    right.pack_propagate(False)

    top_search = ctk.CTkFrame(left, fg_color="transparent")
    top_search.pack(fill="x", pady=(0, 10))

    busqueda = ctk.CTkEntry(
        top_search,
        width=360,
        placeholder_text="🔍 Buscar por nombre, SKU o categoría..."
    )
    busqueda.pack(side="left")

    metodo_pago = ctk.StringVar(value="Efectivo")
    metodo_menu = ctk.CTkOptionMenu(
        top_search,
        values=["Efectivo", "Tarjeta", "Transferencia"],
        variable=metodo_pago,
        width=160,
        fg_color="#333333",
        button_color="#444444",
        button_hover_color="#555555"
    )
    metodo_menu.pack(side="right")

    productos_frame = ctk.CTkScrollableFrame(left, fg_color="#1a1a1a", corner_radius=14)
    productos_frame.pack(fill="both", expand=True)

    ctk.CTkLabel(
        right,
        text="Carrito",
        text_color="#FFFFFF",
        font=ctk.CTkFont(size=17, weight="bold")
    ).pack(anchor="w", padx=16, pady=(16, 4))

    carrito_frame = ctk.CTkScrollableFrame(right, fg_color="#1a1a1a", height=260)
    carrito_frame.pack(fill="both", expand=False, padx=10, pady=(4, 8))

    resumen = ctk.CTkFrame(right, fg_color="#222222", corner_radius=10)
    resumen.pack(fill="x", padx=12, pady=8)

    lbl_subtotal = ctk.CTkLabel(resumen, text="Subtotal: $0.00", text_color="#CCCCCC")
    lbl_subtotal.pack(anchor="w", padx=12, pady=(10, 2))

    lbl_iva = ctk.CTkLabel(resumen, text="IVA 16%: $0.00", text_color="#CCCCCC")
    lbl_iva.pack(anchor="w", padx=12, pady=2)

    lbl_total = ctk.CTkLabel(
        resumen,
        text="Total: $0.00",
        text_color="#E8751A",
        font=ctk.CTkFont(size=22, weight="bold")
    )
    lbl_total.pack(anchor="w", padx=12, pady=(6, 12))

    def calcular_totales():
        subtotal = sum(item["precio"] * item["cantidad"] for item in carrito.values())
        iva = subtotal * 0.16
        total = subtotal + iva
        return subtotal, iva, total

    def actualizar_resumen():
        subtotal, iva, total = calcular_totales()
        lbl_subtotal.configure(text=f"Subtotal: ${subtotal:.2f}")
        lbl_iva.configure(text=f"IVA 16%: ${iva:.2f}")
        lbl_total.configure(text=f"Total: ${total:.2f}")

    def render_carrito():
        for w in carrito_frame.winfo_children():
            w.destroy()

        if not carrito:
            ctk.CTkLabel(
                carrito_frame,
                text="Carrito vacío",
                text_color="#555555"
            ).pack(pady=30)
            actualizar_resumen()
            return

        for producto_id, item in carrito.items():
            fila = ctk.CTkFrame(carrito_frame, fg_color="#222222", corner_radius=8)
            fila.pack(fill="x", padx=4, pady=4)

            ctk.CTkLabel(
                fila,
                text=item["nombre"],
                text_color="#FFFFFF",
                font=ctk.CTkFont(size=11, weight="bold"),
                wraplength=150
            ).pack(anchor="w", padx=8, pady=(6, 0))

            ctk.CTkLabel(
                fila,
                text=f"${item['precio']:.2f} x {item['cantidad']}",
                text_color="#888888",
                font=ctk.CTkFont(size=10)
            ).pack(anchor="w", padx=8)

            controles = ctk.CTkFrame(fila, fg_color="transparent")
            controles.pack(fill="x", padx=8, pady=6)

            ctk.CTkButton(
                controles,
                text="-",
                width=28,
                height=24,
                fg_color="#333333",
                hover_color="#444444",
                command=lambda pid=producto_id: cambiar_cantidad(pid, -1)
            ).pack(side="left")

            ctk.CTkLabel(
                controles,
                text=str(item["cantidad"]),
                text_color="#FFFFFF",
                width=30
            ).pack(side="left", padx=4)

            ctk.CTkButton(
                controles,
                text="+",
                width=28,
                height=24,
                fg_color="#333333",
                hover_color="#444444",
                command=lambda pid=producto_id: cambiar_cantidad(pid, 1)
            ).pack(side="left")

            ctk.CTkButton(
                controles,
                text="Quitar",
                width=65,
                height=24,
                fg_color="#7a1a1a",
                hover_color="#a02020",
                command=lambda pid=producto_id: quitar_producto(pid)
            ).pack(side="right")

        actualizar_resumen()

    def agregar_al_carrito(prod):
        producto_id = prod["id"]
        cantidad_actual = carrito.get(producto_id, {}).get("cantidad", 0)

        if cantidad_actual + 1 > prod["stock"]:
            mostrar_alerta("Stock insuficiente", "No hay más piezas disponibles.", ventana)
            return

        if producto_id not in carrito:
            carrito[producto_id] = {
                "id": producto_id,
                "nombre": prod["nombre"],
                "precio": prod["precio"],
                "stock": prod["stock"],
                "cantidad": 1
            }
        else:
            carrito[producto_id]["cantidad"] += 1

        render_carrito()

    def cambiar_cantidad(producto_id, cambio):
        if producto_id not in carrito:
            return

        nueva = carrito[producto_id]["cantidad"] + cambio

        if nueva <= 0:
            del carrito[producto_id]
        elif nueva > carrito[producto_id]["stock"]:
            mostrar_alerta("Stock insuficiente", "No hay más piezas disponibles.", ventana)
            return
        else:
            carrito[producto_id]["cantidad"] = nueva

        render_carrito()

    def quitar_producto(producto_id):
        if producto_id in carrito:
            del carrito[producto_id]
        render_carrito()

    def render_productos(filtro=""):
        for w in productos_frame.winfo_children():
            w.destroy()

        filtro = filtro.strip().lower()

        filtrados = [
            p for p in productos
            if filtro in p["nombre"].lower()
            or filtro in p["sku"].lower()
            or filtro in p["categoria"].lower()
        ]

        if not filtrados:
            ctk.CTkLabel(
                productos_frame,
                text="Sin productos disponibles",
                text_color="#555555"
            ).pack(pady=40)
            return

        grid = ctk.CTkFrame(productos_frame, fg_color="transparent")
        grid.pack(fill="both", expand=True, padx=10, pady=10)

        columnas = 3

        for index, prod in enumerate(filtrados):
            row = index // columnas
            col = index % columnas

            card = ctk.CTkFrame(
                grid,
                fg_color="#222222",
                corner_radius=12,
                width=190,
                height=250
            )
            card.grid(row=row, column=col, padx=8, pady=8, sticky="nsew")
            card.grid_propagate(False)

            img = cargar_ctk_imagen(prod["imagen"], size=(92, 82))

            img_box = ctk.CTkFrame(card, fg_color="#161616", corner_radius=10, height=90)
            img_box.pack(fill="x", padx=10, pady=(10, 6))
            img_box.pack_propagate(False)

            if img:
                lbl_img = ctk.CTkLabel(img_box, image=img, text="")
                lbl_img.image = img
                lbl_img.pack(expand=True)
            else:
                ctk.CTkLabel(
                    img_box,
                    text="📦",
                    text_color="#555555",
                    font=ctk.CTkFont(size=36)
                ).pack(expand=True)

            ctk.CTkLabel(
                card,
                text=prod["nombre"],
                text_color="#FFFFFF",
                font=ctk.CTkFont(size=12, weight="bold"),
                wraplength=165
            ).pack(anchor="w", padx=10)

            ctk.CTkLabel(
                card,
                text=f"SKU: {prod['sku'] or '-'}",
                text_color="#777777",
                font=ctk.CTkFont(size=10),
                wraplength=165
            ).pack(anchor="w", padx=10, pady=(1, 0))

            ctk.CTkLabel(
                card,
                text=f"Stock: {prod['stock']}",
                text_color="#3B6D11" if prod["stock"] > 0 else "#A32D2D",
                font=ctk.CTkFont(size=10, weight="bold")
            ).pack(anchor="w", padx=10, pady=(3, 0))

            bottom = ctk.CTkFrame(card, fg_color="transparent")
            bottom.pack(fill="x", padx=10, pady=(8, 10), side="bottom")

            ctk.CTkLabel(
                bottom,
                text=f"${prod['precio']:.2f}",
                text_color="#E8751A",
                font=ctk.CTkFont(size=15, weight="bold")
            ).pack(side="left")

            ctk.CTkButton(
                bottom,
                text="+",
                width=38,
                height=30,
                fg_color="#E8751A",
                hover_color="#c45e0e",
                command=lambda p=prod: agregar_al_carrito(p)
            ).pack(side="right")

        for col in range(columnas):
            grid.grid_columnconfigure(col, weight=1)

    def finalizar_venta():
        if not carrito:
            mostrar_alerta("Carrito vacío", "Agrega productos antes de finalizar.", ventana)
            return

        subtotal, iva, total = calcular_totales()
        fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M")
        metodo = metodo_pago.get()

        nota_final = f"Método: {metodo} | Subtotal: ${subtotal:.2f} | IVA: ${iva:.2f}"

        conn = None

        try:
            conn = conectar()
            cursor = conn.cursor()
            cursor.execute("BEGIN")

            for producto_id, item in carrito.items():
                cursor.execute("SELECT cantidad FROM productos WHERE id=?", (producto_id,))
                row = cursor.fetchone()

                if not row:
                    conn.rollback()
                    mostrar_alerta("Error", f"El producto {item['nombre']} ya no existe.", ventana)
                    return

                stock_actual = row[0]

                if item["cantidad"] > stock_actual:
                    conn.rollback()
                    mostrar_alerta(
                        "Stock insuficiente",
                        f"{item['nombre']} solo tiene {stock_actual} piezas.",
                        ventana
                    )
                    return

            cursor.execute("""
                INSERT INTO ventas (fecha, total, notas)
                VALUES (?, ?, ?)
            """, (
                fecha_actual,
                total,
                nota_final
            ))

            venta_id = cursor.lastrowid

            for producto_id, item in carrito.items():
                cursor.execute("SELECT precio_menudeo FROM productos WHERE id=?", (producto_id,))
                precio_actual = cursor.fetchone()[0] or 0

                cursor.execute("""
                    INSERT INTO venta_detalle
                    (venta_id, producto_id, cantidad, precio)
                    VALUES (?, ?, ?, ?)
                """, (
                    venta_id,
                    producto_id,
                    item["cantidad"],
                    precio_actual
                ))

                cursor.execute("""
                    UPDATE productos
                    SET cantidad = cantidad - ?
                    WHERE id = ? AND cantidad >= ?
                """, (
                    item["cantidad"],
                    producto_id,
                    item["cantidad"]
                ))

                if cursor.rowcount == 0:
                    conn.rollback()
                    mostrar_alerta("Error", f"No se pudo descontar {item['nombre']}.", ventana)
                    return

            conn.commit()
            conn.close()

            for producto_id, item in carrito.items():
                registrar_movimiento(
                    producto_id,
                    "VENTA",
                    item["cantidad"],
                    f"Venta #{venta_id}"
                )

            mostrar_alerta("Venta registrada", f"Venta #{venta_id} registrada correctamente.", ventana)
            ventana.destroy()
            callback()

        except sqlite3.Error as e:
            if conn:
                conn.rollback()
                conn.close()
            mostrar_alerta("Error BD", str(e), ventana)

        except Exception as e:
            if conn:
                try:
                    conn.rollback()
                    conn.close()
                except Exception:
                    pass
            mostrar_alerta("Error", str(e), ventana)

    btn_finalizar = ctk.CTkButton(
        right,
        text="COBRAR",
        fg_color="#E8751A",
        hover_color="#c45e0e",
        height=55,
        font=ctk.CTkFont(size=18, weight="bold"),
        command=finalizar_venta
    )
    btn_finalizar.pack(fill="x", padx=12, pady=(15, 15))

    busqueda.bind("<KeyRelease>", lambda e: render_productos(busqueda.get()))

    render_productos()
    render_carrito()


def exportar_ventas(filtro, parent=None):
    try:
        import openpyxl

        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Ventas"
        ws.append(["ID", "Fecha", "Total", "Notas"])

        ventas = cargar_ventas(filtro)

        for v in ventas:
            ws.append([v[0], v[1], v[2], v[3] or ""])

        nombre = f"reporte_ventas_{filtro}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        ruta = os.path.join(BASE_DIR, "exports", nombre)

        os.makedirs(os.path.dirname(ruta), exist_ok=True)
        wb.save(ruta)

        mostrar_alerta("OK", f"Excel guardado en:\nexports/{nombre}", parent)

    except PermissionError:
        mostrar_alerta("Error", "No se pudo guardar el Excel.\nCierra el archivo si está abierto.", parent)

    except Exception as e:
        mostrar_alerta("Error", f"No se pudo exportar:\n{e}", parent)