import customtkinter as ctk
from tkinter import filedialog, messagebox
from threading import Thread
from src.excel_service import leer_excel
from src.database import importar_dataframe_a_mysql

class ModuloImportacion:
    def __init__(self, parent):
        self.parent = parent
        self.contenido = None
        
    def mostrar(self, contenido):
        self.contenido = contenido
        self.limpiar_contenido()
        self.crear_interfaz()
    
    def limpiar_contenido(self):
        for widget in self.contenido.winfo_children():
            widget.destroy()
    
    def crear_interfaz(self):
        main_frame = ctk.CTkFrame(self.contenido, fg_color="transparent")
        main_frame.pack(fill="both", expand=True)
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_rowconfigure(0, weight=1)
        
        center_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        center_frame.place(relx=0.5, rely=0.5, anchor="center")
        
        tarjeta = ctk.CTkFrame(center_frame, width=600, height=420, corner_radius=20, fg_color="white")
        tarjeta.pack()
        tarjeta.pack_propagate(False)
        
        ctk.CTkLabel(tarjeta, text="📂", font=("Segoe UI", 56)).pack(pady=(40, 10))
        ctk.CTkLabel(tarjeta, text="Módulo de Importación", font=("Segoe UI", 24, "bold")).pack(pady=10)
        ctk.CTkLabel(tarjeta, text="Importa tu archivo Excel con los datos de los becarios", font=("Segoe UI", 12)).pack()
        ctk.CTkLabel(tarjeta, text="El archivo debe contener una columna llamada 'CURP'", font=("Segoe UI", 11), text_color="#e74c3c").pack(pady=5)
        
        ctk.CTkButton(
            tarjeta, text="📎 Seleccionar archivo Excel",
            font=("Segoe UI", 14, "bold"), fg_color="#2ecc71",
            hover_color="#27ae60", height=45, width=280, corner_radius=10,
            command=self.importar_excel
        ).pack(pady=40)
    
    def importar_excel(self):
        ruta = filedialog.askopenfilename(
            filetypes=[("Archivos Excel", "*.xlsx"), ("Todos los archivos", "*.*")]
        )
        if not ruta:
            return

        def importar_thread():
            progreso_ventana = ctk.CTkToplevel(self.contenido)
            progreso_ventana.title("Importando...")
            progreso_ventana.geometry("300x100")
            progreso_ventana.transient(self.contenido)
            progreso_ventana.grab_set()
            
            ctk.CTkLabel(progreso_ventana, text="🔄 Procesando archivo...", font=("Segoe UI", 13)).pack(pady=20)
            progreso = ctk.CTkProgressBar(progreso_ventana, width=250)
            progreso.pack(pady=10)
            progreso.set(0.5)
            self.contenido.update()

            try:
                df = leer_excel(ruta)
                if "CURP" not in df.columns:
                    self.contenido.after(0, lambda: [progreso_ventana.destroy(), messagebox.showerror("Error", "El Excel debe tener una columna llamada 'CURP'")])
                    return

                resultado = importar_dataframe_a_mysql(df)
                total = resultado.get("guardados", 0)
                omitidos = resultado.get("omitidos", 0)
                
                self.contenido.after(0, lambda: progreso_ventana.destroy())
                self.contenido.after(0, lambda: messagebox.showinfo("✅ Importación exitosa", f"Registros guardados: {total}\nOmitidos: {omitidos}"))
                self.contenido.after(0, lambda: self.cambiar_modulo("registros"))

            except Exception as e:
                self.contenido.after(0, lambda: progreso_ventana.destroy())
                self.contenido.after(0, lambda: messagebox.showerror("❌ Error", str(e)))

        Thread(target=importar_thread, daemon=True).start()
    
    def cambiar_modulo(self, modulo):
        # Esto debe conectarse con el controlador principal
        pass