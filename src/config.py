import customtkinter as ctk

# Configuración de la app
APP_CONFIG = {
    "titulo": "Sistema de Becas - Administración",
    "geometria": "1400x800",
    "min_size": (1200, 600),
    "modo": "light",
    "tema": "blue"
}

# Colores del sistema
COLORES = {
    "menu_bg": "#0a2a3a",
    "menu_hover": "#1a4a5a",
    "header_bg": "white",
    "tabla_header": "#0a2a3a",
    "tabla_fila_par": "#f8f9fa",
    "tabla_fila_impar": "white",
    "btn_importar": "#27ae60",
    "btn_registros": "#2980b9",
    "btn_captura": "#e67e22",
    "btn_exportar": "#8e44ad",
    "btn_guardar": "#27ae60",
    "btn_cancelar": "#e74c3c",
    "btn_buscar": "#2980b9"
}

# Opciones de combobox
OPCIONES_SITUACION = [
    "ACTIVO", "REINSCRITO", "NUEVO INGRESO", "BAJA TEMPORAL",
    "BAJA DEFINITIVA", "CAMBIO DE PLANTEL", "CAMBIO DE CARRERA",
    "SUSPENDIDO", "EGRESADO"
]

OPCIONES_MODALIDAD = ["ESCOLARIZADA", "MIXTA", "NO ESCOLARIZADA", "VIRTUAL", "PRESENCIAL"]
OPCIONES_PERIODO = [str(i) for i in range(1, 13)]
OPCIONES_TIPO_PERIODO = ["SEMESTRE", "CUATRIMESTRE", "TRIMESTRE", "ANUAL"]

# Configuración de paginación
PAGINACION = {
    "registros_por_pagina": 20
}