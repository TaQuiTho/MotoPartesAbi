import customtkinter as ctk
from database.db import conectar
from datetime import datetime
import os
import json
import sqlite3


def get_idioma():
    try:
        config_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "..",
            "config",
            "settings.json"
        )
        with open(config_path, "r", encoding="utf-8") as f:
            return json.load(f).get("idioma", "Español")
    except Exception:
        return "Español"


def mostrar_alerta(titulo, mensaje, parent=None):
    alerta = ctk.CTkToplevel(parent) if parent else ctk.CTkToplevel()
    alerta.title(titulo)
    alerta.geometry("380x170")
    alerta.grab_set()
    alerta.resizable(False, False)

    ctk.CTkLabel(
        alerta,
        text=mensaje,
        text_color="#E8751A",
        font=ctk.CTkFont(size=13, weight="bold"),
        wraplength=330
    ).pack(pady=25)

    ctk.CTkButton(
        alerta,
        text="OK",
        fg_color="#E8751A",
        hover_color="#c45e0e",
        command=alerta.destroy
    ).pack()


def confirmar(titulo, mensaje, accion, parent=None):
    ventana = ctk.CTkToplevel(parent) if parent else ctk.CTkToplevel()
    ventana.title(titulo)
    ventana.geometry("390x180")
    ventana.grab_set()
    ventana.resizable(False, False)

    ctk.CTkLabel(
        ventana,
        text=mensaje,
        text_color="#FFFFFF",
        font=ctk.CTkFont(size=13, weight="bold"),
        wraplength=340
    ).pack(pady=25)

    botones = ctk.CTkFrame(ventana, fg_color="transparent")
    botones.pack(pady=8)

    def aceptar():
        ventana.destroy()
        accion()

    ctk.CTkButton(
        botones,
        text="Cancelar",
        fg_color="#333333",
        hover_color="#444444",
        width=100,
        command=ventana.destroy
    ).pack(side="left", padx=8)

    ctk.CTkButton(
        botones,
        text="Aceptar",
        fg_color="#7a1a1a",
        hover_color="#a02020",
        width=100,
        command=aceptar
    ).pack(side="left", padx=8)


def entero_seguro(valor, defecto=1):
    try:
        return int(str(valor).strip())
    except Exception:
        return defecto


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


def mostrar_apartados(frame):
    from config.translations import t
    idioma = get_idioma()

    content = ctk.CTkFrame(frame, fg_color="#0f0f0f")
    content.pack(fill="both", expand=True, padx=20, pady=20)

    def recargar():
        for widget in content.winfo_children():
            widget.destroy()
        construir(content)

    def construir(c):
        idioma = get_idioma()

        ctk.CTkLabel(
            c,
            text=t("apartados", idioma),
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#FFFFFF"
        ).pack(anchor="w", pady=(0, 10))

        ctk.CTkButton(
            c,
            text=f"+ {t('nuevo_apartado', idioma)}",
            fg_color="#E8751A",
            hover_color="#c45e0e",
            text_color="#FFFFFF",
            command=lambda: nuevo_apartado(recargar)
        ).pack(anchor="w", pady=(0, 15))

        mostrar_tabla(c, recargar)

    construir(content)


def campo_autocomplete(ventana, label_text, clientes):
    ctk.CTkLabel(
        ventana,
        text=label_text,
        text_color="#AAAAAA"
    ).pack(anchor="w", padx=30)

    contenedor = ctk.CTkFrame(ventana, fg_color="transparent")
    contenedor.pack(padx=30, pady=(2, 8), fill="x")

    entrada = ctk.CTkEntry(contenedor, width=360)
    entrada.pack()

    sugerencias_frame = ctk.CTkFrame(
        contenedor,
        fg_color="#2a2a2a",
        corner_radius=6
    )

    def actualizar_sugerencias(event=None):
        texto = entrada.get().strip().lower()

        for w in sugerencias_frame.winfo_children():
            w.destroy()

        if not texto:
            sugerencias_frame.pack_forget()
            return

        coincidencias = [
            cliente for cliente in clientes
            if texto in cliente.lower()
        ][:5]

        if not coincidencias:
            sugerencias_frame.pack_forget()
            return

        sugerencias_frame.pack(fill="x", pady=(2, 0))

        for nombre in coincidencias:
            def seleccionar(n=nombre):
                entrada.delete(0, "end")
                entrada.insert(0, n)
                sugerencias_frame.pack_forget()

            ctk.CTkButton(
                sugerencias_frame,
                text=nombre,
                fg_color="transparent",
                hover_color="#3a3a3a",
                text_color="#FFFFFF",
                anchor="w",
                height=28,
                command=seleccionar
            ).pack(fill="x", padx=4, pady=1)

    entrada.bind("<KeyRelease>", actualizar_sugerencias)
    return entrada


