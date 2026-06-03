import customtkinter as ctk
from tkinter import filedialog, messagebox, ttk
from PIL import Image
import os
from datetime import datetime

from src.curp_utils import analizar_curp
from src.excel_service import leer_excel, exportar_excel
from src.database import (
    importar_dataframe_a_mysql,
    buscar_alumno_por_curp,
    obtener_todos_los_alumnos,
    actualizar_alumno
)

# Configuración global
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

# Opciones para comboboxes (basadas en beca Benito Juárez - Media Superior)
OPCIONES_SITUACION = [
    "ACTIVO",
    "REINSCRITO", 
    "NUEVO INGRESO",
    "BAJA TEMPORAL",
    "BAJA DEFINITIVA",
    "CAMBIO DE PLANTEL",
    "CAMBIO DE CARRERA",
    "SUSPENDIDO",
    "EGRESADO"
]

OPCIONES_MODALIDAD = [
    "ESCOLARIZADA",
    "MIXTA",
    "NO ESCOLARIZADA",
    "VIRTUAL",
    "PRESENCIAL"
]

OPCIONES_PERIODO = [
    "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12"
]

OPCIONES_TIPO_PERIODO = [
    "SEMESTRE",
    "CUATRIMESTRE", 
    "TRIMESTRE",
    "ANUAL"
]


