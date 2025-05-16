-- 1️⃣ Eliminar la base de datos si ya existe y crearla nuevamente
DROP DATABASE IF EXISTS sears_db;
CREATE DATABASE sears_db;
USE sears_db;

-- 2️⃣ Tabla: `departamentos`
CREATE TABLE departamentos (
    id_departamento INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    ubicacion VARCHAR(255),
    encargado VARCHAR(100)
);

-- 8️⃣ Tabla: `proveedores`
CREATE TABLE proveedores (
    id_proveedor INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    contacto VARCHAR(100),
    telefono VARCHAR(20)
);

-- 3️⃣ Tabla: `productos`
CREATE TABLE productos (
    id_producto INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    descripcion TEXT,
    precio_costo DECIMAL(10,2) NOT NULL,
    precio_publico DECIMAL(10,2) NOT NULL,
    id_departamento INT,
    id_proveedor INT, -- Clave foránea para el proveedor
    FOREIGN KEY (id_departamento) REFERENCES departamentos(id_departamento),
    FOREIGN KEY (id_proveedor) REFERENCES proveedores(id_proveedor) -- Relación con proveedores
);

-- 4️⃣ Tabla: `empleados`
CREATE TABLE empleados (
    id_empleado INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    domicilio VARCHAR(255),
    puesto VARCHAR(100),
    id_departamento INT,
    FOREIGN KEY (id_departamento) REFERENCES departamentos(id_departamento)
);

-- 5️⃣ Tabla: `clientes`
CREATE TABLE clientes (
    id_cliente INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    correo VARCHAR(100) UNIQUE,
    telefono VARCHAR(20)
);

-- 6️⃣ Tabla: `ventas` (Cabecera de la venta)
CREATE TABLE ventas (
    id_venta INT AUTO_INCREMENT PRIMARY KEY,
    fecha DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    id_empleado INT NOT NULL,
    id_cliente INT NOT NULL,
    FOREIGN KEY (id_empleado) REFERENCES empleados(id_empleado),
    FOREIGN KEY (id_cliente) REFERENCES clientes(id_cliente)
);

-- 7️⃣ Tabla: `detalle_ventas` (Productos vendidos en cada venta)
CREATE TABLE detalle_ventas (
    id_venta INT NOT NULL,
    id_producto INT NOT NULL,
    cantidad INT NOT NULL CHECK (cantidad > 0),
    PRIMARY KEY (id_venta, id_producto),
    FOREIGN KEY (id_venta) REFERENCES ventas(id_venta),
    FOREIGN KEY (id_producto) REFERENCES productos(id_producto)
);

