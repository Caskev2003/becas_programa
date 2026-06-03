import customtkinter as ctk
from tkinter import ttk, messagebox
from src.database import obtener_alumnos_paginados, contar_alumnos
from src.config import COLORES, PAGINACION

class ModuloRegistros:
    def __init__(self, parent):
        self.parent = parent
        self.contenido = None
        self.tabla = None
        self.pagina_actual = 1
        self.total_paginas = 1
        self.registros_por_pagina = 20  # Número fijo
        self.datos_completos = []  # Almacenar todos los datos para paginación manual
        
    def mostrar(self, contenido):
        self.contenido = contenido
        self.limpiar_contenido()
        self.pagina_actual = 1
        self.cargar_datos()
    
    def limpiar_contenido(self):
        for widget in self.contenido.winfo_children():
            widget.destroy()
    
    def formatear_fecha(self, fecha):
        if not fecha:
            return ""
        try:
            if isinstance(fecha, str) and "-" in fecha:
                partes = fecha.split("-")
                if len(partes) == 3:
                    return f"{partes[2]}/{partes[1]}/{partes[0]}"
            return str(fecha)
        except:
            return str(fecha)
    
    def cargar_datos(self):
        # Header
        header = ctk.CTkFrame(self.contenido, corner_radius=15, fg_color="white")
        header.pack(fill="x", padx=30, pady=(20, 15))
        
        ctk.CTkLabel(header, text="📋 Registros Guardados", font=("Segoe UI", 22, "bold")).pack(anchor="w", padx=20, pady=(15, 5))
        ctk.CTkLabel(header, text="Consulta y gestión de beneficiarios", font=("Segoe UI", 13)).pack(anchor="w", padx=20, pady=(0, 15))
        
        # Frame de la tabla
        self.frame_tabla = ctk.CTkFrame(self.contenido, fg_color="white", corner_radius=15)
        self.frame_tabla.pack(fill="both", expand=True, padx=30, pady=(0, 15))
        
        try:
            # Obtener todos los datos
            from src.database import obtener_todos_los_alumnos
            self.datos_completos = obtener_todos_los_alumnos()
            total_registros = len(self.datos_completos)
            self.total_paginas = max(1, (total_registros + self.registros_por_pagina - 1) // self.registros_por_pagina)
            
            # Validar página
            if self.pagina_actual > self.total_paginas:
                self.pagina_actual = self.total_paginas
            if self.pagina_actual < 1:
                self.pagina_actual = 1
            
            # Obtener datos de la página actual
            inicio = (self.pagina_actual - 1) * self.registros_por_pagina
            fin = inicio + self.registros_por_pagina
            datos_pagina = self.datos_completos[inicio:fin]
            
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo conectar a la base de datos:\n{str(e)}")
            return
        
        if not datos_pagina:
            ctk.CTkLabel(self.frame_tabla, text="📭 No hay registros guardados", font=("Segoe UI", 16)).pack(expand=True)
            return
        
        # Mostrar tabla
        self.mostrar_tabla(self.frame_tabla, datos_pagina)
        
        # Mostrar paginación
        self.mostrar_paginacion(self.contenido, total_registros)
    
    def mostrar_tabla(self, parent, datos):
        # Configurar estilo
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Custom.Treeview.Heading", background="#1a2c3e", foreground="white", font=("Segoe UI", 11, "bold"))
        style.configure("Custom.Treeview", font=("Segoe UI", 10), rowheight=30)
        style.map("Custom.Treeview", background=[("selected", "#3498db")])
        
        # Frame con scroll
        container = ctk.CTkFrame(parent, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=5, pady=5)
        
        scroll_y = ttk.Scrollbar(container, orient="vertical")
        scroll_x = ttk.Scrollbar(container, orient="horizontal")
        
        self.tabla = ttk.Treeview(
            container, yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set,
            selectmode="browse", height=22, style="Custom.Treeview"
        )
        
        scroll_y.config(command=self.tabla.yview)
        scroll_x.config(command=self.tabla.xview)
        
        scroll_y.pack(side="right", fill="y")
        scroll_x.pack(side="bottom", fill="x")
        self.tabla.pack(fill="both", expand=True)
        
        # Columnas
        columnas = [
            ("ID", 50), ("CURP", 160), ("P. APELLIDO", 120), ("S. APELLIDO", 120),
            ("NOMBRE", 150), ("FECHA NAC", 100), ("SEXO", 50), ("ENTIDAD", 100),
            ("SITUACIÓN", 130), ("CAUSA", 130), ("TIPO PERIODO", 110), ("PERIODO", 70), ("MODALIDAD", 120)
        ]
        
        self.tabla["columns"] = [c[0] for c in columnas]
        self.tabla["show"] = "headings"
        
        for col, ancho in columnas:
            self.tabla.heading(col, text=col)
            self.tabla.column(col, width=ancho, anchor="center")
        
        # Insertar datos
        for i, fila in enumerate(datos):
            valores = [
                fila.get("id", ""),
                fila.get("curp", ""),
                fila.get("p_apellido", ""),
                fila.get("s_apellido", ""),
                fila.get("nombre", ""),
                self.formatear_fecha(fila.get("fecha_nac", "")),
                fila.get("sexo", ""),
                fila.get("entidad_nacimiento", ""),
                fila.get("situacion", ""),
                (fila.get("causa_situacion", "") or "-")[:35],
                fila.get("tipo_periodo", ""),
                fila.get("periodo", ""),
                fila.get("modalidad", "")
            ]
            # Color de fila alternado
            if i % 2 == 0:
                self.tabla.insert("", "end", values=valores, tags=("even",))
            else:
                self.tabla.insert("", "end", values=valores, tags=("odd",))
        
        self.tabla.tag_configure("even", background="white")
        self.tabla.tag_configure("odd", background="#f8f9fa")
    
    def mostrar_paginacion(self, parent, total_registros):
        """Muestra los botones de paginación"""
        # Frame para paginación
        pag_frame = ctk.CTkFrame(parent, fg_color="transparent")
        pag_frame.pack(fill="x", padx=30, pady=(0, 20))
        
        inicio = (self.pagina_actual - 1) * self.registros_por_pagina + 1
        fin = min(self.pagina_actual * self.registros_por_pagina, total_registros)
        
        # Información de registros
        info_label = ctk.CTkLabel(
            pag_frame, 
            text=f"📊 Mostrando {inicio} - {fin} de {total_registros} registros",
            font=("Segoe UI", 12, "bold"), 
            text_color="#1a2c3e"
        )
        info_label.pack(side="left", padx=10)
        
        # Frame para botones
        btn_container = ctk.CTkFrame(pag_frame, fg_color="transparent")
        btn_container.pack(side="right")
        
        # Botón Anterior
        self.btn_anterior = ctk.CTkButton(
            btn_container, 
            text="◀ Anterior", 
            width=100, 
            height=35,
            font=("Segoe UI", 12, "bold"), 
            fg_color="#3498db",
            command=self.pagina_anterior
        )
        self.btn_anterior.pack(side="left", padx=5)
        
        # Label de página actual
        self.lbl_pagina = ctk.CTkLabel(
            btn_container, 
            text=f"Página {self.pagina_actual} de {self.total_paginas}",
            font=("Segoe UI", 12, "bold"), 
            text_color="#1a2c3e"
        )
        self.lbl_pagina.pack(side="left", padx=15)
        
        # Botón Siguiente
        self.btn_siguiente = ctk.CTkButton(
            btn_container, 
            text="Siguiente ▶", 
            width=100, 
            height=35,
            font=("Segoe UI", 12, "bold"), 
            fg_color="#3498db",
            command=self.pagina_siguiente
        )
        self.btn_siguiente.pack(side="left", padx=5)
        
        # Deshabilitar botones si es necesario
        self.actualizar_botones()
    
    def actualizar_botones(self):
        """Habilita/deshabilita botones según la página actual"""
        if self.pagina_actual <= 1:
            self.btn_anterior.configure(state="disabled", fg_color="#95a5a6")
        else:
            self.btn_anterior.configure(state="normal", fg_color="#3498db")
        
        if self.pagina_actual >= self.total_paginas:
            self.btn_siguiente.configure(state="disabled", fg_color="#95a5a6")
        else:
            self.btn_siguiente.configure(state="normal", fg_color="#3498db")
        
        # Actualizar texto de página
        self.lbl_pagina.configure(text=f"Página {self.pagina_actual} de {self.total_paginas}")
    
    def pagina_anterior(self):
        if self.pagina_actual > 1:
            self.pagina_actual -= 1
            self.recargar_pagina()
    
    def pagina_siguiente(self):
        if self.pagina_actual < self.total_paginas:
            self.pagina_actual += 1
            self.recargar_pagina()
    
    def recargar_pagina(self):
        """Recarga solo los datos de la tabla sin recrear toda la interfaz"""
        inicio = (self.pagina_actual - 1) * self.registros_por_pagina
        fin = inicio + self.registros_por_pagina
        datos_pagina = self.datos_completos[inicio:fin]
        
        # Limpiar tabla
        for item in self.tabla.get_children():
            self.tabla.delete(item)
        
        # Insertar nuevos datos
        for i, fila in enumerate(datos_pagina):
            valores = [
                fila.get("id", ""),
                fila.get("curp", ""),
                fila.get("p_apellido", ""),
                fila.get("s_apellido", ""),
                fila.get("nombre", ""),
                self.formatear_fecha(fila.get("fecha_nac", "")),
                fila.get("sexo", ""),
                fila.get("entidad_nacimiento", ""),
                fila.get("situacion", ""),
                (fila.get("causa_situacion", "") or "-")[:35],
                fila.get("tipo_periodo", ""),
                fila.get("periodo", ""),
                fila.get("modalidad", "")
            ]
            if i % 2 == 0:
                self.tabla.insert("", "end", values=valores, tags=("even",))
            else:
                self.tabla.insert("", "end", values=valores, tags=("odd",))
        
        # Actualizar info de página
        total_registros = len(self.datos_completos)
        inicio = (self.pagina_actual - 1) * self.registros_por_pagina + 1
        fin = min(self.pagina_actual * self.registros_por_pagina, total_registros)
        
        # Actualizar el texto de información
        for widget in self.contenido.winfo_children():
            if isinstance(widget, ctk.CTkFrame):
                for child in widget.winfo_children():
                    if isinstance(child, ctk.CTkLabel) and "Mostrando" in child.cget("text"):
                        child.configure(text=f"📊 Mostrando {inicio} - {fin} de {total_registros} registros")
                        break
        
        self.actualizar_botones()