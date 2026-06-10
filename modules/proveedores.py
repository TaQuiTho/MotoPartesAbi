import customtkinter as ctk
from database.db import conectar
import os
import json
import re
import sqlite3
import webbrowser
from urllib.parse import quote


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


class Tooltip:
    active_tip = None

    def __init__(self, widget, text):
        self.widget = widget
        self.text = text or "Sin notas"
        self.tip = None
        widget.bind("<Enter>", self.show)
        widget.bind("<Leave>", self.hide)

    def show(self, event=None):
        Tooltip.hide_all()

        x = self.widget.winfo_rootx() + 20
        y = self.widget.winfo_rooty() + 30

        self.tip = ctk.CTkToplevel(self.widget)
        Tooltip.active_tip = self.tip
        self.tip.wm_overrideredirect(True)
        self.tip.geometry(f"+{x}+{y}")
        self.tip.attributes("-topmost", True)

        box = ctk.CTkFrame(
            self.tip,
            fg_color="#111111",
            border_color="#E8751A",
            border_width=1,
            corner_radius=10
        )
        box.pack()

        ctk.CTkLabel(
            box,
            text=self.text,
            text_color="#FFFFFF",
            font=ctk.CTkFont(size=12),
            wraplength=280,
            justify="left"
        ).pack(padx=12, pady=10)

    def hide(self, event=None):
        if self.tip:
            try:
                self.tip.destroy()
            except Exception:
                pass
            self.tip = None
            Tooltip.active_tip = None

    @classmethod
    def hide_all(cls):
        if cls.active_tip:
            try:
                cls.active_tip.destroy()
            except Exception:
                pass
            cls.active_tip = None


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


def email_valido(email):
    if not email:
        return True
    patron = r"^[\w\.-]+@[\w\.-]+\.\w+$"
    return re.match(patron, email) is not None


def limpiar_numero_whatsapp(numero):
    limpio = re.sub(r"\D", "", numero or "")

    if len(limpio) == 10:
        limpio = "52" + limpio

    if limpio.startswith("52") and not limpio.startswith("521"):
        limpio = "521" + limpio[2:]

    return limpio


def abrir_whatsapp(telefono, nombre=""):
    numero = limpiar_numero_whatsapp(telefono)

    if not numero:
        mostrar_alerta("WhatsApp", "Este proveedor no tiene teléfono o WhatsApp.")
        return

    mensaje = quote(f"Hola {nombre}, te escribo de Moto Partes Abi.")
    webbrowser.open(f"https://wa.me/{numero}?text={mensaje}")


def proveedor_duplicado(nombre, proveedor_id=None):
    conn = conectar()
    cursor = conn.cursor()

    if proveedor_id:
        cursor.execute(
            "SELECT id FROM proveedores WHERE LOWER(nombre)=LOWER(?) AND id != ?",
            (nombre, proveedor_id)
        )
    else:
        cursor.execute(
            "SELECT id FROM proveedores WHERE LOWER(nombre)=LOWER(?)",
            (nombre,)
        )

    existe = cursor.fetchone()
    conn.close()
    return existe is not None


