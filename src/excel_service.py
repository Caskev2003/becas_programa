import pandas as pd


def leer_excel(ruta):
    df = pd.read_excel(ruta)
    df.columns = df.columns.str.strip().str.upper()
    return df


def exportar_excel(datos, ruta):
    df = pd.DataFrame(datos)
    df.to_excel(ruta, index=False)