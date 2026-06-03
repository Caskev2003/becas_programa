# crear_bd.py
import mysql.connector

DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "12345678",
    "port": 3306
}

def crear_base_datos():
    try:
        # Conectar sin seleccionar base de datos
        conexion = mysql.connector.connect(**DB_CONFIG)
        cursor = conexion.cursor()
        
        # Crear base de datos
        cursor.execute("CREATE DATABASE IF NOT EXISTS sistema_becas")
        print("✅ Base de datos 'sistema_becas' creada o ya existe")
        
        # Seleccionar la base de datos
        cursor.execute("USE sistema_becas")
        
        # Crear tabla de alumnos
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS alumnos (
                id INT AUTO_INCREMENT PRIMARY KEY,
                curp VARCHAR(18) UNIQUE NOT NULL,
                p_apellido VARCHAR(100),
                s_apellido VARCHAR(100),
                nombre VARCHAR(100),
                fecha_nac DATE,
                sexo VARCHAR(1),
                entidad_nacimiento VARCHAR(100),
                situacion VARCHAR(50),
                causa_situacion VARCHAR(200),
                tipo_periodo VARCHAR(50),
                periodo VARCHAR(20),
                modalidad VARCHAR(50),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            )
        """)
        print("✅ Tabla 'alumnos' creada o ya existe")
        
        cursor.close()
        conexion.close()
        print("\n🎉 Configuración completada con éxito!")
        print("📌 Ahora puedes ejecutar tu programa principal.")
        
    except mysql.connector.Error as e:
        print(f"❌ Error: {e}")
        print("\n🔍 Verifica que:")
        print("   1. XAMPP esté abierto")
        print("   2. MySQL esté corriendo (botón verde)")
        print("   3. La contraseña sea correcta (12345678)")

if __name__ == "__main__":
    crear_base_datos()