def cargar_productos():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, nombre, cantidad, precio_menudeo
        FROM productos
        WHERE cantidad > 0
        ORDER BY nombre ASC
    """)
    productos = cursor.fetchall()
    conn.close()
    return productos


def cargar_clientes():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT nombre FROM clientes ORDER BY nombre")
    clientes = [r[0] for r in cursor.fetchall()]
    conn.close()
    return clientes


def nuevo_apartado(callback):
    from config.translations import t
    idioma = get_idioma()

    productos = cargar_productos()
    clientes = cargar_clientes()

    if not productos:
        mostrar_alerta(
            "Sin productos",
            "No hay productos disponibles para apartar."
        )
        return

    ventana = ctk.CTkToplevel()
    ventana.title(t("nuevo_apartado", idioma))
    ventana.geometry("430x590")
    ventana.grab_set()
    ventana.resizable(False, False)

    ctk.CTkLabel(
        ventana,
        text=t("nuevo_apartado", idioma),
        font=ctk.CTkFont(size=16, weight="bold")
    ).pack(pady=20)

    ctk.CTkLabel(
        ventana,
        text=t("producto", idioma),
        text_color="#AAAAAA"
    ).pack(anchor="w", padx=30)

    nombres = [
        f"{p[1]} | Disp: {p[2]}"
        for p in productos
    ]

    mapa_productos = {
        f"{p[1]} | Disp: {p[2]}": {
            "id": p[0],
            "nombre": p[1],
            "stock": p[2],
            "precio": p[3] or 0
        }
        for p in productos
    }

    seleccion = ctk.StringVar(value=nombres[0])

    ctk.CTkOptionMenu(
        ventana,
        values=nombres,
        variable=seleccion,
        width=360
    ).pack(padx=30, pady=(2, 10))

    entrada_cliente = campo_autocomplete(
        ventana,
        t("clientes", idioma),
        clientes
    )

    entradas = {}

    for key in ["cantidad", "fecha_entrega", "notas"]:
        ctk.CTkLabel(
            ventana,
            text=t(key, idioma),
            text_color="#AAAAAA"
        ).pack(anchor="w", padx=30)

        entrada = ctk.CTkEntry(ventana, width=360)

        if key == "cantidad":
            entrada.insert(0, "1")

        entrada.pack(padx=30, pady=(2, 10))
        entradas[key] = entrada

    def guardar(event=None):
        cliente = entrada_cliente.get().strip()

        if not cliente:
            mostrar_alerta(
                t("campo_requerido", idioma),
                f"{t('falta_llenar', idioma)}: {t('clientes', idioma)}",
                ventana
            )
            return

        producto_info = mapa_productos.get(seleccion.get())

        if not producto_info:
            mostrar_alerta("Error", "Selecciona un producto válido.", ventana)
            return

        cantidad = entero_seguro(entradas["cantidad"].get(), 1)

        if cantidad <= 0:
            mostrar_alerta("Error", "La cantidad debe ser mayor a 0.", ventana)
            return

        if cantidad > producto_info["stock"]:
            mostrar_alerta(
                "Stock insuficiente",
                f"No puedes apartar {cantidad} piezas.\n"
                f"Solo hay {producto_info['stock']} disponibles.",
                ventana
            )
            return

        fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M")

        try:
            conn = conectar()
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO apartados
                (cliente, producto_id, cantidad, fecha, fecha_entrega, notas, estado)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                cliente,
                producto_info["id"],
                cantidad,
                fecha_actual,
                entradas["fecha_entrega"].get().strip(),
                entradas["notas"].get().strip(),
                "pendiente"
            ))

            conn.commit()
            conn.close()

            ventana.destroy()
            callback()

        except sqlite3.Error as e:
            mostrar_alerta("Error BD", str(e), ventana)

    ventana.bind("<Return>", guardar)

    ctk.CTkButton(
        ventana,
        text=t("guardar", idioma),
        fg_color="#E8751A",
        hover_color="#c45e0e",
        command=guardar
    ).pack(pady=15)


def editar_apartado(apartado_id, callback):
    from config.translations import t
    idioma = get_idioma()

    try:
        conn = conectar()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM apartados WHERE id=?", (apartado_id,))
        apartado = cursor.fetchone()

        if not apartado:
            conn.close()
            mostrar_alerta("Error", "El apartado ya no existe.")
            return

        cursor.execute("""
            SELECT id, nombre, cantidad, precio_menudeo
            FROM productos
            ORDER BY nombre ASC
        """)
        productos = cursor.fetchall()

        cursor.execute("SELECT nombre FROM clientes ORDER BY nombre")
        clientes = [r[0] for r in cursor.fetchall()]

        conn.close()

    except Exception as e:
        mostrar_alerta("Error BD", str(e))
        return

    if not productos:
        mostrar_alerta("Sin productos", "No hay productos registrados.")
        return

    ventana = ctk.CTkToplevel()
    ventana.title(t("editar_apartado", idioma))
    ventana.geometry("430x590")
    ventana.grab_set()
    ventana.resizable(False, False)

    ctk.CTkLabel(
        ventana,
        text=t("editar_apartado", idioma),
        font=ctk.CTkFont(size=16, weight="bold")
    ).pack(pady=20)

    ctk.CTkLabel(
        ventana,
        text=t("producto", idioma),
        text_color="#AAAAAA"
    ).pack(anchor="w", padx=30)

    nombres = [
        f"{p[1]} | Disp: {p[2]}"
        for p in productos
    ]

    mapa_productos = {
        f"{p[1]} | Disp: {p[2]}": {
            "id": p[0],
            "nombre": p[1],
            "stock": p[2],
            "precio": p[3] or 0
        }
        for p in productos
    }

    producto_actual = None

    for nombre_combo, info in mapa_productos.items():
        if info["id"] == apartado[2]:
            producto_actual = nombre_combo
            break

    if not producto_actual:
        producto_actual = nombres[0]

    seleccion = ctk.StringVar(value=producto_actual)

    ctk.CTkOptionMenu(
        ventana,
        values=nombres,
        variable=seleccion,
        width=360
    ).pack(padx=30, pady=(2, 10))

    entrada_cliente = campo_autocomplete(
        ventana,
        t("clientes", idioma),
        clientes
    )
    entrada_cliente.insert(0, apartado[1] or "")

    entradas = {}

    valores = {
        "cantidad": apartado[3],
        "fecha_entrega": apartado[5],
        "notas": apartado[6],
    }

    for key in ["cantidad", "fecha_entrega", "notas"]:
        ctk.CTkLabel(
            ventana,
            text=t(key, idioma),
            text_color="#AAAAAA"
        ).pack(anchor="w", padx=30)

        entrada = ctk.CTkEntry(ventana, width=360)
        entrada.insert(0, str(valores.get(key) or ""))
        entrada.pack(padx=30, pady=(2, 10))
        entradas[key] = entrada

    def guardar(event=None):
        cliente = entrada_cliente.get().strip()

        if not cliente:
            mostrar_alerta("Error", "El cliente es obligatorio.", ventana)
            return

        producto_info = mapa_productos.get(seleccion.get())

        if not producto_info:
            mostrar_alerta("Error", "Selecciona un producto válido.", ventana)
            return

        cantidad = entero_seguro(entradas["cantidad"].get(), 1)

        if cantidad <= 0:
            mostrar_alerta("Error", "La cantidad debe ser mayor a 0.", ventana)
            return

        try:
            conn = conectar()
            cursor = conn.cursor()

            cursor.execute("""
                UPDATE apartados
                SET cliente=?,
                    producto_id=?,
                    cantidad=?,
                    fecha_entrega=?,
                    notas=?
                WHERE id=?
            """, (
                cliente,
                producto_info["id"],
                cantidad,
                entradas["fecha_entrega"].get().strip(),
                entradas["notas"].get().strip(),
                apartado_id
            ))

            conn.commit()
            conn.close()

            ventana.destroy()
            callback()

        except sqlite3.Error as e:
            mostrar_alerta("Error BD", str(e), ventana)

    ventana.bind("<Return>", guardar)

    ctk.CTkButton(
        ventana,
        text=t("guardar_cambios", idioma),
        fg_color="#E8751A",
        hover_color="#c45e0e",
        command=guardar
    ).pack(pady=15)


def mostrar_tabla(content, recargar):
    from config.translations import t
    idioma = get_idioma()

    try:
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT a.id, a.cliente, p.nombre, a.cantidad,
                   a.fecha_entrega, a.estado
            FROM apartados a
            LEFT JOIN productos p ON a.producto_id = p.id
            ORDER BY a.id DESC
        """)
        apartados = cursor.fetchall()
        conn.close()

    except Exception as e:
        mostrar_alerta("Error BD", str(e))
        apartados = []

    tabla = ctk.CTkScrollableFrame(
        content,
        fg_color="#1a1a1a",
        corner_radius=10
    )
    tabla.pack(fill="both", expand=True)

    if not apartados:
        ctk.CTkLabel(
            tabla,
            text=t("sin_apartados", idioma),
            text_color="#555555"
        ).pack(pady=40)
        return

    encabezado = ctk.CTkFrame(tabla, fg_color="#111111", corner_radius=6)
    encabezado.pack(fill="x", padx=8, pady=(8, 4))

    columnas = [
        (t("clientes", idioma), 140),
        (t("producto", idioma), 160),
        (t("cantidad", idioma), 70),
        (t("fecha_entrega", idioma), 120),
        (t("estado", idioma), 90),
    ]

    for texto, ancho in columnas:
        ctk.CTkLabel(
            encabezado,
            text=texto,
            text_color="#777777",
            width=ancho,
            anchor="w",
            font=ctk.CTkFont(size=10, weight="bold")
        ).pack(side="left", padx=4, pady=6)

    for a in apartados:
        fila = ctk.CTkFrame(tabla, fg_color="#222222", corner_radius=6)
        fila.pack(fill="x", padx=8, pady=3)

        estado = a[5] or "pendiente"

        color_estado = "#E8751A" if estado == "pendiente" else "#3B6D11"
        estado_txt = (
            t("pendiente", idioma)
            if estado == "pendiente"
            else t("entregado", idioma)
        )

        ctk.CTkLabel(
            fila,
            text=a[1],
            text_color="#FFFFFF",
            width=140,
            anchor="w"
        ).pack(side="left", padx=4, pady=7)

        ctk.CTkLabel(
            fila,
            text=a[2] or "Producto eliminado",
            text_color="#888888",
            width=160,
            anchor="w"
        ).pack(side="left", padx=4)

        ctk.CTkLabel(
            fila,
            text=str(a[3]),
            text_color="#AAAAAA",
            width=70,
            anchor="w"
        ).pack(side="left", padx=4)

        ctk.CTkLabel(
            fila,
            text=a[4] or "",
            text_color="#AAAAAA",
            width=120,
            anchor="w"
        ).pack(side="left", padx=4)

        ctk.CTkLabel(
            fila,
            text=estado_txt,
            text_color=color_estado,
            width=90,
            anchor="w",
            font=ctk.CTkFont(size=11, weight="bold")
        ).pack(side="left", padx=4)

        if estado == "pendiente":
            ctk.CTkButton(
                fila,
                text=t("entregar", idioma),
                width=70,
                height=26,
                fg_color="#1a3a1a",
                hover_color="#2a5a2a",
                command=lambda aid=a[0]: entregar(aid, recargar)
            ).pack(side="right", padx=4, pady=4)

        ctk.CTkButton(
            fila,
            text=t("editar", idioma),
            width=60,
            height=26,
            fg_color="#333333",
            hover_color="#444444",
            command=lambda aid=a[0]: editar_apartado(aid, recargar)
        ).pack(side="right", padx=4, pady=4)

        ctk.CTkButton(
            fila,
            text=t("borrar", idioma),
            width=60,
            height=26,
            fg_color="#7a1a1a",
            hover_color="#a02020",
            command=lambda aid=a[0]: borrar(aid, recargar)
        ).pack(side="right", padx=4, pady=4)