def exportar_proveedores():
    try:
        import openpyxl
        from datetime import datetime

        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        export_dir = os.path.join(base_dir, "exports")
        os.makedirs(export_dir, exist_ok=True)

        conn = conectar()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT nombre, telefono, whatsapp, email, direccion, categoria, notas
            FROM proveedores
            ORDER BY nombre ASC
        """)
        proveedores = cursor.fetchall()
        conn.close()

        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "Proveedores"
        ws.append([
            "Nombre",
            "Teléfono",
            "WhatsApp",
            "Email",
            "Dirección",
            "Categoría",
            "Notas"
        ])

        for p in proveedores:
            ws.append(list(p))

        nombre_archivo = f"proveedores_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        ruta = os.path.join(export_dir, nombre_archivo)
        wb.save(ruta)

        mostrar_alerta("Exportado", f"Proveedores exportados en:\nexports/{nombre_archivo}")

    except Exception as e:
        mostrar_alerta("Error", f"No se pudo exportar:\n{e}")


def mostrar_proveedores(frame):
    from config.translations import t
    idioma = get_idioma()

    content = ctk.CTkFrame(frame, fg_color="#0f0f0f")
    content.pack(fill="both", expand=True, padx=20, pady=20)

    def recargar(filtro=""):
        for widget in content.winfo_children():
            widget.destroy()
        construir(content, filtro)

    def construir(c, filtro=""):
        idioma = get_idioma()

        ctk.CTkLabel(
            c,
            text=t("proveedores", idioma),
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#FFFFFF"
        ).pack(anchor="w", pady=(0, 10))

        top_frame = ctk.CTkFrame(c, fg_color="transparent")
        top_frame.pack(fill="x", pady=(0, 12))

        ctk.CTkButton(
            top_frame,
            text=f"+ {t('nuevo_proveedor', idioma)}",
            fg_color="#E8751A",
            hover_color="#c45e0e",
            text_color="#FFFFFF",
            command=lambda: nuevo_proveedor(lambda: recargar(filtro))
        ).pack(side="left")

        ctk.CTkButton(
            top_frame,
            text="⬇ Exportar Excel",
            fg_color="#1a3a1a",
            hover_color="#2a5a2a",
            text_color="#FFFFFF",
            command=exportar_proveedores
        ).pack(side="left", padx=8)

        busqueda = ctk.CTkEntry(
            top_frame,
            width=320,
            placeholder_text=f"🔍 {t('buscar', idioma) if t('buscar', idioma) != 'buscar' else 'Buscar...'}"
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
            mostrar_tabla(tabla, lambda: recargar(busqueda.get()), busqueda.get())

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
                SELECT id, nombre, telefono, email, direccion, notas, whatsapp, categoria
                FROM proveedores
                WHERE nombre LIKE ?
                   OR telefono LIKE ?
                   OR email LIKE ?
                   OR direccion LIKE ?
                   OR notas LIKE ?
                   OR whatsapp LIKE ?
                   OR categoria LIKE ?
                ORDER BY nombre ASC
            """, (
                f"%{filtro}%",
                f"%{filtro}%",
                f"%{filtro}%",
                f"%{filtro}%",
                f"%{filtro}%",
                f"%{filtro}%",
                f"%{filtro}%"
            ))
        else:
            cursor.execute("""
                SELECT id, nombre, telefono, email, direccion, notas, whatsapp, categoria
                FROM proveedores
                ORDER BY nombre ASC
            """)

        proveedores = cursor.fetchall()
        conn.close()

    except Exception as e:
        mostrar_alerta("Error BD", str(e))
        proveedores = []

    if not proveedores:
        ctk.CTkLabel(
            content,
            text=t("sin_proveedores", idioma),
            text_color="#555555"
        ).pack(pady=40)
        return

    for p in proveedores:
        proveedor_id = p[0]
        nombre = p[1] or ""
        telefono = p[2] or ""
        email = p[3] or ""
        direccion = p[4] or ""
        notas = p[5] or ""
        whatsapp = p[6] or ""
        categoria = p[7] or "General"

        card = ctk.CTkFrame(content, fg_color="#222222", corner_radius=12)
        card.pack(fill="x", padx=10, pady=6)

        left = ctk.CTkFrame(card, fg_color="transparent")
        left.pack(side="left", fill="both", expand=True, padx=14, pady=10)

        top_line = ctk.CTkFrame(left, fg_color="transparent")
        top_line.pack(fill="x")

        lbl_nombre = ctk.CTkLabel(
            top_line,
            text=nombre,
            text_color="#FFFFFF",
            font=ctk.CTkFont(size=15, weight="bold"),
            anchor="w"
        )
        lbl_nombre.pack(side="left", anchor="w")

        ctk.CTkLabel(
            top_line,
            text=categoria,
            text_color="#E8751A",
            fg_color="#332211",
            corner_radius=10,
            font=ctk.CTkFont(size=10, weight="bold"),
            padx=8,
            pady=3
        ).pack(side="left", padx=10)

        tooltip_text = (
            f"Proveedor:\n{nombre}\n\n"
            f"Categoría: {categoria or '-'}\n"
            f"Teléfono: {telefono or '-'}\n"
            f"WhatsApp: {whatsapp or telefono or '-'}\n"
            f"Email: {email or '-'}\n"
            f"Dirección: {direccion or '-'}\n\n"
            f"Notas:\n{notas if notas else 'Sin notas'}"
        )
        Tooltip(lbl_nombre, tooltip_text)

        ctk.CTkLabel(
            left,
            text=f"📞 {telefono or '-'}    ✉ {email or '-'}",
            text_color="#888888",
            font=ctk.CTkFont(size=11),
            anchor="w"
        ).pack(anchor="w", pady=(4, 0))

        ctk.CTkLabel(
            left,
            text=f"Dirección: {direccion or '-'}",
            text_color="#666666",
            font=ctk.CTkFont(size=10),
            anchor="w",
            wraplength=520
        ).pack(anchor="w", pady=(2, 0))

        if notas:
            ctk.CTkLabel(
                left,
                text=f"📝 {notas}",
                text_color="#E8751A",
                font=ctk.CTkFont(size=10),
                anchor="w",
                wraplength=520
            ).pack(anchor="w", pady=(3, 0))

        right = ctk.CTkFrame(card, fg_color="transparent")
        right.pack(side="right", padx=10, pady=10)

        ctk.CTkLabel(
            right,
            text="Proveedor",
            text_color="#888888",
            font=ctk.CTkFont(size=10)
        ).pack(anchor="e", pady=(0, 6))

        btns = ctk.CTkFrame(right, fg_color="transparent")
        btns.pack(anchor="e")

        ctk.CTkButton(
            btns,
            text="WhatsApp",
            width=80,
            height=28,
            fg_color="#1a3a1a",
            hover_color="#2a5a2a",
            command=lambda tel=whatsapp or telefono, nom=nombre: abrir_whatsapp(tel, nom)
        ).pack(side="left", padx=2)

        ctk.CTkButton(
            btns,
            text=t("editar", idioma),
            width=65,
            height=28,
            fg_color="#333333",
            hover_color="#444444",
            command=lambda pid=proveedor_id: editar_proveedor(pid, recargar)
        ).pack(side="left", padx=2)

        ctk.CTkButton(
            btns,
            text=t("borrar", idioma),
            width=65,
            height=28,
            fg_color="#7a1a1a",
            hover_color="#a02020",
            command=lambda pid=proveedor_id: borrar_proveedor(pid, recargar)
        ).pack(side="left", padx=2)


