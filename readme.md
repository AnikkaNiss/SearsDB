# Sistema de Gestión Sears - CRUD

## Configuración Inicial

### Paso 1. Crear la base de datos
1. Ejecutar el script SQL:  
   `D:\ruta\a\db23270652.sql`  

### Paso 2. Abrir el proyecto

### Paso 3. Crear Entorno Virtual
python -m venv env23270652
env23270652\scripts\activate

### Paso 4. Instalar Librerias
pip install PyQt6 mysql-connector-python

### Paso 5. Modificar la conexion a la db
Editar en database_manager.py:

python
self.connection = mysql.connector.connect(
    host='localhost',
    port=3307,
    user='tu_usuario',
    password='tu_contraseña',
    database='sears_db'
)

### Paso 6. Correr el Programa