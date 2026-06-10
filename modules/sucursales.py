import customtkinter as ctk
from database.db import conectar
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
    ventana = ctk.CTkToplevel(parent) if parent else ctk.CTkToplevel()
    ventana.title(titulo)
    ventana.geometry("370x160")
    ventana.grab_set()
    ventana.resizable(False, False)

    ctk.CTkLabel(
        ventana,
        text=mensaje,
        text_color="#E8751A",
        font=ctk.CTkFont(size=13, weight="bold"),
        wraplength=330
    ).pack(pady=25)

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
        text="Eliminar",
        fg_color="#7a1a1a",
        hover_color="#a02020",
        width=100,
        command=aceptar
    ).pack(side="left", padx=8)


def sucursal_duplicada(nombre, sucursal_id=None):
    conn = conectar()
    cursor = conn.cursor()

    if sucursal_id:
        cursor.execute("""
            SELECT id
            FROM sucursales
            WHERE LOWER(nombre)=LOWER(?)
            AND id != ?
        """, (nombre, sucursal_id))
    else:
        cursor.execute("""
            SELECT id
            FROM sucursales
            WHERE LOWER(nombre)=LOWER(?)
        """, (nombre,))

    existe = cursor.fetchone()
    conn.close()

    return existe is not None


def mostrar_sucursales(frame):
    from config.translations import t
    idioma = get_idioma()

    content = ctk.CTkFrame(frame, fg_color="#0f0f0f")
    content.pack(fill="both", expand=True, padx=20, pady=20)

    def recargar(filtro=""):
        for widget in content.winfo_children():
            widget.destroy()
        construir(content, filtro)

    def construir(c, filtro=""):
        idioma_actual = get_idioma()

        ctk.CTkLabel(
            c,
            text=t("sucursales", idioma_actual),
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#FFFFFF"
        ).pack(anchor="w", pady=(0, 10))

        top_frame = ctk.CTkFrame(c, fg_color="transparent")
        top_frame.pack(fill="x", pady=(0, 12))

        ctk.CTkButton(
            top_frame,
            text=f"+ {t('nueva_sucursal', idioma_actual)}",
            fg_color="#E8751A",
            hover_color="#c45e0e",
            text_color="#FFFFFF",
            command=lambda: nueva_sucursal(lambda: recargar(filtro))
        ).pack(side="left")

        busqueda = ctk.CTkEntry(
            top_frame,
            width=270,
            placeholder_text=f"🔍 {t('buscar', idioma_actual) if t('buscar', idioma_actual) != 'buscar' else 'Buscar...'}"
        )
        busqueda.insert(0, filtro)
        busqueda.pack(side="right")

        tabla = ctk.CTkScrollableFrame(
            c,
            fg_color="#1a1a1a",
            corner_radius=10
        )
        tabla.pack(fill="both", expand=True)

        def filtrar(event=None):
            mostrar_tabla(
                tabla,
                lambda: recargar(busqueda.get()),
                busqueda.get()
            )

        busqueda.bind("<KeyRelease>", filtrar)

        mostrar_tabla(tabla, lambda: recargar(busqueda.get()), filtro)

    construir(content)


