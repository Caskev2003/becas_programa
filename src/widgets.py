import customtkinter as ctk
from src.config import COLORES

class MenuLateral(ctk.CTkFrame):
    def __init__(self, parent, comandos):
        super().__init__(parent, width=260, corner_radius=0, fg_color=COLORES["menu_bg"])
        # No hacer pack aquí, se hará desde app.py
        self.propagate(False)
        
        # Título
        ctk.CTkLabel(
            self, text="🎓 Sistema Becas \nMedia Superior",
            font=("Segoe UI", 18, "bold"), text_color="white"
        ).pack(pady=(40, 20), padx=20)
        
        ctk.CTkFrame(self, height=2, fg_color=COLORES["menu_hover"]).pack(fill="x", padx=20, pady=10)
        
        # Botones
        for texto, comando, color in comandos:
            btn = ctk.CTkButton(
                self, text=texto, font=("Segoe UI", 13, "bold"),
                fg_color=color, hover_color=self._darken_color(color),
                height=40, corner_radius=8, command=comando
            )
            btn.pack(fill="x", padx=20, pady=6)
        
        ctk.CTkFrame(self, height=2, fg_color=COLORES["menu_hover"]).pack(fill="x", padx=20, pady=20)
        
        ctk.CTkLabel(
            self, text="Sistema Becas Media Superior",
            font=("Segoe UI", 10), text_color="#7f8c8d"
        ).pack(side="bottom", pady=20)
    
    def _darken_color(self, color):
        if color.startswith("#"):
            r = int(color[1:3], 16)
            g = int(color[3:5], 16)
            b = int(color[5:7], 16)
            return f"#{max(0, r-40):02x}{max(0, g-40):02x}{max(0, b-40):02x}"
        return "#1a5276"


class TarjetaInfo(ctk.CTkFrame):
    def __init__(self, parent, titulo, subtitulo=""):
        super().__init__(parent, corner_radius=15, fg_color="white")
        self.pack(fill="x", padx=30, pady=(10, 5))
        
        ctk.CTkLabel(
            self, text=titulo, font=("Segoe UI", 20, "bold")
        ).pack(anchor="w", padx=20, pady=(15, 5))
        
        if subtitulo:
            ctk.CTkLabel(
                self, text=subtitulo, font=("Segoe UI", 12), text_color="#6c7a8a"
            ).pack(anchor="w", padx=20, pady=(0, 15))


class CampoFormulario(ctk.CTkFrame):
    def __init__(self, parent, label, valor="", tipo="entry", opciones=None):
        super().__init__(parent, fg_color="#f8f9fa", corner_radius=8)
        
        ctk.CTkLabel(self, text=label, font=("Segoe UI", 12, "bold")).pack(anchor="w", padx=12, pady=(8, 3))
        
        if tipo == "combobox" and opciones:
            self.widget = ctk.CTkComboBox(self, values=opciones, font=("Segoe UI", 11), height=35, state="readonly")
            self.widget.set(valor if valor in opciones else opciones[0])
        else:
            self.widget = ctk.CTkEntry(self, height=35, font=("Segoe UI", 11))
            self.widget.insert(0, valor)
        
        self.widget.pack(fill="x", padx=12, pady=(0, 8))
    
    def get_value(self):
        return self.widget.get().strip()
    
    def set_value(self, valor):
        self.widget.delete(0, "end")
        self.widget.insert(0, valor)


class BotonAccion(ctk.CTkButton):
    def __init__(self, parent, texto, comando, color, ancho=160):
        super().__init__(
            parent, text=texto, font=("Segoe UI", 13, "bold"),
            fg_color=color, hover_color=self._darken_color(color),
            height=40, width=ancho, corner_radius=10, command=comando
        )
    
    def _darken_color(self, color):
        if color.startswith("#"):
            r = int(color[1:3], 16)
            g = int(color[3:5], 16)
            b = int(color[5:7], 16)
            return f"#{max(0, r-40):02x}{max(0, g-40):02x}{max(0, b-40):02x}"
        return "#1a5276"