def nuevo_proveedor(callback):
    from config.translations import t
    idioma = get_idioma()

    ventana = ctk.CTkToplevel()
    ventana.title(t("nuevo_proveedor", idioma))
    ventana.geometry("460x660")
    ventana.grab_set()
    ventana.resizable(False, False)

    ctk.CTkLabel(
        ventana,
        text=t("nuevo_proveedor", idioma),
        font=ctk.CTkFont(size=16, weight="bold")
    ).pack(pady=20)

    scroll = ctk.CTkScrollableFrame(ventana, fg_color="transparent")
    scroll.pack(fill="both", expand=True, padx=25)

    campos_keys = [
        "nombre",
        "telefono",
        "whatsapp",
        "email",
        "direccion",
        "categoria",
        "notas"
    ]

    etiquetas = {
        "whatsapp": "WhatsApp",
        "categoria": "Categoría"
    }

    entradas = {}

    for key in campos_keys:
        ctk.CTkLabel(
            scroll,
            text=etiquetas.get(key, t(key, idioma)),
            text_color="#AAAAAA"
        ).pack(anchor="w")

        entrada = ctk.CTkEntry(scroll, width=380)
        entrada.pack(pady=(2, 10))
        entradas[key] = entrada

    def guardar(event=None):
        nombre = entradas["nombre"].get().strip()
        telefono = entradas["telefono"].get().strip()
        whatsapp = entradas["whatsapp"].get().strip()
        email = entradas["email"].get().strip()
        direccion = entradas["direccion"].get().strip()
        categoria = entradas["categoria"].get().strip()
        notas = entradas["notas"].get().strip()

        if not nombre:
            mostrar_alerta(
                t("campo_requerido", idioma),
                f"{t('falta_llenar', idioma)}: {t('nombre', idioma)}",
                ventana
            )
            return

        if not email_valido(email):
            mostrar_alerta("Email inválido", "Escribe un correo válido o deja el campo vacío.", ventana)
            return

        if proveedor_duplicado(nombre):
            mostrar_alerta("Proveedor duplicado", "Ya existe un proveedor con ese nombre.", ventana)
            return

        try:
            conn = conectar()
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO proveedores
                (nombre, telefono, whatsapp, email, direccion, categoria, notas)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                nombre,
                telefono,
                whatsapp,
                email,
                direccion,
                categoria,
                notas
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


