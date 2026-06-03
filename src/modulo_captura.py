import customtkinter as ctk
from tkinter import messagebox
from src.curp_utils import analizar_curp
from src.database import buscar_alumno_por_curp, actualizar_alumno
from src.config import COLORES, OPCIONES_SITUACION, OPCIONES_MODALIDAD, OPCIONES_PERIODO, OPCIONES_TIPO_PERIODO

class ModuloCaptura:
    def __init__(self, parent):
        self.parent = parent
        self.contenido = None
        self.alumno_actual = None
        self.entries = {}
        self.comboboxes = {}
        
    def mostrar(self, contenido):
        self.contenido = contenido
        self.limpiar_contenido()
        self.alumno_actual = None
        self.entries = {}
        self.comboboxes = {}
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
    
    def desformatear_fecha(self, fecha):
        if not fecha:
            return ""
        try:
            if isinstance(fecha, str) and "/" in fecha:
                partes = fecha.split("/")
                if len(partes) == 3:
                    return f"{partes[2]}-{partes[1]}-{partes[0]}"
            return fecha
        except:
            return fecha
    
    def crear_interfaz(self):
        header = ctk.CTkFrame(self.contenido, corner_radius=15, fg_color="white")
        header.pack(fill="x", padx=30, pady=(20, 10))
        
        ctk.CTkLabel(header, text="✏️ Captura por CURP", font=("Segoe UI", 20, "bold")).pack(anchor="w", padx=20, pady=(15, 5))
        ctk.CTkLabel(header, text="Buscar, editar y actualizar beneficiarios", font=("Segoe UI", 12)).pack(anchor="w", padx=20, pady=(0, 15))
        
        frame_busqueda = ctk.CTkFrame(self.contenido, fg_color="white", corner_radius=15)
        frame_busqueda.pack(fill="x", padx=30, pady=(0, 15))
        
        ctk.CTkLabel(frame_busqueda, text="🔍 CURP del beneficiario:", font=("Segoe UI", 14, "bold")).pack(pady=(20, 5))
        
        self.entry_curp = ctk.CTkEntry(frame_busqueda, width=500, height=40, font=("Segoe UI", 13),
                                       placeholder_text="Ingrese la CURP a buscar (18 caracteres)")
        self.entry_curp.pack(pady=5)
        
        ctk.CTkButton(frame_busqueda, text="🔍 Buscar CURP", font=("Segoe UI", 13, "bold"),
                     fg_color=COLORES["btn_buscar"], height=40, width=200,
                     command=self.buscar_curp).pack(pady=(10, 20))
        
        self.frame_resultado = ctk.CTkScrollableFrame(self.contenido, fg_color="white", corner_radius=15)
        self.frame_resultado.pack(fill="both", expand=True, padx=30, pady=(0, 20))
    
    def buscar_curp(self):
        for widget in self.frame_resultado.winfo_children():
            widget.destroy()
        
        curp = self.entry_curp.get().strip().upper()
        
        if not curp:
            messagebox.showwarning("⚠️ Aviso", "Ingrese una CURP")
            return
        if len(curp) != 18:
            messagebox.showwarning("⚠️ Aviso", "La CURP debe tener 18 caracteres")
            return
        
        try:
            datos_curp = analizar_curp(curp)
            alumno = buscar_alumno_por_curp(curp)
            
            if not alumno:
                info_frame = ctk.CTkFrame(self.frame_resultado, fg_color="#fef3c7", corner_radius=10)
                info_frame.pack(fill="x", padx=20, pady=20)
                ctk.CTkLabel(info_frame, text="ℹ️ CURP no registrada", font=("Segoe UI", 16, "bold"), text_color="#92400e").pack(pady=15)
                ctk.CTkLabel(info_frame, text=f"📅 {datos_curp['fecha_nac']} | 👤 {datos_curp['sexo']} | 📍 {datos_curp['entidad_nacimiento']}",
                            font=("Segoe UI", 12)).pack(pady=(0, 15))
                return
            
            self.alumno_actual = alumno
            self.crear_formulario_edicion(alumno, datos_curp)
            
        except Exception as e:
            messagebox.showerror("❌ Error", str(e))
    
    def crear_formulario_edicion(self, alumno, datos_curp):
        info_frame = ctk.CTkFrame(self.frame_resultado, fg_color="#d4edda", corner_radius=10)
        info_frame.pack(fill="x", padx=20, pady=(10, 20))
        
        ctk.CTkLabel(info_frame, text="✅ Registro encontrado", font=("Segoe UI", 16, "bold"), text_color="#155724").pack(pady=(15, 5))
        ctk.CTkLabel(info_frame, text=f"CURP: {alumno.get('curp', 'N/A')}", font=("Segoe UI", 12)).pack(pady=5)
        
        fecha_nac = alumno.get('fecha_nac', '')
        fecha_mostrar = self.formatear_fecha(fecha_nac) if fecha_nac else ''
        ctk.CTkLabel(info_frame, text=f"📅 {fecha_mostrar} | 👤 {datos_curp['sexo']} | 📍 {datos_curp['entidad_nacimiento']}",
                    font=("Segoe UI", 11)).pack(pady=(0, 15))
        
        frame_form = ctk.CTkFrame(self.frame_resultado, fg_color="transparent")
        frame_form.pack(fill="both", expand=True, padx=20, pady=10)
        frame_form.grid_columnconfigure(0, weight=1)
        frame_form.grid_columnconfigure(1, weight=1)
        
        campos = [
            ("p_apellido", "Primer Apellido", 0, 0, "entry"),
            ("s_apellido", "Segundo Apellido", 0, 1, "entry"),
            ("nombre", "Nombre(s)", 1, 0, "entry"),
            ("fecha_nac", "Fecha Nacimiento (DD/MM/YYYY)", 1, 1, "entry"),
            ("sexo", "Sexo", 2, 0, "entry"),
            ("entidad_nacimiento", "Entidad Nacimiento", 2, 1, "entry"),
            ("situacion", "Situación", 3, 0, "combobox", OPCIONES_SITUACION),
            ("causa_situacion", "Causa Situación", 3, 1, "entry"),
            ("tipo_periodo", "Tipo Periodo", 4, 0, "combobox", OPCIONES_TIPO_PERIODO),
            ("periodo", "Periodo", 4, 1, "combobox", OPCIONES_PERIODO),
            ("modalidad", "Modalidad", 5, 0, "combobox", OPCIONES_MODALIDAD),
        ]
        
        for campo in campos:
            frame_campo = ctk.CTkFrame(frame_form, fg_color="#f8f9fa", corner_radius=8)
            frame_campo.grid(row=campo[2], column=campo[3], padx=10, pady=6, sticky="nsew")
            
            ctk.CTkLabel(frame_campo, text=campo[1], font=("Segoe UI", 12, "bold")).pack(anchor="w", padx=12, pady=(8, 3))
            
            valor_raw = alumno.get(campo[0])
            if campo[0] == "fecha_nac" and valor_raw:
                valor = self.formatear_fecha(str(valor_raw))
            else:
                valor = "" if valor_raw is None else str(valor_raw)
            
            if campo[4] == "combobox":
                opciones = campo[5]
                cb = ctk.CTkComboBox(frame_campo, values=opciones, font=("Segoe UI", 11), height=35, state="readonly")
                cb.set(valor if valor in opciones else opciones[0])
                cb.pack(fill="x", padx=12, pady=(0, 8))
                self.comboboxes[campo[0]] = cb
            else:
                entry = ctk.CTkEntry(frame_campo, height=35, font=("Segoe UI", 11))
                entry.insert(0, valor)
                entry.pack(fill="x", padx=12, pady=(0, 8))
                self.entries[campo[0]] = entry
        
        btn_frame = ctk.CTkFrame(self.frame_resultado, fg_color="transparent")
        btn_frame.pack(pady=20)
        
        ctk.CTkButton(btn_frame, text="💾 Guardar cambios", font=("Segoe UI", 13, "bold"),
                     fg_color=COLORES["btn_guardar"], hover_color="#27ae60", height=40, width=180,
                     command=self.guardar_cambios).pack(side="left", padx=10)
        
        ctk.CTkButton(btn_frame, text="🗑️ Cancelar", font=("Segoe UI", 13, "bold"),
                     fg_color=COLORES["btn_cancelar"], hover_color="#c0392b", height=40, width=120,
                     command=lambda: self.mostrar(self.contenido)).pack(side="left", padx=10)
    
    def guardar_cambios(self):
        if not self.alumno_actual:
            messagebox.showwarning("⚠️ Aviso", "No hay alumno seleccionado")
            return
        
        datos = {}
        for campo, entry in self.entries.items():
            valor = entry.get().strip()
            if campo == "fecha_nac" and valor:
                valor = self.desformatear_fecha(valor)
            datos[campo] = valor
        
        for campo, cb in self.comboboxes.items():
            datos[campo] = cb.get().strip()
        
        try:
            actualizar_alumno(self.alumno_actual["id"], datos)
            messagebox.showinfo("✅ Éxito", "Registro actualizado correctamente")
            self.cambiar_modulo("registros")
        except Exception as e:
            messagebox.showerror("❌ Error", str(e))
    
    def cambiar_modulo(self, modulo):
        pass