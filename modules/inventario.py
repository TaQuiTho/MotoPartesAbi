import customtkinter as ctk
from database.db import conectar
from config.translations import t
import os
import json
import sqlite3
from tkinter import filedialog
import shutil
from datetime import datetime

try:
    from PIL import Image
except Exception:
    Image = None


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS_PRODUCTOS = os.path.join(BASE_DIR, "assets", "productos")


def get_idioma():
    try:
        config_path = os.path.join(BASE_DIR, "config", "settings.json")
        with open(config_path, "r", encoding="utf-8") as f:
            return json.load(f).get("idioma", "Español")
    except Exception:
        return "Español"


def mostrar_alerta(titulo, mensaje, parent=None):
    ventana = ctk.CTkToplevel(parent) if parent else ctk.CTkToplevel()
    ventana.title(titulo)
    ventana.geometry("380x170")
    ventana.grab_set()
    ventana.resizable(False, False)

    ctk.CTkLabel(
        ventana,
        text=mensaje,
        text_color="#E8751A",
        font=ctk.CTkFont(size=13, weight="bold"),
        wraplength=340
    ).pack(pady=30)

    ctk.CTkButton(
        ventana,
        text="OK",
        fg_color="#E8751A",
        hover_color="#c45e0e",
        command=ventana.destroy
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

    btns = ctk.CTkFrame(ventana, fg_color="transparent")
    btns.pack(pady=10)

    def aceptar():
        ventana.destroy()
        accion()

    ctk.CTkButton(
        btns,
        text="Cancelar",
        fg_color="#333333",
        hover_color="#444444",
        width=100,
        command=ventana.destroy
    ).pack(side="left", padx=8)

    ctk.CTkButton(
        btns,
        text="Eliminar",
        fg_color="#7a1a1a",
        hover_color="#a02020",
        width=100,
        command=aceptar
    ).pack(side="left", padx=8)


def entero_seguro(valor, defecto=0):
    try:
        return int(str(valor).strip())
    except Exception:
        return defecto


def decimal_seguro(valor, defecto=0.0):
    try:
        texto = str(valor).strip().replace(",", ".")
        return float(texto)
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


def obtener_stock_minimo_default():
    try:
        config_path = os.path.join(BASE_DIR, "config", "settings.json")
        with open(config_path, "r", encoding="utf-8") as f:
            return int(json.load(f).get("stock_minimo", 5))
    except Exception:
        return 5


def guardar_imagen_producto(ruta_origen):
    if not ruta_origen:
        return ""

    try:
        os.makedirs(ASSETS_PRODUCTOS, exist_ok=True)

        nombre_original = os.path.basename(ruta_origen)
        nombre, ext = os.path.splitext(nombre_original)
        ext = ext.lower()

        if ext not in [".png", ".jpg", ".jpeg", ".webp"]:
            return ""

        nombre_limpio = "".join(
            c for c in nombre if c.isalnum() or c in ("_", "-", " ")
        ).strip().replace(" ", "_")

        nuevo_nombre = f"{nombre_limpio}_{datetime.now().strftime('%Y%m%d_%H%M%S')}{ext}"
        destino = os.path.join(ASSETS_PRODUCTOS, nuevo_nombre)

        shutil.copy2(ruta_origen, destino)

        return os.path.join("assets", "productos", nuevo_nombre)

    except Exception as e:
        print("ERROR copiando imagen:", e)
        return ""


def resolver_ruta_imagen(ruta):
    if not ruta:
        return ""

    if os.path.isabs(ruta):
        return ruta

    return os.path.join(BASE_DIR, ruta)


def cargar_ctk_imagen(ruta, size=(54, 54)):
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


def guardar_compatibilidades(producto_id, texto):
    try:
        conn = conectar()
        cursor = conn.cursor()

        cursor.execute("DELETE FROM compatibilidades WHERE producto_id=?", (producto_id,))

        partes = []
        for linea in texto.replace(",", "\n").splitlines():
            vehiculo = linea.strip()
            if vehiculo and vehiculo not in partes:
                partes.append(vehiculo)

        for vehiculo in partes:
            cursor.execute("""
                INSERT INTO compatibilidades (producto_id, vehiculo)
                VALUES (?, ?)
            """, (producto_id, vehiculo))

        conn.commit()
        conn.close()
    except Exception as e:
        print("ERROR compatibilidades:", e)


def obtener_compatibilidades(producto_id):
    try:
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT vehiculo
            FROM compatibilidades
            WHERE producto_id=?
            ORDER BY vehiculo ASC
        """, (producto_id,))
        datos = [r[0] for r in cursor.fetchall()]
        conn.close()
        return "\n".join(datos)
    except Exception:
        return ""


def obtener_categorias():
    try:
        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT DISTINCT categoria
            FROM productos
            WHERE categoria IS NOT NULL AND categoria != ''
            ORDER BY categoria ASC
        """)
        categorias = [r[0] for r in cursor.fetchall()]
        conn.close()
        return categorias
    except Exception:
        return []


