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

-- 3️⃣ Tabla: `proveedores`
CREATE TABLE proveedores (
    id_proveedor INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    contacto VARCHAR(100),
    telefono VARCHAR(20),
    email VARCHAR(100),
    direccion TEXT
);

-- 4️⃣ Tabla: `productos` con soporte para códigos de barras
CREATE TABLE productos (
    id_producto INT AUTO_INCREMENT PRIMARY KEY,
    codigo_barras VARCHAR(50) UNIQUE, -- Campo para código de barras
    nombre VARCHAR(100) NOT NULL,
    descripcion TEXT,
    precio_costo DECIMAL(10,2) NOT NULL,
    precio_publico DECIMAL(10,2) NOT NULL,
    stock INT NOT NULL DEFAULT 0, -- Control de inventario
    id_departamento INT,
    id_proveedor INT,
    fecha_creacion DATETIME DEFAULT CURRENT_TIMESTAMP,
    fecha_actualizacion DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (id_departamento) REFERENCES departamentos(id_departamento),
    FOREIGN KEY (id_proveedor) REFERENCES proveedores(id_proveedor)
);

-- 5️⃣ Tabla: `empleados`
CREATE TABLE empleados (
    id_empleado INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    domicilio VARCHAR(255),
    puesto VARCHAR(100),
    id_departamento INT,
    usuario VARCHAR(50) UNIQUE, -- Para sistema de login
    contrasena VARCHAR(255), -- Contraseña encriptada
    nivel_acceso INT DEFAULT 1, -- 1=basico, 2=admin, etc.
    FOREIGN KEY (id_departamento) REFERENCES departamentos(id_departamento)
);

-- 6️⃣ Tabla: `clientes`
CREATE TABLE clientes (
    id_cliente INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    correo VARCHAR(100) UNIQUE,
    telefono VARCHAR(20),
    direccion TEXT,
    rfc VARCHAR(20),
    puntos_acumulados INT DEFAULT 0 -- Para programas de lealtad
);

-- 7️⃣ Tabla: `ventas` (Cabecera de la venta)
CREATE TABLE ventas (
    id_venta INT AUTO_INCREMENT PRIMARY KEY,
    folio VARCHAR(20) UNIQUE, -- Folio legible para el cliente
    fecha DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    id_empleado INT NOT NULL,
    id_cliente INT DEFAULT 1, -- 1=Cliente general
    subtotal DECIMAL(10,2) NOT NULL,
    iva DECIMAL(10,2) NOT NULL,
    total DECIMAL(10,2) NOT NULL,
    estado ENUM('pendiente', 'completada', 'cancelada') DEFAULT 'completada',
    metodo_pago ENUM('efectivo', 'tarjeta', 'transferencia', 'mixto'),
    FOREIGN KEY (id_empleado) REFERENCES empleados(id_empleado),
    FOREIGN KEY (id_cliente) REFERENCES clientes(id_cliente)
);

-- 8️⃣ Tabla: `detalle_ventas` (Productos vendidos en cada venta)
CREATE TABLE detalle_ventas (
    id_detalle INT AUTO_INCREMENT PRIMARY KEY, -- ID único para cada detalle
    id_venta INT NOT NULL,
    id_producto INT NOT NULL,
    cantidad INT NOT NULL CHECK (cantidad > 0),
    precio_unitario DECIMAL(10,2) NOT NULL, -- Precio en el momento de la venta
    importe DECIMAL(10,2) NOT NULL,
    FOREIGN KEY (id_venta) REFERENCES ventas(id_venta),
    FOREIGN KEY (id_producto) REFERENCES productos(id_producto)
);

-- 9️⃣ Tabla: `inventario` para movimientos de stock
CREATE TABLE inventario (
    id_movimiento INT AUTO_INCREMENT PRIMARY KEY,
    id_producto INT NOT NULL,
    tipo_movimiento ENUM('entrada', 'salida', 'ajuste'),
    cantidad INT NOT NULL,
    fecha DATETIME DEFAULT CURRENT_TIMESTAMP,
    id_usuario INT, -- Empleado que realizó el movimiento
    motivo TEXT,
    FOREIGN KEY (id_producto) REFERENCES productos(id_producto),
    FOREIGN KEY (id_usuario) REFERENCES empleados(id_empleado)
);

-- 🔟 Crear cliente general por defecto
INSERT INTO clientes (id_cliente, nombre, correo, telefono) 
VALUES (1, 'CLIENTE GENERAL', 'general@example.com', '0000000000');

-- 🔟1️⃣ Crear triggers para manejo de inventario
DELIMITER //