class SistemaBecas(ctk.CTk):

    def __init__(self):
        super().__init__()

        self.title("Sistema de Becas - Administración")
        self.geometry("1400x800")
        self.minsize(1200, 600)

        # Configurar grid principal
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Variables
        self.alumno_actual = None
        self.entries = {}
        self.comboboxes = {}
        self.tabla = None

        self.crear_interfaz()

    def crear_interfaz(self):
        # ==================== MENÚ LATERAL ====================
        self.menu = ctk.CTkFrame(
            self,
            width=260,
            corner_radius=0,
            fg_color="#1a2c3e"
        )
        self.menu.grid(row=0, column=0, sticky="nsew")
        self.menu.grid_propagate(False)

        # Logo o título del sistema
        ctk.CTkLabel(
            self.menu,
            text="🎓 Sistema Becas\nBenito Juárez",
            font=("Segoe UI", 20, "bold"),
            text_color="white"
        ).pack(pady=(40, 20), padx=20)

        # Línea separadora
        ctk.CTkFrame(
            self.menu,
            height=2,
            fg_color="#2d4a6e"
        ).pack(fill="x", padx=20, pady=10)

        # Botones del menú
        botones = [
            ("📥 Importación", self.modulo_importacion, "#2ecc71"),
            ("📋 Registros", self.modulo_registros, "#3498db"),
            ("✏️ Captura CURP", self.modulo_captura, "#e67e22"),
            ("📤 Exportación", self.modulo_exportacion, "#9b59b6"),
        ]

        for texto, comando, color in botones:
            btn = ctk.CTkButton(
                self.menu,
                text=texto,
                font=("Segoe UI", 14, "bold"),
                fg_color=color,
                hover_color=self._darken_color(color),
                height=45,
                corner_radius=8,
                command=comando
            )
            btn.pack(fill="x", padx=20, pady=8)

        # Footer del menú
        ctk.CTkFrame(
            self.menu,
            height=2,
            fg_color="#2d4a6e"
        ).pack(fill="x", padx=20, pady=20)

        ctk.CTkLabel(
            self.menu,
            text="Beca Benito Juárez\nMedia Superior 2024",
            font=("Segoe UI", 11),
            text_color="#7f8c8d"
        ).pack(side="bottom", pady=20)

        # ==================== CONTENIDO PRINCIPAL ====================
        self.contenido = ctk.CTkFrame(
            self,
            corner_radius=0,
            fg_color="#f0f2f5"
        )
        self.contenido.grid(row=0, column=1, sticky="nsew")
        self.contenido.grid_columnconfigure(0, weight=1)
        self.contenido.grid_rowconfigure(0, weight=1)

        # Iniciar con módulo de importación
        self.modulo_importacion()

    def _darken_color(self, color):
        """Oscurece un color hexadecimal"""
        if color.startswith("#"):
            r = int(color[1:3], 16)
            g = int(color[3:5], 16)
            b = int(color[5:7], 16)
            return f"#{max(0, r-40):02x}{max(0, g-40):02x}{max(0, b-40):02x}"
        return "#1a5276"

    def limpiar_contenido(self):
        """Limpia el contenido principal"""
        for widget in self.contenido.winfo_children():
            widget.destroy()

    def crear_tarjeta(self, parent, titulo, subtitulo=""):
        """Crea una tarjeta con título y subtítulo"""
        frame = ctk.CTkFrame(parent, corner_radius=15, fg_color="white")
        frame.pack(fill="x", padx=30, pady=(10, 5))

        ctk.CTkLabel(
            frame,
            text=titulo,
            font=("Segoe UI", 18, "bold"),
            text_color="#1a2c3e"
        ).pack(anchor="w", padx=20, pady=(15, 5))

        if subtitulo:
            ctk.CTkLabel(
                frame,
                text=subtitulo,
                font=("Segoe UI", 12),
                text_color="#6c7a8a"
            ).pack(anchor="w", padx=20, pady=(0, 15))

        return frame

    def formatear_fecha(self, fecha):
        """Formatea fecha a formato dd/mm/yyyy"""
        if not fecha or fecha == "":
            return ""
        try:
            if isinstance(fecha, str):
                if "-" in fecha:
                    fecha_obj = datetime.strptime(fecha, "%Y-%m-%d")
                else:
                    return fecha
            else:
                fecha_obj = fecha
            return fecha_obj.strftime("%d/%m/%Y")
        except:
            return str(fecha)

    # =========================
    # IMPORTACIÓN
    # =========================

    def modulo_importacion(self):
        self.limpiar_contenido()

        # Contenedor centrado
        main_frame = ctk.CTkFrame(self.contenido, fg_color="transparent")
        main_frame.grid(row=0, column=0, sticky="nsew")
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_rowconfigure(0, weight=1)

        center_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        center_frame.grid(row=0, column=0)

        # Tarjeta de importación
        tarjeta = ctk.CTkFrame(
            center_frame,
            width=650,
            height=450,
            corner_radius=20,
            fg_color="white"
        )
        tarjeta.pack(pady=50)
        tarjeta.pack_propagate(False)

        # Icono
        ctk.CTkLabel(
            tarjeta,
            text="📂",
            font=("Segoe UI", 64)
        ).pack(pady=(50, 10))

        ctk.CTkLabel(
            tarjeta,
            text="Módulo de Importación",
            font=("Segoe UI", 26, "bold"),
            text_color="#1a2c3e"
        ).pack(pady=10)

        ctk.CTkLabel(
            tarjeta,
            text="Importa tu archivo Excel con los datos de los becarios",
            font=("Segoe UI", 13),
            text_color="#6c7a8a"
        ).pack(pady=5)

        ctk.CTkLabel(
            tarjeta,
            text="El archivo debe contener una columna llamada 'CURP'",
            font=("Segoe UI", 11),
            text_color="#e74c3c"
        ).pack(pady=5)

        # Botón de importar
        btn_importar = ctk.CTkButton(
            tarjeta,
            text="📎 Seleccionar archivo Excel",
            font=("Segoe UI", 15, "bold"),
            fg_color="#2ecc71",
            hover_color="#27ae60",
            height=50,
            width=300,
            corner_radius=12,
            command=self.importar_excel
        )
        btn_importar.pack(pady=40)

    def importar_excel(self):
        ruta = filedialog.askopenfilename(
            title="Seleccionar archivo Excel",
            filetypes=[("Archivos Excel", "*.xlsx"), ("Todos los archivos", "*.*")]
        )

        if not ruta:
            return

        # Crear ventana de progreso
        progreso_ventana = ctk.CTkToplevel(self)
        progreso_ventana.title("Importando...")
        progreso_ventana.geometry("350x120")
        progreso_ventana.transient(self)
        progreso_ventana.grab_set()
        
        ctk.CTkLabel(
            progreso_ventana,
            text="🔄 Procesando archivo...",
            font=("Segoe UI", 14, "bold")
        ).pack(pady=20)
        
        progreso = ctk.CTkProgressBar(progreso_ventana, width=280)
        progreso.pack(pady=10)
        progreso.set(0.5)
        
        self.update()

        try:
            df = leer_excel(ruta)

            if "CURP" not in df.columns:
                progreso_ventana.destroy()
                messagebox.showerror("Error", "El Excel debe tener una columna llamada 'CURP'")
                return

            resultado = importar_dataframe_a_mysql(df)
            total = resultado.get("guardados", 0)
            omitidos = resultado.get("omitidos", 0)
            
            progreso_ventana.destroy()
            
            messagebox.showinfo(
                "✅ Importación exitosa",
                f"Archivo importado correctamente.\n\n📊 Registros guardados: {total}\n⚠️ Registros omitidos: {omitidos}"
            )

            self.modulo_registros()

        except Exception as e:
            progreso_ventana.destroy()
            messagebox.showerror("❌ Error", f"Error al importar:\n{str(e)}")

    # =========================
    # REGISTROS - TABLA MEJORADA
    # =========================

    def modulo_registros(self):
        self.limpiar_contenido()

        # Header
        header = self.crear_tarjeta(self.contenido, "📋 Registros Guardados", "Consulta y gestión de beneficiarios - Beca Benito Juárez")
        header.pack(fill="x", padx=30, pady=(20, 10))

        # Frame para tabla con scroll
        frame_tabla = ctk.CTkFrame(self.contenido, fg_color="white", corner_radius=15)
        frame_tabla.pack(fill="both", expand=True, padx=30, pady=(0, 20))

        try:
            datos = obtener_todos_los_alumnos()
        except Exception as e:
            messagebox.showerror("Error de conexión", f"No se pudo conectar a la base de datos:\n{str(e)}")
            return

        if not datos:
            ctk.CTkLabel(
                frame_tabla,
                text="📭 No hay registros guardados en el sistema",
                font=("Segoe UI", 16),
                text_color="#6c7a8a"
            ).pack(expand=True)
            return

        self.mostrar_tabla_mejorada(frame_tabla, datos)

    def mostrar_tabla_mejorada(self, parent, datos):
        """Muestra una tabla mejorada con diseño cuadriculado"""
        
        # Frame con scroll
        container = ctk.CTkFrame(parent, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=5, pady=5)

        # Canvas para scroll
        canvas = tk.Canvas(container, bg="white", highlightthickness=0)
        scrollbar_y = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
        scrollbar_x = ttk.Scrollbar(container, orient="horizontal", command=canvas.xview)
        canvas.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)

        scrollbar_y.pack(side="right", fill="y")
        scrollbar_x.pack(side="bottom", fill="x")
        canvas.pack(side="left", fill="both", expand=True)

        # Frame interior para la tabla
        tabla_frame = ctk.CTkFrame(canvas, fg_color="white")
        canvas.create_window((0, 0), window=tabla_frame, anchor="nw")

        # Columnas de la tabla
        columnas = [
            ("ID", 50),
            ("CURP", 160),
            ("P. APELLIDO", 120),
            ("S. APELLIDO", 120),
            ("NOMBRE", 150),
            ("FECHA NAC", 100),
            ("SEXO", 60),
            ("ENTIDAD", 130),
            ("SITUACIÓN", 130),
            ("CAUSA", 150),
            ("TIPO PERIODO", 110),
            ("PERIODO", 80),
            ("MODALIDAD", 120)
        ]

        # Encabezados
        for col_idx, (texto, ancho) in enumerate(columnas):
            header = tk.Frame(tabla_frame, bg="#1a2c3e", width=ancho, height=40)
            header.grid(row=0, column=col_idx, sticky="nsew")
            header.grid_propagate(False)
            
            label = tk.Label(
                header, 
                text=texto, 
                bg="#1a2c3e", 
                fg="white", 
                font=("Segoe UI", 11, "bold")
            )
            label.pack(expand=True)

        # Datos
        for row_idx, fila in enumerate(datos, start=1):
            bg_color = "#f8f9fa" if row_idx % 2 == 0 else "white"
            
            for col_idx, (col_name, ancho) in enumerate(columnas):
                valor = fila.get(col_name.lower().replace(" ", "_").replace("á", "a").replace("é", "e").replace("í", "i").replace("ó", "o").replace("ú", "u"), "")
                
                if valor is None:
                    valor = ""
                
                # Formatear fecha
                if col_name == "FECHA NAC" and valor:
                    valor = self.formatear_fecha(valor)
                
                cell = tk.Frame(tabla_frame, bg=bg_color, width=ancho, height=35, relief="solid", bd=1)
                cell.grid(row=row_idx, column=col_idx, sticky="nsew")
                cell.grid_propagate(False)
                
                label = tk.Label(
                    cell, 
                    text=str(valor), 
                    bg=bg_color, 
                    fg="#1a2c3e", 
                    font=("Segoe UI", 10),
                    wraplength=ancho-10
                )
                label.pack(expand=True, padx=5, pady=5)

        # Configurar anchos de columna
        for col_idx, (_, ancho) in enumerate(columnas):
            tabla_frame.grid_columnconfigure(col_idx, minsize=ancho)

        # Configurar scroll
        tabla_frame.update_idletasks()
        canvas.configure(scrollregion=canvas.bbox("all"))

        def on_frame_configure(event):
            canvas.configure(scrollregion=canvas.bbox("all"))

        tabla_frame.bind("<Configure>", on_frame_configure)

        # Contador de registros
        ctk.CTkLabel(
            parent,
            text=f"📊 Total de registros: {len(datos)}",
            font=("Segoe UI", 13, "bold"),
            text_color="#1a2c3e"
        ).pack(pady=10)

    # =========================
    # CAPTURA CURP - MEJORADA
    # =========================

    def modulo_captura(self):
        self.limpiar_contenido()
        self.alumno_actual = None
        self.entries = {}
        self.comboboxes = {}

        # Header
        header = self.crear_tarjeta(self.contenido, "✏️ Captura por CURP", "Buscar, editar y actualizar beneficiarios - Beca Benito Juárez")
        header.pack(fill="x", padx=30, pady=(20, 10))

        # Frame de búsqueda
        frame_busqueda = ctk.CTkFrame(self.contenido, fg_color="white", corner_radius=15)
        frame_busqueda.pack(fill="x", padx=30, pady=(0, 15))

        ctk.CTkLabel(
            frame_busqueda,
            text="🔍 CURP del beneficiario:",
            font=("Segoe UI", 15, "bold")
        ).pack(pady=(20, 5))

        self.entry_curp = ctk.CTkEntry(
            frame_busqueda,
            width=550,
            height=45,
            font=("Segoe UI", 14),
            placeholder_text="Ingrese la CURP a buscar (18 caracteres)"
        )
        self.entry_curp.pack(pady=5)

        ctk.CTkButton(
            frame_busqueda,
            text="🔍 Buscar CURP",
            font=("Segoe UI", 14, "bold"),
            fg_color="#3498db",
            hover_color="#2980b9",
            height=45,
            width=220,
            command=self.buscar_curp
        ).pack(pady=(10, 20))

        # Frame para resultados
        self.frame_resultado = ctk.CTkScrollableFrame(
            self.contenido,
            fg_color="white",
            corner_radius=15
        )
        self.frame_resultado.pack(fill="both", expand=True, padx=30, pady=(0, 20))

    def buscar_curp(self):
        for widget in self.frame_resultado.winfo_children():
            widget.destroy()

        curp = self.entry_curp.get().strip().upper()

        if not curp:
            messagebox.showwarning("⚠️ Aviso", "Por favor ingrese una CURP")
            return

        if len(curp) != 18:
            messagebox.showwarning("⚠️ Aviso", "La CURP debe tener 18 caracteres")
            return

        try:
            datos_curp = analizar_curp(curp)

            try:
                alumno = buscar_alumno_por_curp(curp)
            except Exception as e:
                messagebox.showerror("Error de conexión", f"No se pudo conectar a la base de datos:\n{str(e)}")
                return

            if not alumno:
                info_frame = ctk.CTkFrame(self.frame_resultado, fg_color="#fef3c7", corner_radius=10)
                info_frame.pack(fill="x", padx=20, pady=20)

                ctk.CTkLabel(
                    info_frame,
                    text="ℹ️ CURP no registrada en el sistema",
                    font=("Segoe UI", 18, "bold"),
                    text_color="#92400e"
                ).pack(pady=(15, 10))

                ctk.CTkLabel(
                    info_frame,
                    text="Puedes agregar este registro manualmente o importarlo desde Excel",
                    font=("Segoe UI", 13),
                    text_color="#92400e"
                ).pack(pady=(0, 15))

                ctk.CTkLabel(
                    info_frame,
                    text=f"📅 Fecha nacimiento: {datos_curp['fecha_nac']} | 👤 Sexo: {datos_curp['sexo']} | 📍 Entidad: {datos_curp['entidad_nacimiento']}",
                    font=("Segoe UI", 12),
                    text_color="#92400e"
                ).pack(pady=(0, 15))

                return

            self.alumno_actual = alumno
            self.crear_formulario_edicion_mejorado(alumno, datos_curp)

        except Exception as e:
            messagebox.showerror("❌ Error", str(e))

    def crear_formulario_edicion_mejorado(self, alumno, datos_curp):
        """Crea el formulario de edición mejorado con comboboxes"""
        
        # Info del alumno encontrado
        info_frame = ctk.CTkFrame(self.frame_resultado, fg_color="#d4edda", corner_radius=10)
        info_frame.pack(fill="x", padx=20, pady=(10, 20))

        ctk.CTkLabel(
            info_frame,
            text="✅ Registro encontrado - Editar información",
            font=("Segoe UI", 18, "bold"),
            text_color="#155724"
        ).pack(pady=(15, 10))

        ctk.CTkLabel(
            info_frame,
            text=f"📋 CURP: {alumno.get('curp', 'N/A')}",
            font=("Segoe UI", 13),
            text_color="#155724"
        ).pack(pady=5)

        ctk.CTkLabel(
            info_frame,
            text=f"📅 Fecha nacimiento: {datos_curp['fecha_nac']} | 👤 Sexo: {datos_curp['sexo']} | 📍 Entidad: {datos_curp['entidad_nacimiento']}",
            font=("Segoe UI", 12),
            text_color="#155724"
        ).pack(pady=(0, 15))

        # Formulario
        self.entries = {}
        self.comboboxes = {}
        
        frame_form = ctk.CTkFrame(self.frame_resultado, fg_color="transparent")
        frame_form.pack(fill="both", expand=True, padx=20, pady=10)

        # Configurar grid de 2 columnas para mejor organización
        frame_form.grid_columnconfigure(0, weight=1)
        frame_form.grid_columnconfigure(1, weight=1)

        campos = [
            ("p_apellido", "Primer Apellido", 0, 0, "entry"),
            ("s_apellido", "Segundo Apellido", 0, 1, "entry"),
            ("nombre", "Nombre(s)", 1, 0, "entry"),
            ("fecha_nac", "Fecha Nacimiento (YYYY-MM-DD)", 1, 1, "entry"),
            ("sexo", "Sexo", 2, 0, "entry"),
            ("entidad_nacimiento", "Entidad Nacimiento", 2, 1, "entry"),
            ("situacion", "Situación", 3, 0, "combobox", OPCIONES_SITUACION),
            ("causa_situacion", "Causa Situación", 3, 1, "entry"),
            ("tipo_periodo", "Tipo Periodo", 4, 0, "combobox", OPCIONES_TIPO_PERIODO),
            ("periodo", "Periodo", 4, 1, "combobox", OPCIONES_PERIODO),
            ("modalidad", "Modalidad", 5, 0, "combobox", OPCIONES_MODALIDAD),
        ]

        for campo_info in campos:
            campo = campo_info[0]
            label = campo_info[1]
            row = campo_info[2]
            col = campo_info[3]
            tipo = campo_info[4]
            
            frame_campo = ctk.CTkFrame(frame_form, fg_color="#f8f9fa", corner_radius=10)
            frame_campo.grid(row=row, column=col, padx=15, pady=10, sticky="nsew")

            ctk.CTkLabel(
                frame_campo,
                text=label,
                font=("Segoe UI", 13, "bold"),
                text_color="#1a2c3e"
            ).pack(anchor="w", padx=15, pady=(10, 5))

            valor = "" if alumno.get(campo) is None else str(alumno.get(campo))
            
            if tipo == "combobox":
                opciones = campo_info[5]
                combobox = ctk.CTkComboBox(
                    frame_campo,
                    values=opciones,
                    font=("Segoe UI", 12),
                    height=38,
                    state="readonly"
                )
                combobox.set(valor if valor in opciones else opciones[0])
                combobox.pack(fill="x", padx=15, pady=(0, 10))
                self.comboboxes[campo] = combobox
            else:
                entry = ctk.CTkEntry(frame_campo, height=38, font=("Segoe UI", 12))
                entry.insert(0, valor)
                entry.pack(fill="x", padx=15, pady=(0, 10))
                self.entries[campo] = entry

        # Botones
        btn_frame = ctk.CTkFrame(self.frame_resultado, fg_color="transparent")
        btn_frame.pack(pady=30)

        ctk.CTkButton(
            btn_frame,
            text="💾 Guardar cambios",
            font=("Segoe UI", 15, "bold"),
            fg_color="#2ecc71",
            hover_color="#27ae60",
            height=45,
            width=200,
            corner_radius=10,
            command=self.guardar_cambios_mejorado
        ).pack(side="left", padx=15)

        ctk.CTkButton(
            btn_frame,
            text="🗑️ Cancelar",
            font=("Segoe UI", 15, "bold"),
            fg_color="#e74c3c",
            hover_color="#c0392b",
            height=45,
            width=150,
            corner_radius=10,
            command=self.modulo_captura
        ).pack(side="left", padx=15)

    def guardar_cambios_mejorado(self):
        if not self.alumno_actual:
            messagebox.showwarning("⚠️ Aviso", "No hay alumno seleccionado")
            return

        datos = {}
        
        # Obtener valores de entries
        for campo, entry in self.entries.items():
            datos[campo] = entry.get().strip()
        
        # Obtener valores de comboboxes
        for campo, combobox in self.comboboxes.items():
            datos[campo] = combobox.get().strip()

        try:
            actualizar_alumno(self.alumno_actual["id"], datos)
            messagebox.showinfo("✅ Éxito", "Registro actualizado correctamente")
            self.modulo_registros()

        except Exception as e:
            messagebox.showerror("❌ Error", str(e))

    # =========================
    # EXPORTACIÓN
    # =========================

    def modulo_exportacion(self):
        self.limpiar_contenido()

        # Header
        header = self.crear_tarjeta(self.contenido, "📤 Módulo de Exportación", "Exporta los datos a Excel para reportes")
        header.pack(fill="x", padx=30, pady=(20, 10))

        try:
            datos = obtener_todos_los_alumnos()
        except Exception as e:
            messagebox.showerror("Error de conexión", f"No se pudo conectar a la base de datos:\n{str(e)}")
            return

        if not datos:
            ctk.CTkLabel(
                self.contenido,
                text="📭 No hay datos para exportar",
                font=("Segoe UI", 16),
                text_color="#6c7a8a"
            ).pack(expand=True)
            return

        # Barra de acciones
        action_frame = ctk.CTkFrame(self.contenido, fg_color="white", corner_radius=15)
        action_frame.pack(fill="x", padx=30, pady=(0, 15))

        ctk.CTkButton(
            action_frame,
            text="📥 Exportar a Excel",
            font=("Segoe UI", 14, "bold"),
            fg_color="#9b59b6",
            hover_color="#8e44ad",
            height=45,
            width=220,
            corner_radius=10,
            command=self.exportar_datos
        ).pack(pady=15)

        # Tabla de datos mejorada
        frame_tabla = ctk.CTkFrame(self.contenido, fg_color="white", corner_radius=15)
        frame_tabla.pack(fill="both", expand=True, padx=30, pady=(0, 20))

        self.mostrar_tabla_mejorada(frame_tabla, datos)

    def exportar_datos(self):
        try:
            datos = obtener_todos_los_alumnos()
        except Exception as e:
            messagebox.showerror("Error de conexión", f"No se pudo conectar a la base de datos:\n{str(e)}")
            return

        if not datos:
            messagebox.showwarning("⚠️ Aviso", "No hay datos para exportar")
            return

        ruta = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Archivo Excel", "*.xlsx"), ("Todos los archivos", "*.*")],
            title="Guardar archivo Excel"
        )

        if not ruta:
            return

        try:
            exportar_excel(datos, ruta)
            messagebox.showinfo("✅ Éxito", f"Archivo exportado correctamente:\n{os.path.basename(ruta)}")
        except Exception as e:
            messagebox.showerror("❌ Error", str(e))


# Importar tkinter para Canvas
import tkinter as tk

if __name__ == "__main__":
    app = SistemaBecas()
    app.mainloop()