def editar_proveedor(proveedor_id, callback):
    from config.translations import t
    idioma = get_idioma()

    try:
        conn = conectar()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id, nombre, telefono, whatsapp, email, direccion, categoria, notas
            FROM proveedores
            WHERE id=?
        """, (proveedor_id,))

        p = cursor.fetchone()
        conn.close()

    except Exception as e:
        mostrar_alerta("Error BD", str(e))
        return

    if not p:
        mostrar_alerta("Error", "El proveedor ya no existe.")
        return

    ventana = ctk.CTkToplevel()
    ventana.title(t("editar_proveedor", idioma))
    ventana.geometry("460x660")
    ventana.grab_set()
    ventana.resizable(False, False)

    ctk.CTkLabel(
        ventana,
        text=t("editar_proveedor", idioma),
        font=ctk.CTkFont(size=16, weight="bold")
    ).pack(pady=20)

    scroll = ctk.CTkScrollableFrame(ventana, fg_color="transparent")
    scroll.pack(fill="both", expand=True, padx=25)

    campos_keys = [
        "nombre",
        "telefono",
        "whatsapp",
        "email",
        "direccion",
        "categoria",
        "notas"
    ]

    valores = {
        "nombre": p[1],
        "telefono": p[2],
        "whatsapp": p[3],
        "email": p[4],
        "direccion": p[5],
        "categoria": p[6],
        "notas": p[7],
    }

    etiquetas = {
        "whatsapp": "WhatsApp",
        "categoria": "Categoría"
    }

    entradas = {}

    for key in campos_keys:
        ctk.CTkLabel(
            scroll,
            text=etiquetas.get(key, t(key, idioma)),
            text_color="#AAAAAA"
        ).pack(anchor="w")

        entrada = ctk.CTkEntry(scroll, width=380)
        entrada.insert(0, str(valores.get(key) or ""))
        entrada.pack(pady=(2, 10))
        entradas[key] = entrada

    def guardar(event=None):
        nombre = entradas["nombre"].get().strip()
        telefono = entradas["telefono"].get().strip()
        whatsapp = entradas["whatsapp"].get().strip()
        email = entradas["email"].get().strip()
        direccion = entradas["direccion"].get().strip()
        categoria = entradas["categoria"].get().strip()
        notas = entradas["notas"].get().strip()

        if not nombre:
            mostrar_alerta(
                t("campo_requerido", idioma),
                f"{t('falta_llenar', idioma)}: {t('nombre', idioma)}",
                ventana
            )
            return

        if not email_valido(email):
            mostrar_alerta("Email inválido", "Escribe un correo válido o deja el campo vacío.", ventana)
            return

        if proveedor_duplicado(nombre, proveedor_id):
            mostrar_alerta("Proveedor duplicado", "Ya existe otro proveedor con ese nombre.", ventana)
            return

        try:
            conn = conectar()
            cursor = conn.cursor()

            cursor.execute("""
                UPDATE proveedores
                SET nombre=?,
                    telefono=?,
                    whatsapp=?,
                    email=?,
                    direccion=?,
                    categoria=?,
                    notas=?
                WHERE id=?
            """, (
                nombre,
                telefono,
                whatsapp,
                email,
                direccion,
                categoria,
                notas,
                proveedor_id
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


def borrar_proveedor(proveedor_id, callback):
    def eliminar():
        try:
            conn = conectar()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM proveedores WHERE id=?", (proveedor_id,))
            conn.commit()
            conn.close()
            callback()

        except Exception as e:
            mostrar_alerta("Error BD", str(e))

    confirmar(
        "Confirmar eliminación",
        "¿Seguro que deseas eliminar este proveedor?",
        eliminar
    )