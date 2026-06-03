ENTIDADES = {
    "AS": "AGUASCALIENTES",
    "BC": "BAJA CALIFORNIA",
    "BS": "BAJA CALIFORNIA SUR",
    "CC": "CAMPECHE",
    "CL": "COAHUILA",
    "CM": "COLIMA",
    "CS": "CHIAPAS",
    "CH": "CHIHUAHUA",
    "DF": "CIUDAD DE MÉXICO",
    "DG": "DURANGO",
    "GT": "GUANAJUATO",
    "GR": "GUERRERO",
    "HG": "HIDALGO",
    "JC": "JALISCO",
    "MC": "ESTADO DE MÉXICO",
    "MN": "MICHOACÁN",
    "MS": "MORELOS",
    "NT": "NAYARIT",
    "NL": "NUEVO LEÓN",
    "OC": "OAXACA",
    "PL": "PUEBLA",
    "QT": "QUERÉTARO",
    "QR": "QUINTANA ROO",
    "SP": "SAN LUIS POTOSÍ",
    "SL": "SINALOA",
    "SR": "SONORA",
    "TC": "TABASCO",
    "TS": "TAMAULIPAS",
    "TL": "TLAXCALA",
    "VZ": "VERACRUZ",
    "YN": "YUCATÁN",
    "ZS": "ZACATECAS",
    "NE": "NACIDO EN EL EXTRANJERO"
}


def analizar_curp(curp):
    curp = curp.strip().upper()

    if len(curp) != 18:
        raise ValueError("La CURP debe tener 18 caracteres")

    fecha = curp[4:10]
    sexo = curp[10]
    entidad = curp[11:13]

    anio = int(fecha[0:2])
    mes = fecha[2:4]
    dia = fecha[4:6]

    anio_completo = 2000 + anio if anio <= 30 else 1900 + anio

    return {
        "fecha_nac": f"{dia}/{mes}/{anio_completo}",
        "sexo": "HOMBRE" if sexo == "H" else "MUJER",
        "entidad_nacimiento": ENTIDADES.get(entidad, entidad)
    }