def agregar_producto(callback):
    idioma = get_idioma()

    ventana = ctk.CTkToplevel()
    ventana.title(t("agregar_producto", idioma))
    ventana.geometry("480x820")
    ventana.grab_set()
    ventana.resizable(False, False)

    ctk.CTkLabel(
        ventana,
        text=t("agregar_producto", idioma),
        font=ctk.CTkFont(size=18, weight="bold")
    ).pack(pady=18)

    scroll = ctk.CTkScrollableFrame(ventana, fg_color="transparent")
    scroll.pack(fill="both", expand=True, padx=25, pady=(0, 10))

    campos_keys = [
        "nombre",
        "marca",
        "sku",
        "cantidad",
        "precio_costo",
        "precio_menudeo",
        "precio_mayoreo",
        "stock_minimo",
        "descripcion"
    ]

    entradas = {}
    ruta_imagen = ctk.StringVar(value="")

    for key in campos_keys:
        ctk.CTkLabel(scroll, text=t(key, idioma), text_color="#AAAAAA").pack(anchor="w", pady=(4, 0))
        entrada = ctk.CTkEntry(scroll, width=390)

        if key == "cantidad":
            entrada.insert(0, "0")
        elif key == "stock_minimo":
            entrada.insert(0, str(obtener_stock_minimo_default()))
        elif key in ["precio_costo", "precio_menudeo", "precio_mayoreo"]:
            entrada.insert(0, "0")

        entrada.pack(pady=(2, 10))
        entradas[key] = entrada

    ctk.CTkLabel(scroll, text="Categoría", text_color="#AAAAAA").pack(anchor="w", pady=(4, 0))
    entrada_categoria = ctk.CTkEntry(scroll, width=390)
    entrada_categoria.pack(pady=(2, 10))

    ctk.CTkLabel(scroll, text="Imagen", text_color="#AAAAAA").pack(anchor="w", pady=(4, 0))

    frame_img = ctk.CTkFrame(scroll, fg_color="transparent")
    frame_img.pack(fill="x", pady=(2, 10))

    lbl_imagen = ctk.CTkLabel(frame_img, text="Sin imagen seleccionada", text_color="#888888")
    lbl_imagen.pack(side="left")

    def seleccionar_imagen():
        archivo = filedialog.askopenfilename(
            title="Seleccionar imagen",
            filetypes=[("Imágenes", "*.png *.jpg *.jpeg *.webp")]
        )

        if archivo:
            ruta_imagen.set(archivo)
            lbl_imagen.configure(text=os.path.basename(archivo))

    ctk.CTkButton(
        frame_img,
        text="Seleccionar",
        width=120,
        fg_color="#333333",
        hover_color="#444444",
        command=seleccionar_imagen
    ).pack(side="right")

    ctk.CTkLabel(scroll, text="Compatibilidad de motos", text_color="#AAAAAA").pack(anchor="w", pady=(4, 0))
    txt_compat = ctk.CTkTextbox(scroll, width=390, height=80)
    txt_compat.insert("1.0", "Ejemplo: Italika FT150\nHonda Cargo 150")
    txt_compat.pack(pady=(2, 10))

    def guardar(event=None):
        nombre = entradas["nombre"].get().strip()
        marca = entradas["marca"].get().strip()
        sku = entradas["sku"].get().strip()
        descripcion = entradas["descripcion"].get().strip()
        categoria = entrada_categoria.get().strip()

        if not nombre:
            mostrar_alerta(
                t("campo_requerido", idioma),
                f"{t('falta_llenar', idioma)}: {t('nombre', idioma)}",
                ventana
            )
            return

        cantidad = entero_seguro(entradas["cantidad"].get(), 0)
        stock_minimo = entero_seguro(entradas["stock_minimo"].get(), obtener_stock_minimo_default())
        precio_costo = decimal_seguro(entradas["precio_costo"].get(), 0)
        precio_menudeo = decimal_seguro(entradas["precio_menudeo"].get(), 0)
        precio_mayoreo = decimal_seguro(entradas["precio_mayoreo"].get(), 0)

        if cantidad < 0:
            mostrar_alerta("Error", "La cantidad no puede ser negativa.", ventana)
            return

        if stock_minimo < 0:
            mostrar_alerta("Error", "El stock mínimo no puede ser negativo.", ventana)
            return

        if precio_costo < 0 or precio_menudeo < 0 or precio_mayoreo < 0:
            mostrar_alerta("Error", "Los precios no pueden ser negativos.", ventana)
            return

        imagen_guardada = guardar_imagen_producto(ruta_imagen.get())

        try:
            conn = conectar()
            cursor = conn.cursor()

            if sku:
                cursor.execute("SELECT id FROM productos WHERE sku = ?", (sku,))
                if cursor.fetchone():
                    conn.close()
                    mostrar_alerta("SKU duplicado", "Ya existe un producto con ese SKU.", ventana)
                    return

            cursor.execute("""
                INSERT INTO productos
                (nombre, marca, sku, cantidad, precio_costo,
                 precio_menudeo, precio_mayoreo, stock_minimo, descripcion,
                 categoria, imagen)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                nombre,
                marca,
                sku if sku else None,
                cantidad,
                precio_costo,
                precio_menudeo,
                precio_mayoreo,
                stock_minimo,
                descripcion,
                categoria,
                imagen_guardada
            ))

            producto_id = cursor.lastrowid
            conn.commit()
            conn.close()

            compat_text = txt_compat.get("1.0", "end").strip()
            compat_text = compat_text.replace("Ejemplo: Italika FT150", "").strip()
            guardar_compatibilidades(producto_id, compat_text)

            if cantidad > 0:
                registrar_movimiento(producto_id, "ENTRADA", cantidad, "Producto agregado al inventario")

            ventana.destroy()
            callback()

        except sqlite3.IntegrityError as e:
            mostrar_alerta("Error BD", f"Error de integridad:\n{e}", ventana)
        except Exception as e:
            mostrar_alerta("Error BD", str(e), ventana)

    ventana.bind("<Return>", guardar)

    ctk.CTkButton(
        ventana,
        text=t("guardar", idioma),
        fg_color="#E8751A",
        hover_color="#c45e0e",
        height=36,
        command=guardar
    ).pack(pady=12)


def editar_producto(producto_id, callback):
    idioma = get_idioma()

    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, nombre, marca, sku, cantidad, precio_costo,
               precio_menudeo, precio_mayoreo, stock_minimo, descripcion,
               categoria, imagen
        FROM productos
        WHERE id=?
    """, (producto_id,))
    p = cursor.fetchone()
    conn.close()

    if not p:
        mostrar_alerta("Error", "El producto ya no existe.")
        return

    ventana = ctk.CTkToplevel()
    ventana.title(t("editar_producto", idioma))
    ventana.geometry("480x820")
    ventana.grab_set()
    ventana.resizable(False, False)

    ctk.CTkLabel(
        ventana,
        text=t("editar_producto", idioma),
        font=ctk.CTkFont(size=18, weight="bold")
    ).pack(pady=18)

    scroll = ctk.CTkScrollableFrame(ventana, fg_color="transparent")
    scroll.pack(fill="both", expand=True, padx=25, pady=(0, 10))

    campos_keys = [
        "nombre",
        "marca",
        "sku",
        "cantidad",
        "precio_costo",
        "precio_menudeo",
        "precio_mayoreo",
        "stock_minimo",
        "descripcion"
    ]

    valores = {
        "nombre": p[1],
        "marca": p[2],
        "sku": p[3],
        "cantidad": p[4],
        "precio_costo": p[5],
        "precio_menudeo": p[6],
        "precio_mayoreo": p[7],
        "stock_minimo": p[8],
        "descripcion": p[9],
    }

    categoria_actual = p[10] or ""
    imagen_actual = p[11] or ""

    stock_anterior = int(p[4] or 0)
    entradas = {}
    ruta_imagen = ctk.StringVar(value="")

    for key in campos_keys:
        ctk.CTkLabel(scroll, text=t(key, idioma), text_color="#AAAAAA").pack(anchor="w", pady=(4, 0))

        entrada = ctk.CTkEntry(scroll, width=390)
        entrada.insert(0, str(valores.get(key, "") if valores.get(key) is not None else ""))
        entrada.pack(pady=(2, 10))
        entradas[key] = entrada

    ctk.CTkLabel(scroll, text="Categoría", text_color="#AAAAAA").pack(anchor="w", pady=(4, 0))
    entrada_categoria = ctk.CTkEntry(scroll, width=390)
    entrada_categoria.insert(0, categoria_actual)
    entrada_categoria.pack(pady=(2, 10))

    ctk.CTkLabel(scroll, text="Imagen", text_color="#AAAAAA").pack(anchor="w", pady=(4, 0))

    frame_img = ctk.CTkFrame(scroll, fg_color="transparent")
    frame_img.pack(fill="x", pady=(2, 10))

    lbl_imagen = ctk.CTkLabel(
        frame_img,
        text=os.path.basename(imagen_actual) if imagen_actual else "Sin imagen",
        text_color="#888888"
    )
    lbl_imagen.pack(side="left")

    def seleccionar_imagen():
        archivo = filedialog.askopenfilename(
            title="Seleccionar imagen",
            filetypes=[("Imágenes", "*.png *.jpg *.jpeg *.webp")]
        )

        if archivo:
            ruta_imagen.set(archivo)
            lbl_imagen.configure(text=os.path.basename(archivo))

    ctk.CTkButton(
        frame_img,
        text="Cambiar",
        width=120,
        fg_color="#333333",
        hover_color="#444444",
        command=seleccionar_imagen
    ).pack(side="right")

    ctk.CTkLabel(scroll, text="Compatibilidad de motos", text_color="#AAAAAA").pack(anchor="w", pady=(4, 0))
    txt_compat = ctk.CTkTextbox(scroll, width=390, height=90)
    txt_compat.insert("1.0", obtener_compatibilidades(producto_id))
    txt_compat.pack(pady=(2, 10))

    def guardar(event=None):
        nombre = entradas["nombre"].get().strip()
        marca = entradas["marca"].get().strip()
        sku = entradas["sku"].get().strip()
        descripcion = entradas["descripcion"].get().strip()
        categoria = entrada_categoria.get().strip()

        if not nombre:
            mostrar_alerta(
                t("campo_requerido", idioma),
                f"{t('falta_llenar', idioma)}: {t('nombre', idioma)}",
                ventana
            )
            return

        cantidad = entero_seguro(entradas["cantidad"].get(), 0)
        stock_minimo = entero_seguro(entradas["stock_minimo"].get(), obtener_stock_minimo_default())
        precio_costo = decimal_seguro(entradas["precio_costo"].get(), 0)
        precio_menudeo = decimal_seguro(entradas["precio_menudeo"].get(), 0)
        precio_mayoreo = decimal_seguro(entradas["precio_mayoreo"].get(), 0)

        if cantidad < 0:
            mostrar_alerta("Error", "La cantidad no puede ser negativa.", ventana)
            return

        if stock_minimo < 0:
            mostrar_alerta("Error", "El stock mínimo no puede ser negativo.", ventana)
            return

        if precio_costo < 0 or precio_menudeo < 0 or precio_mayoreo < 0:
            mostrar_alerta("Error", "Los precios no pueden ser negativos.", ventana)
            return

        imagen_final = imagen_actual

        if ruta_imagen.get():
            nueva = guardar_imagen_producto(ruta_imagen.get())
            if nueva:
                imagen_final = nueva

        try:
            conn = conectar()
            cursor = conn.cursor()

            if sku:
                cursor.execute(
                    "SELECT id FROM productos WHERE sku = ? AND id != ?",
                    (sku, producto_id)
                )
                if cursor.fetchone():
                    conn.close()
                    mostrar_alerta("SKU duplicado", "Ya existe otro producto con ese SKU.", ventana)
                    return

            cursor.execute("""
                UPDATE productos
                SET nombre=?,
                    marca=?,
                    sku=?,
                    cantidad=?,
                    precio_costo=?,
                    precio_menudeo=?,
                    precio_mayoreo=?,
                    stock_minimo=?,
                    descripcion=?,
                    categoria=?,
                    imagen=?
                WHERE id=?
            """, (
                nombre,
                marca,
                sku if sku else None,
                cantidad,
                precio_costo,
                precio_menudeo,
                precio_mayoreo,
                stock_minimo,
                descripcion,
                categoria,
                imagen_final,
                producto_id
            ))

            conn.commit()
            conn.close()

            guardar_compatibilidades(producto_id, txt_compat.get("1.0", "end").strip())

            diferencia = cantidad - stock_anterior
            if diferencia != 0:
                tipo = "AJUSTE_ENTRADA" if diferencia > 0 else "AJUSTE_SALIDA"
                registrar_movimiento(
                    producto_id,
                    tipo,
                    abs(diferencia),
                    f"Ajuste manual de stock. Antes: {stock_anterior}, Ahora: {cantidad}"
                )

            ventana.destroy()
            callback()

        except sqlite3.IntegrityError as e:
            mostrar_alerta("Error BD", f"Error de integridad:\n{e}", ventana)
        except Exception as e:
            mostrar_alerta("Error BD", str(e), ventana)

    ventana.bind("<Return>", guardar)

    ctk.CTkButton(
        ventana,
        text=t("guardar_cambios", idioma),
        fg_color="#E8751A",
        hover_color="#c45e0e",
        height=36,
        command=guardar
    ).pack(pady=12)