-- Trigger para actualizar stock al vender
CREATE TRIGGER after_venta_insert
AFTER INSERT ON detalle_ventas
FOR EACH ROW
BEGIN
    -- Restar del inventario
    UPDATE productos SET stock = stock - NEW.cantidad 
    WHERE id_producto = NEW.id_producto;
    
    -- Registrar movimiento de inventario
    INSERT INTO inventario (id_producto, tipo_movimiento, cantidad, id_usuario, motivo)
    VALUES (NEW.id_producto, 'salida', NEW.cantidad, 
           (SELECT id_empleado FROM ventas WHERE id_venta = NEW.id_venta),
           CONCAT('Venta #', NEW.id_venta));
END//

-- Trigger para revertir stock si se elimina una venta
CREATE TRIGGER after_venta_delete
AFTER DELETE ON detalle_ventas
FOR EACH ROW
BEGIN
    -- Sumar al inventario
    UPDATE productos SET stock = stock + OLD.cantidad 
    WHERE id_producto = OLD.id_producto;
    
    -- Registrar movimiento de inventario
    INSERT INTO inventario (id_producto, tipo_movimiento, cantidad, id_usuario, motivo)
    VALUES (OLD.id_producto, 'entrada', OLD.cantidad, 
           (SELECT id_empleado FROM ventas WHERE id_venta = OLD.id_venta),
           CONCAT('Cancelación venta #', OLD.id_venta));
END//

DELIMITER ;

-- 🔟2️⃣ Crear vista para reporte de ventas
CREATE VIEW vista_ventas AS
SELECT 
    v.id_venta,
    v.folio,
    v.fecha,
    e.nombre AS empleado,
    c.nombre AS cliente,
    COUNT(dv.id_producto) AS total_productos,
    v.subtotal,
    v.iva,
    v.total,
    v.metodo_pago,
    v.estado
FROM ventas v
JOIN empleados e ON v.id_empleado = e.id_empleado
JOIN clientes c ON v.id_cliente = c.id_cliente
LEFT JOIN detalle_ventas dv ON v.id_venta = dv.id_venta
GROUP BY v.id_venta;


INSERT INTO departamentos (nombre, ubicacion, encargado) VALUES
('Electrónica', 'Planta Baja - Zona A', 'Carlos Mendoza'),
('Ropa', 'Primer Piso - Zona B', 'Laura Ramírez'),
('Hogar', 'Segundo Piso - Zona C', 'Fernando López'),
('Juguetería', 'Planta Baja - Zona D', 'Ana Pérez'),
('Deportes', 'Primer Piso - Zona E', 'Miguel Torres');

INSERT INTO productos 
(codigo_barras, nombre, descripcion, precio_costo, precio_publico, stock, id_departamento, id_proveedor) 
VALUES
-- Electrónica (departamento 1, proveedor 1)
('7501000000001', 'Televisor LED 40"', 'Pantalla LED con resolución Full HD', 3500.00, 4999.99, 10, 1, 1),
('7501000000002', 'Laptop 14"', 'Intel Core i5, 8GB RAM, 256GB SSD', 7000.00, 8999.99, 8, 1, 1),
('7501000000003', 'Smartphone X10', 'Pantalla 6.5", 128GB', 4500.00, 6399.99, 12, 1, 1),
('7501000000004', 'Cámara Digital', '16MP, Zoom óptico 10x', 1800.00, 2499.99, 5, 1, 1),
('7501000000005', 'Audífonos Bluetooth', 'Cancelación de ruido activa', 300.00, 599.99, 20, 1, 1),
('7501000000006', 'Tablet 10"', 'Android, 64GB almacenamiento', 1800.00, 2799.99, 10, 1, 1),

-- Ropa (departamento 2, proveedor 2)
('7501000000007', 'Camisa Casual Hombre', 'Algodón, talla M', 150.00, 299.99, 15, 2, 2),
('7501000000008', 'Pantalón de Mezclilla', 'Talla 32', 200.00, 399.99, 12, 2, 2),
('7501000000009', 'Blusa Estampada', 'Talla CH, manga corta', 180.00, 349.99, 10, 2, 2),
('7501000000010', 'Vestido Formal', 'Color negro, talla M', 400.00, 799.99, 5, 2, 2),
('7501000000011', 'Sudadera Unisex', 'Talla L, con gorro', 220.00, 449.99, 8, 2, 2),
('7501000000012', 'Zapatos de vestir', 'Color negro, talla 26', 500.00, 899.99, 7, 2, 2),