def mostrar_tabla(content, recargar, filtro=""):
    from config.translations import t
    idioma = get_idioma()

    for widget in content.winfo_children():
        widget.destroy()

    try:
        conn = conectar()
        cursor = conn.cursor()

        if filtro:
            cursor.execute("""
                SELECT id, nombre, direccion, telefono, gerente, activa
                FROM sucursales
                WHERE nombre LIKE ?
                   OR direccion LIKE ?
                   OR telefono LIKE ?
                   OR gerente LIKE ?
                ORDER BY activa DESC, nombre ASC
            """, (
                f"%{filtro}%",
                f"%{filtro}%",
                f"%{filtro}%",
                f"%{filtro}%"
            ))
        else:
            cursor.execute("""
                SELECT id, nombre, direccion, telefono, gerente, activa
                FROM sucursales
                ORDER BY activa DESC, nombre ASC
            """)

        sucursales = cursor.fetchall()
        conn.close()

    except Exception as e:
        mostrar_alerta("Error BD", str(e))
        sucursales = []

    if not sucursales:
        ctk.CTkLabel(
            content,
            text=t("sin_sucursales", idioma),
            text_color="#555555"
        ).pack(pady=40)
        return

    encabezado = ctk.CTkFrame(content, fg_color="#111111", corner_radius=6)
    encabezado.pack(fill="x", padx=8, pady=(8, 4))

    columnas = [
        (t("nombre", idioma), 160),
        (t("direccion", idioma), 200),
        (t("telefono", idioma), 120),
        (t("gerente", idioma), 140),
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
        ).pack(side="left", padx=5, pady=6)

    for s in sucursales:
        fila = ctk.CTkFrame(
            content,
            fg_color="#222222" if s[5] else "#2d1a1a",
            corner_radius=6
        )
        fila.pack(fill="x", padx=8, pady=3)

        estado_txt = t("activa", idioma) if s[5] else t("inactiva", idioma)
        estado_color = "#3B6D11" if s[5] else "#A32D2D"

        ctk.CTkLabel(
            fila,
            text=s[1],
            text_color="#FFFFFF",
            width=160,
            anchor="w"
        ).pack(side="left", padx=5, pady=7)

        ctk.CTkLabel(
            fila,
            text=s[2] or "",
            text_color="#888888",
            width=200,
            anchor="w"
        ).pack(side="left", padx=5)

        ctk.CTkLabel(
            fila,
            text=s[3] or "",
            text_color="#888888",
            width=120,
            anchor="w"
        ).pack(side="left", padx=5)

        ctk.CTkLabel(
            fila,
            text=s[4] or "",
            text_color="#888888",
            width=140,
            anchor="w"
        ).pack(side="left", padx=5)

        ctk.CTkLabel(
            fila,
            text=estado_txt,
            text_color=estado_color,
            width=90,
            anchor="w",
            font=ctk.CTkFont(size=11, weight="bold")
        ).pack(side="left", padx=5)

        ctk.CTkButton(
            fila,
            text=t("editar", idioma),
            width=60,
            height=26,
            fg_color="#333333",
            hover_color="#444444",
            command=lambda sid=s[0]: editar_sucursal(sid, recargar)
        ).pack(side="right", padx=4, pady=4)

        ctk.CTkButton(
            fila,
            text=t("borrar", idioma),
            width=60,
            height=26,
            fg_color="#7a1a1a",
            hover_color="#a02020",
            command=lambda sid=s[0]: borrar_sucursal(sid, recargar)
        ).pack(side="right", padx=4, pady=4)