def entregar(apartado_id, callback):
    def confirmar_entrega():
        try:
            conn = conectar()
            cursor = conn.cursor()

            cursor.execute("""
                SELECT a.cliente, a.producto_id, a.cantidad,
                       p.precio_menudeo, p.cantidad
                FROM apartados a
                JOIN productos p ON a.producto_id = p.id
                WHERE a.id = ? AND a.estado = 'pendiente'
            """, (apartado_id,))

            data = cursor.fetchone()

            if not data:
                conn.close()
                mostrar_alerta("Error", "El apartado no existe o ya fue entregado.")
                return

            cliente, prod_id, cant, precio, stock_actual = data

            if stock_actual < cant:
                conn.close()
                mostrar_alerta(
                    "Stock insuficiente",
                    f"No hay suficiente inventario.\n"
                    f"Necesitas {cant}, disponible {stock_actual}."
                )
                return

            total_venta = (precio or 0) * cant
            fecha_venta = datetime.now().strftime("%Y-%m-%d %H:%M")

            cursor.execute("BEGIN")

            cursor.execute("""
                INSERT INTO ventas (fecha, total, notas)
                VALUES (?, ?, ?)
            """, (
                fecha_venta,
                total_venta,
                f"Apartado ID: {apartado_id} - Cliente: {cliente}"
            ))

            venta_id = cursor.lastrowid

            cursor.execute("""
                INSERT INTO venta_detalle
                (venta_id, producto_id, cantidad, precio)
                VALUES (?, ?, ?, ?)
            """, (
                venta_id,
                prod_id,
                cant,
                precio or 0
            ))

            cursor.execute("""
                UPDATE productos
                SET cantidad = cantidad - ?
                WHERE id = ? AND cantidad >= ?
            """, (
                cant,
                prod_id,
                cant
            ))

            if cursor.rowcount == 0:
                conn.rollback()
                conn.close()
                mostrar_alerta("Error", "No se pudo descontar inventario.")
                return

            cursor.execute("""
                UPDATE apartados
                SET estado='entregado'
                WHERE id=?
            """, (apartado_id,))

            conn.commit()
            conn.close()

            registrar_movimiento(
                prod_id,
                "APARTADO_ENTREGADO",
                cant,
                f"Apartado #{apartado_id} entregado. Venta #{venta_id}"
            )

            callback()

        except sqlite3.Error as e:
            try:
                conn.rollback()
                conn.close()
            except Exception:
                pass

            mostrar_alerta("Error BD", str(e))

        except Exception as e:
            mostrar_alerta("Error", str(e))

    confirmar(
        "Confirmar entrega",
        "¿Deseas entregar este apartado y registrarlo como venta?",
        confirmar_entrega
    )


def borrar(apartado_id, callback):
    def eliminar():
        try:
            conn = conectar()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM apartados WHERE id=?", (apartado_id,))
            conn.commit()
            conn.close()
            callback()

        except Exception as e:
            mostrar_alerta("Error BD", str(e))

    confirmar(
        "Confirmar eliminación",
        "¿Seguro que deseas eliminar este apartado?",
        eliminar
    )