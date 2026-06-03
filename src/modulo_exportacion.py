import customtkinter as ctk
from tkinter import filedialog, messagebox, ttk
from threading import Thread
import os
from src.database import obtener_todos_los_alumnos, contar_alumnos, obtener_alumnos_paginados
from src.excel_service import exportar_excel
from src.config import COLORES, PAGINACION

class ModuloExportacion:
    def __init__(self, parent):
        self.parent = parent
        self.contenido = None
        self.registros_por_pagina = PAGINACION["registros_por_pagina"]
        self.pagina_actual = 1
        self.total_paginas = 1
        self.tabla = None
        self.frame_tabla = None
        self.pag_frame = None
        
    def mostrar(self, contenido):
        self.contenido = contenido
        self.limpiar_contenido()
        self.pagina_actual = 1
        self.crear_interfaz()
    
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
    
    def crear_interfaz(self):
        header = ctk.CTkFrame(self.contenido, corner_radius=15, fg_color="white")
        header.pack(fill="x", padx=30, pady=(20, 10))
        
        ctk.CTkLabel(header, text="📤 Módulo de Exportación", font=("Segoe UI", 20, "bold")).pack(anchor="w", padx=20, pady=(15, 5))
        ctk.CTkLabel(header, text="Exporta los datos a Excel para reportes", font=("Segoe UI", 12)).pack(anchor="w", padx=20, pady=(0, 15))
        
        action_frame = ctk.CTkFrame(self.contenido, fg_color="white", corner_radius=15)
        action_frame.pack(fill="x", padx=30, pady=(0, 15))
        
        ctk.CTkButton(action_frame, text="📥 Exportar a Excel", font=("Segoe UI", 13, "bold"),
                     fg_color=COLORES["btn_exportar"], hover_color="#8e44ad", height=40, width=200,
                     command=self.exportar_datos).pack(pady=15)
        
        self.crear_tabla()
    
    def crear_tabla(self):
        # Eliminar frame anterior si existe
        if self.frame_tabla:
            self.frame_tabla.destroy()
        
        self.frame_tabla = ctk.CTkFrame(self.contenido, fg_color="white", corner_radius=15)
        self.frame_tabla.pack(fill="both", expand=True, padx=30, pady=(0, 20))
        
        try:
            total_registros = contar_alumnos()
            self.total_paginas = max(1, (total_registros + self.registros_por_pagina - 1) // self.registros_por_pagina)
            
            if self.pagina_actual > self.total_paginas:
                self.pagina_actual = self.total_paginas
            if self.pagina_actual < 1:
                self.pagina_actual = 1
            
            offset = (self.pagina_actual - 1) * self.registros_por_pagina
            datos = obtener_alumnos_paginados(offset, self.registros_por_pagina)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo conectar:\n{str(e)}")
            return
        
        if not datos:
            ctk.CTkLabel(self.frame_tabla, text="📭 No hay datos para exportar", font=("Segoe UI", 14)).pack(expand=True)
            return
        
        self.mostrar_tabla_previa(self.frame_tabla, datos, total_registros)
    
    def mostrar_tabla_previa(self, parent, datos, total_registros):
        # Configurar estilo
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Preview.Treeview.Heading", background=COLORES["tabla_header"], foreground="white", font=("Segoe UI", 11, "bold"))
        style.configure("Preview.Treeview", font=("Segoe UI", 10), rowheight=30)
        
        # Scrollbars
        container = ctk.CTkFrame(parent, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=5, pady=5)
        
        scroll_y = ttk.Scrollbar(container, orient="vertical")
        scroll_x = ttk.Scrollbar(container, orient="horizontal")
        
        self.tabla = ttk.Treeview(container, yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set,
                                   selectmode="browse", height=20, style="Preview.Treeview")
        
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
            self.tabla.insert("", "end", values=[
                fila.get("id"), fila.get("curp"), fila.get("p_apellido"), fila.get("s_apellido"),
                fila.get("nombre"), self.formatear_fecha(fila.get("fecha_nac")), fila.get("sexo"),
                fila.get("entidad_nacimiento"), fila.get("situacion"), fila.get("causa_situacion") or "-",
                fila.get("tipo_periodo"), fila.get("periodo"), fila.get("modalidad")
            ])
        
        self.crear_paginacion(parent, total_registros)
    
    def crear_paginacion(self, parent, total_registros):
        if self.pag_frame:
            self.pag_frame.destroy()
        
        self.pag_frame = ctk.CTkFrame(parent, fg_color="transparent")
        self.pag_frame.pack(fill="x", pady=10)
        
        inicio = (self.pagina_actual - 1) * self.registros_por_pagina + 1
        fin = min(self.pagina_actual * self.registros_por_pagina, total_registros)
        
        ctk.CTkLabel(self.pag_frame, text=f"📊 Mostrando {inicio} - {fin} de {total_registros} registros",
                    font=("Segoe UI", 11), text_color="#1a2c3e").pack(side="left", padx=15)
        
        btn_frame = ctk.CTkFrame(self.pag_frame, fg_color="transparent")
        btn_frame.pack(side="right")
        
        btn_anterior = ctk.CTkButton(btn_frame, text="◀ Anterior", width=90, height=30,
                                     font=("Segoe UI", 11), fg_color="#3498db",
                                     command=self.pagina_anterior)
        btn_anterior.pack(side="left", padx=3)
        
        if self.pagina_actual <= 1:
            btn_anterior.configure(state="disabled", fg_color="#95a5a6")
        
        ctk.CTkLabel(btn_frame, text=f"Página {self.pagina_actual} de {self.total_paginas}",
                    font=("Segoe UI", 11, "bold")).pack(side="left", padx=10)
        
        btn_siguiente = ctk.CTkButton(btn_frame, text="Siguiente ▶", width=90, height=30,
                                      font=("Segoe UI", 11), fg_color="#3498db",
                                      command=self.pagina_siguiente)
        btn_siguiente.pack(side="left", padx=3)
        
        if self.pagina_actual >= self.total_paginas:
            btn_siguiente.configure(state="disabled", fg_color="#95a5a6")
    
    def pagina_anterior(self):
        if self.pagina_actual > 1:
            self.pagina_actual -= 1
            self.crear_tabla()
    
    def pagina_siguiente(self):
        if self.pagina_actual < self.total_paginas:
            self.pagina_actual += 1
            self.crear_tabla()
    
    def exportar_datos(self):
        ruta = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Archivo Excel", "*.xlsx")])
        if not ruta:
            return
        
        def exportar_thread():
            progreso = ctk.CTkToplevel(self.contenido)
            progreso.title("Exportando...")
            progreso.geometry("250x80")
            progreso.transient(self.contenido)
            ctk.CTkLabel(progreso, text="🔄 Exportando datos...", font=("Segoe UI", 12)).pack(pady=20)
            self.contenido.update()
            
            try:
                datos = obtener_todos_los_alumnos()
                exportar_excel(datos, ruta)
                self.contenido.after(0, lambda: progreso.destroy())
                self.contenido.after(0, lambda: messagebox.showinfo("✅ Éxito", f"Archivo exportado: {os.path.basename(ruta)}"))
            except Exception as e:
                self.contenido.after(0, lambda: progreso.destroy())
                self.contenido.after(0, lambda: messagebox.showerror("❌ Error", str(e)))
        
        Thread(target=exportar_thread, daemon=True).start()