def borrar_producto(producto_id, callback):
    def eliminar():
        try:
            conn = conectar()
            cursor = conn.cursor()

            cursor.execute("SELECT cantidad FROM productos WHERE id=?", (producto_id,))
            row = cursor.fetchone()
            cantidad_actual = row[0] if row else 0

            cursor.execute("DELETE FROM productos WHERE id=?", (producto_id,))
            conn.commit()
            conn.close()

            registrar_movimiento(producto_id, "ELIMINADO", cantidad_actual, "Producto eliminado del inventario")
            callback()

        except Exception as e:
            mostrar_alerta("Error BD", str(e))

    confirmar("Confirmar eliminación", "¿Seguro que deseas eliminar este producto?", eliminar)


def mostrar_inventario(frame):
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
            text=t("inventario", idioma),
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#FFFFFF"
        ).pack(anchor="w", pady=(0, 10))

        top_frame = ctk.CTkFrame(c, fg_color="transparent")
        top_frame.pack(fill="x", pady=(0, 10))

        ctk.CTkButton(
            top_frame,
            text=f"+ {t('agregar_producto', idioma)}",
            fg_color="#E8751A",
            hover_color="#c45e0e",
            text_color="#FFFFFF",
            command=lambda: agregar_producto(recargar)
        ).pack(side="left")

        categorias = ["Todas"] + obtener_categorias()
        categoria_var = ctk.StringVar(value="Todas")

        filtro_categoria = ctk.CTkOptionMenu(
            top_frame,
            values=categorias if categorias else ["Todas"],
            variable=categoria_var,
            width=160,
            command=lambda value: filtrar()
        )
        filtro_categoria.pack(side="right", padx=(8, 0))

        busqueda = ctk.CTkEntry(
            top_frame,
            width=280,
            placeholder_text=f"🔍 {t('buscar', idioma) if t('buscar', idioma) != 'buscar' else 'Buscar...'}"
        )
        busqueda.pack(side="right")

        tabla = ctk.CTkScrollableFrame(c, fg_color="#1a1a1a", corner_radius=10)
        tabla.pack(fill="both", expand=True)

        def filtrar(event=None):
            for widget in tabla.winfo_children():
                widget.destroy()

            categoria = categoria_var.get()
            if categoria == "Todas":
                categoria = ""

            llenar_filas_tabla(tabla, recargar, busqueda.get(), categoria)

        busqueda.bind("<KeyRelease>", filtrar)

        llenar_filas_tabla(tabla, recargar)

    construir(content)