-- Hogar (departamento 3, proveedor 3)
('7501000000013', 'Juego de Sábanas', 'Queen size, 300 hilos', 300.00, 599.99, 6, 3, 3),
('7501000000014', 'Lámpara de Mesa', 'LED, diseño moderno', 120.00, 249.99, 10, 3, 3),
('7501000000015', 'Cafetera 12 tazas', 'Automática, negra', 400.00, 699.99, 7, 3, 3),
('7501000000016', 'Plancha a Vapor', 'Suela cerámica', 180.00, 349.99, 9, 3, 3),
('7501000000017', 'Toalla Grande', '100% algodón, blanca', 100.00, 199.99, 15, 3, 3),
('7501000000018', 'Reloj de Pared', 'Clásico, silencioso', 90.00, 189.99, 6, 3, 3),

-- Juguetería (departamento 4, proveedor 4)
('7501000000019', 'Muñeca Princesa', 'Articulada, accesorios incluidos', 150.00, 299.99, 20, 4, 4),
('7501000000020', 'Carrito de Juguete', 'Escala 1:18, metálico', 120.00, 249.99, 18, 4, 4),
('7501000000021', 'Puzzle 1000 piezas', 'Paisaje natural', 90.00, 179.99, 10, 4, 4),
('7501000000022', 'Set de Plastilina', 'Colores variados', 80.00, 159.99, 12, 4, 4),
('7501000000023', 'Juego de Mesa', 'Clásico familiar', 180.00, 349.99, 9, 4, 4),
('7501000000024', 'Pelota de colores', 'Rebotadora para niños', 60.00, 129.99, 25, 4, 4),

-- Deportes (departamento 5, proveedor 5)
('7501000000025', 'Balón de Fútbol', 'Tamaño oficial', 150.00, 299.99, 15, 5, 5),
('7501000000026', 'Raqueta de Tenis', 'Fibra de carbono', 300.00, 599.99, 6, 5, 5),
('7501000000027', 'Guantes de Box', 'Talla M', 250.00, 499.99, 8, 5, 5),
('7501000000028', 'Bicicleta Montaña', 'Rodada 26, 21 velocidades', 1800.00, 2799.99, 3, 5, 5),
('7501000000029', 'Pesa Rusa 10kg', 'Hierro fundido', 350.00, 699.99, 5, 5, 5),
('7501000000030', 'Playera Dry Fit', 'Talla G, transpirable', 100.00, 199.99, 10, 5, 5);

INSERT INTO empleados (nombre, domicilio, puesto, id_departamento, usuario, contrasena, nivel_acceso) VALUES
('Julio Herrera', 'Calle Sol #123', 'Cajero', 1, 'julioh', 'pass123', 1),
('Andrea Ruiz', 'Av. Luna #456', 'Cajero', 2, 'andrear', 'pass123', 1),
('Martín Gómez', 'Calle Marte #789', 'Jefe de piso', 3, 'marting', 'pass123', 2),
('Elena Sánchez', 'Boulevard Sur #321', 'Almacén', 4, 'elenas', 'pass123', 1),
('Oscar Díaz', 'Col. Centro #654', 'Administrador', 5, 'oscard', 'admin123', 2);

INSERT INTO clientes (nombre, correo, telefono, direccion, rfc, puntos_acumulados) VALUES
('María López', 'maria.lopez@gmail.com', '5551112233', 'Calle Jazmín 10, CDMX', 'LOPM850101ABC', 150),
('Luis Martínez', 'luis.mtz@hotmail.com', '5552223344', 'Av. Reforma 200, CDMX', 'MAML870202DEF', 300),
('Sofía Torres', 'sofia.torres@yahoo.com', '5553334455', 'Col. Roma 123, CDMX', 'TOSF880303GHI', 50);

INSERT INTO proveedores (nombre, contacto, telefono, email, direccion) VALUES
('ElectroMex', 'Juan Silva', '5551234567', 'contacto@electromex.com', 'Av. Revolución 120, CDMX'),
('ModaPlus', 'Sandra Ortega', '5557654321', 'ventas@modaplus.com', 'Blvd. Independencia 45, Monterrey'),
('CasaFina', 'Ricardo Pérez', '5553334444', 'rperez@casafina.com', 'Calle Cedros 89, Guadalajara'),
('JuegaBien', 'Marta Reyes', '5554445555', 'marta@juegabien.com', 'Av. Niños 21, Puebla'),
('SportLife', 'Luis Domínguez', '5559998888', 'ldominguez@sportlife.com', 'Carretera Nacional 99, León');