def nueva_sucursal(callback):
    from config.translations import t
    idioma = get_idioma()

    ventana = ctk.CTkToplevel()
    ventana.title(t("nueva_sucursal", idioma))
    ventana.geometry("430x480")
    ventana.grab_set()
    ventana.resizable(False, False)

    ctk.CTkLabel(
        ventana,
        text=t("nueva_sucursal", idioma),
        font=ctk.CTkFont(size=16, weight="bold")
    ).pack(pady=20)

    campos_keys = ["nombre", "direccion", "telefono", "gerente"]
    entradas = {}

    for key in campos_keys:
        ctk.CTkLabel(
            ventana,
            text=t(key, idioma),
            text_color="#AAAAAA"
        ).pack(anchor="w", padx=30)

        entrada = ctk.CTkEntry(ventana, width=360)
        entrada.pack(padx=30, pady=(2, 10))
        entradas[key] = entrada

    def guardar(event=None):
        nombre = entradas["nombre"].get().strip()
        direccion = entradas["direccion"].get().strip()
        telefono = entradas["telefono"].get().strip()
        gerente = entradas["gerente"].get().strip()

        if not nombre:
            mostrar_alerta(
                t("campo_requerido", idioma),
                f"{t('falta_llenar', idioma)}: {t('nombre', idioma)}",
                ventana
            )
            return

        if sucursal_duplicada(nombre):
            mostrar_alerta(
                "Sucursal duplicada",
                "Ya existe una sucursal con ese nombre.",
                ventana
            )
            return

        try:
            conn = conectar()
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO sucursales
                (nombre, direccion, telefono, gerente, activa)
                VALUES (?, ?, ?, ?, ?)
            """, (
                nombre,
                direccion,
                telefono,
                gerente,
                1
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


def editar_sucursal(sucursal_id, callback):
    from config.translations import t
    idioma = get_idioma()

    try:
        conn = conectar()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id, nombre, direccion, telefono, gerente, activa
            FROM sucursales
            WHERE id=?
        """, (sucursal_id,))

        s = cursor.fetchone()
        conn.close()

    except Exception as e:
        mostrar_alerta("Error BD", str(e))
        return

    if not s:
        mostrar_alerta("Error", "La sucursal ya no existe.")
        return

    ventana = ctk.CTkToplevel()
    ventana.title(t("editar_sucursal", idioma))
    ventana.geometry("430x540")
    ventana.grab_set()
    ventana.resizable(False, False)

    ctk.CTkLabel(
        ventana,
        text=t("editar_sucursal", idioma),
        font=ctk.CTkFont(size=16, weight="bold")
    ).pack(pady=20)

    campos_keys = ["nombre", "direccion", "telefono", "gerente"]

    valores = {
        "nombre": s[1],
        "direccion": s[2],
        "telefono": s[3],
        "gerente": s[4],
    }

    entradas = {}

    for key in campos_keys:
        ctk.CTkLabel(
            ventana,
            text=t(key, idioma),
            text_color="#AAAAAA"
        ).pack(anchor="w", padx=30)

        entrada = ctk.CTkEntry(ventana, width=360)
        entrada.insert(0, str(valores.get(key) or ""))
        entrada.pack(padx=30, pady=(2, 10))
        entradas[key] = entrada

    ctk.CTkLabel(
        ventana,
        text=t("estado", idioma),
        text_color="#AAAAAA"
    ).pack(anchor="w", padx=30)

    activa_var = ctk.BooleanVar(value=bool(s[5]))

    ctk.CTkCheckBox(
        ventana,
        text=t("activa", idioma),
        variable=activa_var,
        text_color="#FFFFFF"
    ).pack(anchor="w", padx=30, pady=(2, 10))

    def guardar(event=None):
        nombre = entradas["nombre"].get().strip()
        direccion = entradas["direccion"].get().strip()
        telefono = entradas["telefono"].get().strip()
        gerente = entradas["gerente"].get().strip()

        if not nombre:
            mostrar_alerta(
                t("campo_requerido", idioma),
                f"{t('falta_llenar', idioma)}: {t('nombre', idioma)}",
                ventana
            )
            return

        if sucursal_duplicada(nombre, sucursal_id):
            mostrar_alerta(
                "Sucursal duplicada",
                "Ya existe otra sucursal con ese nombre.",
                ventana
            )
            return

        try:
            conn = conectar()
            cursor = conn.cursor()

            cursor.execute("""
                UPDATE sucursales
                SET nombre=?,
                    direccion=?,
                    telefono=?,
                    gerente=?,
                    activa=?
                WHERE id=?
            """, (
                nombre,
                direccion,
                telefono,
                gerente,
                int(activa_var.get()),
                sucursal_id
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


def borrar_sucursal(sucursal_id, callback):
    def eliminar():
        try:
            conn = conectar()
            cursor = conn.cursor()

            cursor.execute("DELETE FROM sucursales WHERE id=?", (sucursal_id,))

            conn.commit()
            conn.close()

            callback()

        except Exception as e:
            mostrar_alerta("Error BD", str(e))

    confirmar(
        "Confirmar eliminación",
        "¿Seguro que deseas eliminar esta sucursal?",
        eliminar
    )