def llenar_filas_tabla(tabla_frame, recargar, filtro="", categoria=""):
    idioma = get_idioma()

    try:
        conn = conectar()
        cursor = conn.cursor()

        query = """
            SELECT id, nombre, marca, sku, cantidad, precio_menudeo,
                   stock_minimo, categoria, imagen
            FROM productos
            WHERE 1=1
        """
        params = []

        if filtro:
            query += """
                AND (
                    nombre LIKE ?
                    OR sku LIKE ?
                    OR marca LIKE ?
                    OR categoria LIKE ?
                    OR descripcion LIKE ?
                )
            """
            params.extend([
                f"%{filtro}%",
                f"%{filtro}%",
                f"%{filtro}%",
                f"%{filtro}%",
                f"%{filtro}%"
            ])

        if categoria:
            query += " AND categoria = ?"
            params.append(categoria)

        query += " ORDER BY nombre ASC"

        cursor.execute(query, params)
        productos = cursor.fetchall()
        conn.close()

    except Exception as e:
        mostrar_alerta("Error BD", str(e))
        productos = []

    if not productos:
        ctk.CTkLabel(
            tabla_frame,
            text=t("sin_productos_reg", idioma),
            text_color="#555555",
            font=ctk.CTkFont(size=14)
        ).pack(pady=40)
        return

    grid = ctk.CTkFrame(tabla_frame, fg_color="transparent")
    grid.pack(fill="both", expand=True, padx=10, pady=10)

    columnas_por_fila = 3

    for index, p in enumerate(productos):
        producto_id = p[0]
        nombre = p[1] or ""
        marca = p[2] or ""
        sku = p[3] or ""
        cantidad = p[4] or 0
        precio = p[5] or 0
        stock_minimo = p[6] or 0
        categoria_txt = p[7] or "Sin categoría"
        imagen = p[8] or ""

        row = index // columnas_por_fila
        col = index % columnas_por_fila

        card = ctk.CTkFrame(
            grid,
            fg_color="#222222",
            corner_radius=14,
            width=250,
            height=330
        )
        card.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
        card.grid_propagate(False)

        img = cargar_ctk_imagen(imagen, size=(120, 110))

        img_box = ctk.CTkFrame(card, fg_color="#1a1a1a", corner_radius=12, height=120)
        img_box.pack(fill="x", padx=12, pady=(12, 8))
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
                font=ctk.CTkFont(size=46)
            ).pack(expand=True)

        if cantidad <= 0:
            estado_txt = t("agotado", idioma) if t("agotado", idioma) != "agotado" else "Agotado"
            estado_color = "#A32D2D"
        elif cantidad <= stock_minimo:
            estado_txt = t("stock_bajo", idioma)
            estado_color = "#E8751A"
        else:
            estado_txt = t("stock_alto", idioma)
            estado_color = "#3B6D11"

        ctk.CTkLabel(
            card,
            text=nombre,
            text_color="#FFFFFF",
            font=ctk.CTkFont(size=14, weight="bold"),
            wraplength=215
        ).pack(anchor="w", padx=14, pady=(2, 2))

        ctk.CTkLabel(
            card,
            text=f"{categoria_txt}  •  {marca}",
            text_color="#888888",
            font=ctk.CTkFont(size=11),
            wraplength=215
        ).pack(anchor="w", padx=14)

        ctk.CTkLabel(
            card,
            text=f"SKU: {sku if sku else '-'}",
            text_color="#666666",
            font=ctk.CTkFont(size=10),
            wraplength=215
        ).pack(anchor="w", padx=14, pady=(2, 0))

        info_frame = ctk.CTkFrame(card, fg_color="transparent")
        info_frame.pack(fill="x", padx=14, pady=(8, 2))

        ctk.CTkLabel(
            info_frame,
            text=f"${precio:.2f}",
            text_color="#E8751A",
            font=ctk.CTkFont(size=18, weight="bold")
        ).pack(side="left")

        ctk.CTkLabel(
            info_frame,
            text=f"Stock: {cantidad}",
            text_color="#FFFFFF",
            font=ctk.CTkFont(size=11, weight="bold")
        ).pack(side="right")

        estado_frame = ctk.CTkFrame(card, fg_color="#1a1a1a", corner_radius=8)
        estado_frame.pack(fill="x", padx=14, pady=(6, 8))

        ctk.CTkLabel(
            estado_frame,
            text=estado_txt,
            text_color=estado_color,
            font=ctk.CTkFont(size=11, weight="bold")
        ).pack(pady=5)

        botones = ctk.CTkFrame(card, fg_color="transparent")
        botones.pack(fill="x", padx=12, pady=(2, 12))

        ctk.CTkButton(
            botones,
            text="Editar",
            width=95,
            height=30,
            fg_color="#333333",
            hover_color="#444444",
            command=lambda pid=producto_id: editar_producto(pid, recargar)
        ).pack(side="left", expand=True, padx=(0, 4))

        ctk.CTkButton(
            botones,
            text="Borrar",
            width=95,
            height=30,
            fg_color="#7a1a1a",
            hover_color="#a02020",
            text_color="white",
            command=lambda pid=producto_id: borrar_producto(pid, recargar)
        ).pack(side="right", expand=True, padx=(4, 0))

    for col in range(columnas_por_fila):
        grid.grid_columnconfigure(col, weight=1)