import customtkinter as ctk
from PIL import Image, ImageDraw
import os
from src.modulo_importacion import ModuloImportacion
from src.modulo_registros import ModuloRegistros
from src.modulo_captura import ModuloCaptura
from src.modulo_exportacion import ModuloExportacion
from src.config import APP_CONFIG, COLORES

class SistemaBecas(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title(APP_CONFIG["titulo"])
        
        # Pantalla completa maximizada
        self.state("zoomed")
        
        self.minsize(*APP_CONFIG["min_size"])
        
        self.modulos = {}
        self.modulo_actual = None
        self.contenido_principal = None
        
        self.crear_interfaz()
        self.cargar_modulos()
        self.mostrar_modulo("importacion")
    
    def crear_interfaz(self):
        # Frame principal
        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.pack(fill="both", expand=True)
        
        # ========== MENÚ LATERAL ==========
        menu_frame = ctk.CTkFrame(main_frame, width=280, corner_radius=0, fg_color="#0a2a3a")
        menu_frame.pack(side="left", fill="y")
        menu_frame.pack_propagate(False)
        
        # ========== LOGO CON FONDO BLANCO ==========
        logo_container = ctk.CTkFrame(menu_frame, fg_color="#ffffff", corner_radius=15)
        logo_container.pack(pady=(30, 15), padx=20, fill="x")
        
        # Cargar logo
        logo_path = self.buscar_logo()
        
        if logo_path and os.path.exists(logo_path):
            try:
                # Cargar imagen
                logo_image = Image.open(logo_path)
                
                # Crear fondo blanco si la imagen tiene transparencia
                if logo_image.mode in ('RGBA', 'LA'):
                    fondo = Image.new('RGB', logo_image.size, (255, 255, 255))
                    fondo.paste(logo_image, mask=logo_image.split()[-1] if logo_image.mode == 'RGBA' else None)
                    logo_image = fondo
                
                # Redimensionar manteniendo proporción
                logo_image.thumbnail((180, 120), Image.Resampling.LANCZOS)
                self.logo_ctk = ctk.CTkImage(light_image=logo_image, dark_image=logo_image, size=(logo_image.width, logo_image.height))
                
                logo_label = ctk.CTkLabel(logo_container, image=self.logo_ctk, text="")
                logo_label.pack(pady=(15, 10))
            except Exception as e:
                print(f"Error: {e}")
                self._crear_logo_texto(logo_container)
        else:
            self._crear_logo_texto(logo_container)
        
        # Título del sistema
        ctk.CTkLabel(
            logo_container, 
            text="Sistema de Becas", 
            font=("Segoe UI", 18, "bold"), 
            text_color="#0a2a3a"
        ).pack(anchor="center", pady=(5, 0))
        
        ctk.CTkLabel(
            logo_container, 
            text="Media Superior", 
            font=("Segoe UI", 13), 
            text_color="#555555"
        ).pack(anchor="center", pady=(2, 15))
        
        # Línea separadora
        separador = ctk.CTkFrame(menu_frame, height=2, fg_color="#1a4a5a")
        separador.pack(fill="x", padx=20, pady=10)
        
        # ========== BOTONES DEL MENÚ ==========
        botones = [
            ("📥 Importación", "importacion", COLORES["btn_importar"]),
            ("📋 Registros", "registros", COLORES["btn_registros"]),
            ("✏️ Captura CURP", "captura", COLORES["btn_captura"]),
            ("📤 Exportación", "exportacion", COLORES["btn_exportar"]),
        ]
        
        for texto, modulo, color in botones:
            btn = ctk.CTkButton(
                menu_frame, 
                text=texto, 
                font=("Segoe UI", 14, "bold"),
                fg_color=color, 
                hover_color=self._darken_color(color),
                height=45, 
                corner_radius=10,
                anchor="center",
                command=lambda m=modulo: self.mostrar_modulo(m)
            )
            btn.pack(fill="x", padx=20, pady=8)
        
        # Espaciador
        spacer = ctk.CTkFrame(menu_frame, fg_color="transparent", height=40)
        spacer.pack(expand=True)
        
        # ========== FOOTER DEL MENÚ ==========
        from datetime import datetime
        fecha_actual = datetime.now().strftime("%d/%m/%Y")
        
        footer_frame = ctk.CTkFrame(menu_frame, fg_color="#0a2a3a", corner_radius=10)
        footer_frame.pack(side="bottom", fill="x", pady=(0, 20), padx=15)
        
        ctk.CTkLabel(
            footer_frame, 
            text=f"📅 {fecha_actual}", 
            font=("Segoe UI", 12), 
            text_color="#a0c4e8"
        ).pack(pady=(10, 5))
        
        ctk.CTkLabel(
            footer_frame, 
            text="Sistema de Becas", 
            font=("Segoe UI", 12, "bold"), 
            text_color="#ffffff"
        ).pack(pady=3)
        
        ctk.CTkLabel(
            footer_frame, 
            text="Media Superior 2026", 
            font=("Segoe UI", 11), 
            text_color="#a0c4e8"
        ).pack(pady=(0, 10))
        
        # ========== CONTENIDO PRINCIPAL ==========
        self.contenido_principal = ctk.CTkFrame(main_frame, corner_radius=0, fg_color="#f0f2f5")
        self.contenido_principal.pack(side="right", fill="both", expand=True)
    
    def _crear_logo_texto(self, parent):
        """Crea un logo de texto alternativo"""
        texto_frame = ctk.CTkFrame(parent, fg_color="#0a2a3a", corner_radius=10)
        texto_frame.pack(pady=(15, 10), padx=15, fill="x")
        
        ctk.CTkLabel(
            texto_frame, 
            text="COLEGIO DE\nBACHILLERES", 
            font=("Segoe UI", 14, "bold"), 
            text_color="white"
        ).pack(pady=10)
        
        ctk.CTkLabel(
            texto_frame, 
            text="DE CHIAPAS", 
            font=("Segoe UI", 12), 
            text_color="#a0c4e8"
        ).pack(pady=(0, 10))
    
    def buscar_logo(self):
        """Busca el archivo logo.png en diferentes ubicaciones"""
        posibles_ubicaciones = [
            "logo.png",
            "src/logo.png",
            "../logo.png",
            os.path.join(os.path.dirname(__file__), "logo.png"),
            os.path.join(os.path.dirname(__file__), "src", "logo.png"),
        ]
        
        for ubicacion in posibles_ubicaciones:
            if os.path.exists(ubicacion):
                return ubicacion
        return None
    
    def _darken_color(self, color):
        """Oscurece un color hexadecimal"""
        if color.startswith("#"):
            r = int(color[1:3], 16)
            g = int(color[3:5], 16)
            b = int(color[5:7], 16)
            return f"#{max(0, r-40):02x}{max(0, g-40):02x}{max(0, b-40):02x}"
        return "#1a5276"
    
    def cargar_modulos(self):
        self.modulos["importacion"] = ModuloImportacion(self)
        self.modulos["registros"] = ModuloRegistros(self)
        self.modulos["captura"] = ModuloCaptura(self)
        self.modulos["exportacion"] = ModuloExportacion(self)
    
    def mostrar_modulo(self, nombre):
        if nombre in self.modulos and self.contenido_principal:
            for widget in self.contenido_principal.winfo_children():
                widget.destroy()
            self.modulos[nombre].mostrar(self.contenido_principal)


if __name__ == "__main__":
    ctk.set_appearance_mode("light")
    ctk.set_default_color_theme("blue")
    app = SistemaBecas()
    app.mainloop()