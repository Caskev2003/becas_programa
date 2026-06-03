import math
import pandas as pd
import mysql.connector
from mysql.connector import Error


DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "12345678",
    "database": "sistema_becas",
    "port": 3306
}


COLUMNAS_EXCEL = {
    "CURP": "curp",
    "P_APELLIDO": "p_apellido",
    "S_APELLIDO": "s_apellido",
    "NOMBRE": "nombre",
    "FECHA_NAC": "fecha_nac",
    "SEXO": "sexo",
    "ENTIDAD_NACIMIENTO": "entidad_nacimiento",
    "SITUACION": "situacion",
    "CAUSA_SITUACION": "causa_situacion",
    "TIPO_PERIODO": "tipo_periodo",
    "PERIODO": "periodo",
    "MODALIDAD": "modalidad",
}


def conectar():
    try:
        return mysql.connector.connect(**DB_CONFIG)
    except Error as e:
        raise Exception(
            "No se pudo conectar a MySQL.\n\n"
            "Revisa que XAMPP tenga MySQL encendido y que usuario/contraseña sean correctos.\n\n"
            f"Detalle: {e}"
        )


def normalizar(valor):
    if valor is None:
        return ""

    if isinstance(valor, float) and math.isnan(valor):
        return ""

    if pd.isna(valor):
        return ""

    texto = str(valor).strip()

    if texto.lower() in ["nan", "none", "nat"]:
        return ""

    return texto


def obtener_valor(datos, columna_excel):
    return normalizar(datos.get(columna_excel, ""))


def insertar_o_actualizar_alumno(datos):
    conexion = None
    cursor = None

    try:
        conexion = conectar()
        cursor = conexion.cursor()

        sql = """
        INSERT INTO alumnos (
            curp,
            p_apellido,
            s_apellido,
            nombre,
            fecha_nac,
            sexo,
            entidad_nacimiento,
            situacion,
            causa_situacion,
            tipo_periodo,
            periodo,
            modalidad
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
            p_apellido = VALUES(p_apellido),
            s_apellido = VALUES(s_apellido),
            nombre = VALUES(nombre),
            fecha_nac = VALUES(fecha_nac),
            sexo = VALUES(sexo),
            entidad_nacimiento = VALUES(entidad_nacimiento),
            situacion = VALUES(situacion),
            causa_situacion = VALUES(causa_situacion),
            tipo_periodo = VALUES(tipo_periodo),
            periodo = VALUES(periodo),
            modalidad = VALUES(modalidad)
        """

        valores = (
            obtener_valor(datos, "CURP").upper(),
            obtener_valor(datos, "P_APELLIDO").upper(),
            obtener_valor(datos, "S_APELLIDO").upper(),
            obtener_valor(datos, "NOMBRE").upper(),
            obtener_valor(datos, "FECHA_NAC"),
            obtener_valor(datos, "SEXO").upper(),
            obtener_valor(datos, "ENTIDAD_NACIMIENTO").upper(),
            obtener_valor(datos, "SITUACION").upper(),
            obtener_valor(datos, "CAUSA_SITUACION").upper(),
            obtener_valor(datos, "TIPO_PERIODO").upper(),
            obtener_valor(datos, "PERIODO").upper(),
            obtener_valor(datos, "MODALIDAD").upper(),
        )

        cursor.execute(sql, valores)
        conexion.commit()

    except Error as e:
        raise Exception(f"Error al insertar/actualizar alumno:\n{e}")

    finally:
        if cursor:
            cursor.close()
        if conexion:
            conexion.close()


def importar_dataframe_a_mysql(df):
    total = 0
    omitidos = 0

    df.columns = df.columns.str.strip().str.upper()

    if "CURP" not in df.columns:
        raise Exception("El archivo Excel debe tener una columna llamada CURP.")

    for _, fila in df.iterrows():
        datos = fila.to_dict()

        curp = obtener_valor(datos, "CURP").upper()

        if curp == "" or len(curp) != 18:
            omitidos += 1
            continue

        insertar_o_actualizar_alumno(datos)
        total += 1

    return {
        "guardados": total,
        "omitidos": omitidos
    }


def buscar_alumno_por_curp(curp):
    conexion = None
    cursor = None

    try:
        conexion = conectar()
        cursor = conexion.cursor(dictionary=True)

        sql = """
        SELECT 
            id,
            curp,
            p_apellido,
            s_apellido,
            nombre,
            fecha_nac,
            sexo,
            entidad_nacimiento,
            situacion,
            causa_situacion,
            tipo_periodo,
            periodo,
            modalidad
        FROM alumnos
        WHERE curp = %s
        """

        cursor.execute(sql, (normalizar(curp).upper(),))
        return cursor.fetchone()

    except Error as e:
        raise Exception(f"Error al buscar alumno:\n{e}")

    finally:
        if cursor:
            cursor.close()
        if conexion:
            conexion.close()


def obtener_todos_los_alumnos():
    conexion = None
    cursor = None

    try:
        conexion = conectar()
        cursor = conexion.cursor(dictionary=True)

        cursor.execute("""
            SELECT 
                id,
                curp,
                p_apellido,
                s_apellido,
                nombre,
                fecha_nac,
                sexo,
                entidad_nacimiento,
                situacion,
                causa_situacion,
                tipo_periodo,
                periodo,
                modalidad
            FROM alumnos
            ORDER BY id DESC
        """)

        return cursor.fetchall()

    except Error as e:
        raise Exception(f"Error al obtener registros:\n{e}")

    finally:
        if cursor:
            cursor.close()
        if conexion:
            conexion.close()


def actualizar_alumno(id_alumno, datos):
    conexion = None
    cursor = None

    try:
        conexion = conectar()
        cursor = conexion.cursor()

        sql = """
        UPDATE alumnos SET
            curp = %s,
            p_apellido = %s,
            s_apellido = %s,
            nombre = %s,
            fecha_nac = %s,
            sexo = %s,
            entidad_nacimiento = %s,
            situacion = %s,
            causa_situacion = %s,
            tipo_periodo = %s,
            periodo = %s,
            modalidad = %s
        WHERE id = %s
        """

        valores = (
            normalizar(datos.get("curp")).upper(),
            normalizar(datos.get("p_apellido")).upper(),
            normalizar(datos.get("s_apellido")).upper(),
            normalizar(datos.get("nombre")).upper(),
            normalizar(datos.get("fecha_nac")),
            normalizar(datos.get("sexo")).upper(),
            normalizar(datos.get("entidad_nacimiento")).upper(),
            normalizar(datos.get("situacion")).upper(),
            normalizar(datos.get("causa_situacion")).upper(),
            normalizar(datos.get("tipo_periodo")).upper(),
            normalizar(datos.get("periodo")).upper(),
            normalizar(datos.get("modalidad")).upper(),
            id_alumno
        )

        cursor.execute(sql, valores)
        conexion.commit()

    except Error as e:
        raise Exception(f"Error al actualizar alumno:\n{e}")

    finally:
        if cursor:
            cursor.close()
        if conexion:
            conexion.close()


def eliminar_alumno(id_alumno):
    conexion = None
    cursor = None

    try:
        conexion = conectar()
        cursor = conexion.cursor()

        cursor.execute(
            "DELETE FROM alumnos WHERE id = %s",
            (id_alumno,)
        )

        conexion.commit()

    except Error as e:
        raise Exception(f"Error al eliminar alumno:\n{e}")

    finally:
        if cursor:
            cursor.close()
        if conexion:
            conexion.close()