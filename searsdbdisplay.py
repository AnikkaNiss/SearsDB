import sys
import mysql.connector
import time
import random
from mysql.connector import Error
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem,
    QMessageBox, QStackedWidget, QComboBox, QHeaderView, QSpinBox, QTextEdit
)
from PyQt6.QtCore import Qt, QRegularExpression
from PyQt6.QtGui import QDoubleValidator, QIntValidator, QRegularExpressionValidator

class DatabaseManager:
    def __init__(self):
        try:
            self.connection = mysql.connector.connect(
                host='localhost',
                port=3307,
                user='root',
                password='root',
                database='sears_db'
            )
            print("¡Conexión exitosa a MySQL!")
        except Error as e:
            print(f"Error al conectar a MySQL: {e}")
            QMessageBox.critical(None, "Error de conexión", f"No se pudo conectar a la base de datos:\n{str(e)}")
            raise

    def execute_query(self, query, params=None, fetch=False):
        try:
            cursor = self.connection.cursor(dictionary=True)
            cursor.execute(query, params or ())
            
            if fetch:
                result = cursor.fetchall()
            else:
                self.connection.commit()
                result = cursor.rowcount
            
            cursor.close()
            return result
        except Error as e:
            print(f"Error en la consulta: {e}")
            self.connection.rollback()
            return None

class SearsManagementSystem(QMainWindow):
        def __init__(self):
            super().__init__()
            try:
                self.db = DatabaseManager()
                self.setup_ui()
                self.load_initial_data()
            except Exception as e:
                QMessageBox.critical(self, "Error crítico", f"No se pudo iniciar la aplicación:\n{str(e)}")
                sys.exit(1)

        def setup_ui(self):
            self.setWindowTitle("Sistema de Gestión Sears - Completo")
            self.setGeometry(100, 100, 1200, 800)
            
            # Configuración principal
            self.central_widget = QWidget()
            self.setCentralWidget(self.central_widget)
            self.main_layout = QVBoxLayout(self.central_widget)
            
            # Menú superior
            self.menu_bar = self.menuBar()
            
            # Menú Catálogos
            catalog_menu = self.menu_bar.addMenu("Catálogos")
            catalog_menu.addAction("Departamentos", lambda: self.stacked_widget.setCurrentIndex(0))
            catalog_menu.addAction("Proveedores", lambda: self.stacked_widget.setCurrentIndex(1))
            catalog_menu.addAction("Productos", lambda: self.stacked_widget.setCurrentIndex(2))
            catalog_menu.addAction("Empleados", lambda: self.stacked_widget.setCurrentIndex(3))
            catalog_menu.addAction("Clientes", lambda: self.stacked_widget.setCurrentIndex(4))
            
            # Menú Operaciones
            operations_menu = self.menu_bar.addMenu("Operaciones")
            operations_menu.addAction("Ventas", lambda: self.stacked_widget.setCurrentIndex(5))
            
            # Stacked Widget para las diferentes secciones
            self.stacked_widget = QStackedWidget()
            
            # Inicializar las secciones
            self.init_departamento_crud()
            self.init_proveedor_crud()
            self.init_producto_crud()
            self.init_empleado_crud()
            self.init_cliente_crud()
            self.init_ventas_view()
            
            # Agregar componentes
            self.main_layout.addWidget(self.stacked_widget)
            
            # Estado inicial
            self.carrito = []

        def load_initial_data(self):
            self.refresh_comboboxes()
            self.refresh_departamento_table()
            self.refresh_proveedor_table()
            self.refresh_producto_table()
            self.refresh_empleado_table()
            self.refresh_cliente_table()
            self.load_clientes_empleados()

        def refresh_comboboxes(self):
            # Departamentos
            query = "SELECT id_departamento, nombre FROM departamentos"
            departamentos = self.db.execute_query(query, fetch=True)
            
            self.producto_departamento.clear()
            self.empleado_departamento.clear()
            
            if departamentos:
                for depto in departamentos:
                    self.producto_departamento.addItem(depto['nombre'], depto['id_departamento'])
                    self.empleado_departamento.addItem(depto['nombre'], depto['id_departamento'])
            
            # Proveedores
            query = "SELECT id_proveedor, nombre FROM proveedores"
            proveedores = self.db.execute_query(query, fetch=True)
            self.producto_proveedor.clear()
            
            if proveedores:
                for prov in proveedores:
                    self.producto_proveedor.addItem(prov['nombre'], prov['id_proveedor'])

        # ------------------------- SECCIÓN DEPARTAMENTOS -------------------------
        def init_departamento_crud(self):
            widget = QWidget()
            layout = QVBoxLayout()
            
            # Formulario
            form_layout = QVBoxLayout()
            
            self.departamento_id = QLineEdit()
            self.departamento_id.setVisible(False)
            
            campos = [
                ("Nombre:", "departamento_nombre", QLineEdit()),
                ("Ubicación:", "departamento_ubicacion", QLineEdit()),
                ("Encargado:", "departamento_encargado", QLineEdit())
            ]
            
            for label_text, attr_name, widget_type in campos:
                hbox = QHBoxLayout()
                hbox.addWidget(QLabel(label_text))
                setattr(self, attr_name, widget_type)
                hbox.addWidget(getattr(self, attr_name))
                form_layout.addLayout(hbox)
            
            # Botones CRUD
            btn_layout = QHBoxLayout()
            btn_names = ["Crear", "Actualizar", "Eliminar", "Limpiar"]
            for name in btn_names:
                btn = QPushButton(name)
                btn.clicked.connect(lambda _, x=name: self.handle_departamento_action(x))
                btn_layout.addWidget(btn)
            
            # Tabla
            self.departamento_table = QTableWidget()
            self.departamento_table.setColumnCount(4)
            self.departamento_table.setHorizontalHeaderLabels(["ID", "Nombre", "Ubicación", "Encargado"])
            self.departamento_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
            self.departamento_table.cellClicked.connect(lambda r, _: self.load_departamento_data(r))
            
            layout.addLayout(form_layout)
            layout.addLayout(btn_layout)
            layout.addWidget(self.departamento_table)
            widget.setLayout(layout)
            self.stacked_widget.addWidget(widget)

        def refresh_departamento_table(self):
            query = "SELECT id_departamento, nombre, ubicacion, encargado FROM departamentos"
            departamentos = self.db.execute_query(query, fetch=True)
            
            if departamentos is not None:
                self.departamento_table.setRowCount(len(departamentos))
                for row_idx, row_data in enumerate(departamentos):
                    self.departamento_table.setItem(row_idx, 0, QTableWidgetItem(str(row_data['id_departamento'])))
                    self.departamento_table.setItem(row_idx, 1, QTableWidgetItem(row_data['nombre']))
                    self.departamento_table.setItem(row_idx, 2, QTableWidgetItem(row_data['ubicacion']))
                    self.departamento_table.setItem(row_idx, 3, QTableWidgetItem(row_data['encargado']))

        def load_departamento_data(self, row):
            id_item = self.departamento_table.item(row, 0)
            if id_item:
                id_departamento = id_item.text()
                query = "SELECT * FROM departamentos WHERE id_departamento = %s"
                departamento = self.db.execute_query(query, (id_departamento,), fetch=True)
                
                if departamento and len(departamento) > 0:
                    departamento = departamento[0]
                    self.departamento_id.setText(str(departamento['id_departamento']))
                    self.departamento_nombre.setText(departamento['nombre'])
                    self.departamento_ubicacion.setText(departamento['ubicacion'])
                    self.departamento_encargado.setText(departamento['encargado'])

        def handle_departamento_action(self, action):
            if action == "Crear":
                nombre = self.departamento_nombre.text().strip()
                ubicacion = self.departamento_ubicacion.text().strip()
                encargado = self.departamento_encargado.text().strip()
                
                if not nombre:
                    QMessageBox.warning(self, "Error", "El nombre del departamento es obligatorio")
                    return
                    
                query = "INSERT INTO departamentos (nombre, ubicacion, encargado) VALUES (%s, %s, %s)"
                result = self.db.execute_query(query, (nombre, ubicacion, encargado))
                
                if result is not None:
                    QMessageBox.information(self, "Éxito", "Departamento creado correctamente")
                    self.refresh_departamento_table()
                    self.refresh_comboboxes()
                    self.handle_departamento_action("Limpiar")
            
            elif action == "Actualizar":
                id_departamento = self.departamento_id.text().strip()
                if not id_departamento:
                    QMessageBox.warning(self, "Error", "Seleccione un departamento para actualizar")
                    return
                    
                nombre = self.departamento_nombre.text().strip()
                if not nombre:
                    QMessageBox.warning(self, "Error", "El nombre del departamento es obligatorio")
                    return
                    
                query = """UPDATE departamentos 
                        SET nombre = %s, ubicacion = %s, encargado = %s 
                        WHERE id_departamento = %s"""
                params = (
                    nombre,
                    self.departamento_ubicacion.text().strip(),
                    self.departamento_encargado.text().strip(),
                    id_departamento
                )
                
                result = self.db.execute_query(query, params)
                if result is not None:
                    QMessageBox.information(self, "Éxito", "Departamento actualizado correctamente")
                    self.refresh_departamento_table()
                    self.refresh_comboboxes()
            
            elif action == "Eliminar":
                id_departamento = self.departamento_id.text().strip()
                if not id_departamento:
                    QMessageBox.warning(self, "Error", "Seleccione un departamento para eliminar")
                    return
                    
                reply = QMessageBox.question(
                    self, 'Confirmar', 
                    '¿Estás seguro de eliminar este departamento?',
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )
                
                if reply == QMessageBox.StandardButton.Yes:
                    try:
                        # Verificar si hay productos o empleados asociados
                        query_check_products = "SELECT COUNT(*) AS count FROM productos WHERE id_departamento = %s"
                        query_check_employees = "SELECT COUNT(*) AS count FROM empleados WHERE id_departamento = %s"
                        
                        count_products = self.db.execute_query(query_check_products, (id_departamento,), fetch=True)
                        count_employees = self.db.execute_query(query_check_employees, (id_departamento,), fetch=True)
                        
                        if (count_products and count_products[0]['count'] > 0) or (count_employees and count_employees[0]['count'] > 0):
                            QMessageBox.warning(
                                self, "Error", 
                                "No se puede eliminar: Hay productos o empleados asociados a este departamento"
                            )
                            return
                        
                        query = "DELETE FROM departamentos WHERE id_departamento = %s"
                        result = self.db.execute_query(query, (id_departamento,))
                        
                        if result is not None and result > 0:
                            QMessageBox.information(self, "Éxito", "Departamento eliminado correctamente")
                            self.refresh_departamento_table()
                            self.refresh_comboboxes()
                            self.handle_departamento_action("Limpiar")
                        else:
                            QMessageBox.warning(self, "Error", "No se encontró el departamento para eliminar")
                    except Error as e:
                        QMessageBox.critical(self, "Error", f"Error al eliminar: {str(e)}")
            
            elif action == "Limpiar":
                self.departamento_id.clear()
                self.departamento_nombre.clear()
                self.departamento_ubicacion.clear()
                self.departamento_encargado.clear()

        # ------------------------- SECCIÓN PROVEEDORES -------------------------
        def init_proveedor_crud(self):
            widget = QWidget()
            layout = QVBoxLayout()
            
            # Formulario
            form_layout = QVBoxLayout()
            
            self.proveedor_id = QLineEdit()
            self.proveedor_id.setVisible(False)
            
            campos = [
                ("Nombre:", "proveedor_nombre", QLineEdit()),
                ("Contacto:", "proveedor_contacto", QLineEdit()),
                ("Teléfono:", "proveedor_telefono", QLineEdit())
            ]
            
            for label_text, attr_name, widget_type in campos:
                hbox = QHBoxLayout()
                hbox.addWidget(QLabel(label_text))
                setattr(self, attr_name, widget_type)
                hbox.addWidget(getattr(self, attr_name))
                form_layout.addLayout(hbox)
            
            # Botones CRUD
            btn_layout = QHBoxLayout()
            btn_names = ["Crear", "Actualizar", "Eliminar", "Limpiar"]
            for name in btn_names:
                btn = QPushButton(name)
                btn.clicked.connect(lambda _, x=name: self.handle_proveedor_action(x))
                btn_layout.addWidget(btn)
            
            # Tabla
            self.proveedor_table = QTableWidget()
            self.proveedor_table.setColumnCount(4)
            self.proveedor_table.setHorizontalHeaderLabels(["ID", "Nombre", "Contacto", "Teléfono"])
            self.proveedor_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
            self.proveedor_table.cellClicked.connect(lambda r, _: self.load_proveedor_data(r))
            
            layout.addLayout(form_layout)
            layout.addLayout(btn_layout)
            layout.addWidget(self.proveedor_table)
            widget.setLayout(layout)
            self.stacked_widget.addWidget(widget)

        def refresh_proveedor_table(self):
            query = "SELECT id_proveedor, nombre, contacto, telefono FROM proveedores"
            proveedores = self.db.execute_query(query, fetch=True)
            
            if proveedores is not None:
                self.proveedor_table.setRowCount(len(proveedores))
                for row_idx, row_data in enumerate(proveedores):
                    self.proveedor_table.setItem(row_idx, 0, QTableWidgetItem(str(row_data['id_proveedor'])))
                    self.proveedor_table.setItem(row_idx, 1, QTableWidgetItem(row_data['nombre']))
                    self.proveedor_table.setItem(row_idx, 2, QTableWidgetItem(row_data['contacto']))
                    self.proveedor_table.setItem(row_idx, 3, QTableWidgetItem(row_data['telefono']))

        def load_proveedor_data(self, row):
            id_item = self.proveedor_table.item(row, 0)
            if id_item:
                id_proveedor = id_item.text()
                query = "SELECT * FROM proveedores WHERE id_proveedor = %s"
                proveedor = self.db.execute_query(query, (id_proveedor,), fetch=True)
                
                if proveedor and len(proveedor) > 0:
                    proveedor = proveedor[0]
                    self.proveedor_id.setText(str(proveedor['id_proveedor']))
                    self.proveedor_nombre.setText(proveedor['nombre'])
                    self.proveedor_contacto.setText(proveedor['contacto'])
                    self.proveedor_telefono.setText(proveedor['telefono'])

        def handle_proveedor_action(self, action):
            if action == "Crear":
                nombre = self.proveedor_nombre.text().strip()
                contacto = self.proveedor_contacto.text().strip()
                telefono = self.proveedor_telefono.text().strip()
                
                if not nombre:
                    QMessageBox.warning(self, "Error", "El nombre del proveedor es obligatorio")
                    return
                    
                query = "INSERT INTO proveedores (nombre, contacto, telefono) VALUES (%s, %s, %s)"
                result = self.db.execute_query(query, (nombre, contacto, telefono))
                
                if result is not None:
                    QMessageBox.information(self, "Éxito", "Proveedor creado correctamente")
                    self.refresh_proveedor_table()
                    self.refresh_comboboxes()
                    self.handle_proveedor_action("Limpiar")
            
            elif action == "Actualizar":
                id_proveedor = self.proveedor_id.text().strip()
                if not id_proveedor:
                    QMessageBox.warning(self, "Error", "Seleccione un proveedor para actualizar")
                    return
                    
                nombre = self.proveedor_nombre.text().strip()
                if not nombre:
                    QMessageBox.warning(self, "Error", "El nombre del proveedor es obligatorio")
                    return
                    
                query = """UPDATE proveedores 
                        SET nombre = %s, contacto = %s, telefono = %s 
                        WHERE id_proveedor = %s"""
                params = (
                    nombre,
                    self.proveedor_contacto.text().strip(),
                    self.proveedor_telefono.text().strip(),
                    id_proveedor
                )
                
                result = self.db.execute_query(query, params)
                if result is not None:
                    QMessageBox.information(self, "Éxito", "Proveedor actualizado correctamente")
                    self.refresh_proveedor_table()
                    self.refresh_comboboxes()
            
            elif action == "Eliminar":
                id_proveedor = self.proveedor_id.text().strip()
                if not id_proveedor:
                    QMessageBox.warning(self, "Error", "Seleccione un proveedor para eliminar")
                    return
                    
                reply = QMessageBox.question(
                    self, 'Confirmar', 
                    '¿Estás seguro de eliminar este proveedor?',
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )
                
                if reply == QMessageBox.StandardButton.Yes:
                    try:
                        # Verificar si hay productos asociados
                        query_check = "SELECT COUNT(*) AS count FROM productos WHERE id_proveedor = %s"
                        count = self.db.execute_query(query_check, (id_proveedor,), fetch=True)
                        
                        if count and count[0]['count'] > 0:
                            QMessageBox.warning(
                                self, "Error", 
                                "No se puede eliminar: Hay productos asociados a este proveedor"
                            )
                            return
                        
                        query = "DELETE FROM proveedores WHERE id_proveedor = %s"
                        result = self.db.execute_query(query, (id_proveedor,))
                        
                        if result is not None and result > 0:
                            QMessageBox.information(self, "Éxito", "Proveedor eliminado correctamente")
                            self.refresh_proveedor_table()
                            self.refresh_comboboxes()
                            self.handle_proveedor_action("Limpiar")
                        else:
                            QMessageBox.warning(self, "Error", "No se encontró el proveedor para eliminar")
                    except Error as e:
                        QMessageBox.critical(self, "Error", f"Error al eliminar: {str(e)}")
            
            elif action == "Limpiar":
                self.proveedor_id.clear()
                self.proveedor_nombre.clear()
                self.proveedor_contacto.clear()
                self.proveedor_telefono.clear()

        # ------------------------- SECCIÓN PRODUCTOS -------------------------
        def init_producto_crud(self):
            widget = QWidget()
            layout = QVBoxLayout()
            
            # Formulario
            form_layout = QVBoxLayout()
            
            self.producto_id = QLineEdit()
            self.producto_id.setVisible(False)
            
            campos = [
                ("Nombre:", "producto_nombre", QLineEdit()),
                ("Descripción:", "producto_descripcion", QLineEdit())
            ]
            
            # Validadores numéricos
            self.producto_precio_costo = QLineEdit()
            self.producto_precio_costo.setValidator(QDoubleValidator(0, 999999, 2))
            self.producto_precio_publico = QLineEdit()
            self.producto_precio_publico.setValidator(QDoubleValidator(0, 999999, 2))
            self.producto_stock = QLineEdit()
            self.producto_stock.setValidator(QIntValidator(0, 999999))
            
            # Combobox para relaciones
            self.producto_departamento = QComboBox()
            self.producto_proveedor = QComboBox()
            
            # Agregar campos
            for label_text, attr_name, widget_type in campos:
                hbox = QHBoxLayout()
                hbox.addWidget(QLabel(label_text))
                setattr(self, attr_name, widget_type)
                hbox.addWidget(getattr(self, attr_name))
                form_layout.addLayout(hbox)
            
            # Campos numéricos
            num_campos = [
                ("Precio Costo:", self.producto_precio_costo),
                ("Precio Público:", self.producto_precio_publico),
                ("Stock:", self.producto_stock)
            ]
            
            for label_text, campo in num_campos:
                hbox = QHBoxLayout()
                hbox.addWidget(QLabel(label_text))
                hbox.addWidget(campo)
                form_layout.addLayout(hbox)
            
            # Comboboxes
            rel_campos = [
                ("Departamento:", self.producto_departamento),
                ("Proveedor:", self.producto_proveedor)
            ]
            
            for label_text, combo in rel_campos:
                hbox = QHBoxLayout()
                hbox.addWidget(QLabel(label_text))
                hbox.addWidget(combo)
                form_layout.addLayout(hbox)
            
            # Botones CRUD
            btn_layout = QHBoxLayout()
            btn_names = ["Crear", "Actualizar", "Eliminar", "Limpiar"]
            for name in btn_names:
                btn = QPushButton(name)
                btn.clicked.connect(lambda _, x=name: self.handle_producto_action(x))
                btn_layout.addWidget(btn)
            
            # Tabla
            self.producto_table = QTableWidget()
            self.producto_table.setColumnCount(7)
            self.producto_table.setHorizontalHeaderLabels(["ID", "Nombre", "Descripción", "Precio Costo", "Precio Público", "Stock", "Departamento"])
            self.producto_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
            self.producto_table.cellClicked.connect(lambda r, _: self.load_producto_data(r))
            
            # Layout final
            layout.addLayout(form_layout)
            layout.addLayout(btn_layout)
            layout.addWidget(self.producto_table)
            widget.setLayout(layout)
            self.stacked_widget.addWidget(widget)

        def refresh_producto_table(self):
            query = """SELECT p.id_producto, p.nombre, p.descripcion, p.precio_costo, 
                        p.precio_publico, p.stock, d.nombre as departamento
                FROM productos p
                LEFT JOIN departamentos d ON p.id_departamento = d.id_departamento"""
            productos = self.db.execute_query(query, fetch=True)
            
            if productos is not None:
                self.producto_table.setRowCount(len(productos))
                for row_idx, row_data in enumerate(productos):
                    self.producto_table.setItem(row_idx, 0, QTableWidgetItem(str(row_data['id_producto'])))
                    self.producto_table.setItem(row_idx, 1, QTableWidgetItem(row_data['nombre']))
                    self.producto_table.setItem(row_idx, 2, QTableWidgetItem(row_data['descripcion']))
                    self.producto_table.setItem(row_idx, 3, QTableWidgetItem(f"${row_data['precio_costo']:.2f}"))
                    self.producto_table.setItem(row_idx, 4, QTableWidgetItem(f"${row_data['precio_publico']:.2f}"))
                    self.producto_table.setItem(row_idx, 5, QTableWidgetItem(str(row_data['stock'])))
                    self.producto_table.setItem(row_idx, 6, QTableWidgetItem(row_data['departamento']))

        def load_producto_data(self, row):
            id_item = self.producto_table.item(row, 0)
            if id_item:
                id_producto = id_item.text()
                query = "SELECT * FROM productos WHERE id_producto = %s"
                producto = self.db.execute_query(query, (id_producto,), fetch=True)
                
                if producto and len(producto) > 0:
                    producto = producto[0]
                    self.producto_id.setText(str(producto['id_producto']))
                    self.producto_nombre.setText(producto['nombre'])
                    self.producto_descripcion.setText(producto['descripcion'])
                    self.producto_precio_costo.setText(str(producto['precio_costo']))
                    self.producto_precio_publico.setText(str(producto['precio_publico']))
                    self.producto_stock.setText(str(producto['stock']))
                    
                    # Establecer los comboboxes
                    if producto['id_departamento']:
                        index = self.producto_departamento.findData(producto['id_departamento'])
                        if index >= 0:
                            self.producto_departamento.setCurrentIndex(index)
                    
                    if producto['id_proveedor']:
                        index = self.producto_proveedor.findData(producto['id_proveedor'])
                        if index >= 0:
                            self.producto_proveedor.setCurrentIndex(index)

        def handle_producto_action(self, action):
            if action == "Crear":
                nombre = self.producto_nombre.text().strip()
                descripcion = self.producto_descripcion.text().strip()
                precio_costo = self.producto_precio_costo.text().strip()
                precio_publico = self.producto_precio_publico.text().strip()
                stock = self.producto_stock.text().strip()
                
                if not nombre:
                    QMessageBox.warning(self, "Error", "El nombre del producto es obligatorio")
                    return
                if not precio_costo or not precio_publico or not stock:
                    QMessageBox.warning(self, "Error", "Los precios y el stock son obligatorios")
                    return
                    
                try:
                    precio_costo = float(precio_costo)
                    precio_publico = float(precio_publico)
                    stock = int(stock)
                except ValueError:
                    QMessageBox.warning(self, "Error", "Los valores deben ser números válidos")
                    return
                    
                id_departamento = self.producto_departamento.currentData()
                id_proveedor = self.producto_proveedor.currentData()
                
                query = """INSERT INTO productos 
                        (nombre, descripcion, precio_costo, precio_publico, stock, id_departamento, id_proveedor) 
                        VALUES (%s, %s, %s, %s, %s, %s, %s)"""
                params = (
                    nombre,
                    descripcion,
                    precio_costo,
                    precio_publico,
                    stock,
                    id_departamento if id_departamento else None,
                    id_proveedor if id_proveedor else None
                )
                
                result = self.db.execute_query(query, params)
                if result is not None:
                    QMessageBox.information(self, "Éxito", "Producto creado correctamente")
                    self.refresh_producto_table()
                    self.handle_producto_action("Limpiar")
            
            elif action == "Actualizar":
                id_producto = self.producto_id.text().strip()
                if not id_producto:
                    QMessageBox.warning(self, "Error", "Seleccione un producto para actualizar")
                    return
                    
                nombre = self.producto_nombre.text().strip()
                if not nombre:
                    QMessageBox.warning(self, "Error", "El nombre del producto es obligatorio")
                    return
                    
                try:
                    precio_costo = float(self.producto_precio_costo.text().strip())
                    precio_publico = float(self.producto_precio_publico.text().strip())
                    stock = int(self.producto_stock.text().strip())
                except ValueError:
                    QMessageBox.warning(self, "Error", "Los valores deben ser números válidos")
                    return
                    
                query = """UPDATE productos 
                        SET nombre = %s, descripcion = %s, 
                            precio_costo = %s, precio_publico = %s, stock = %s,
                            id_departamento = %s, id_proveedor = %s
                        WHERE id_producto = %s"""
                params = (
                    nombre,
                    self.producto_descripcion.text().strip(),
                    precio_costo,
                    precio_publico,
                    stock,
                    self.producto_departamento.currentData(),
                    self.producto_proveedor.currentData(),
                    id_producto
                )
                
                result = self.db.execute_query(query, params)
                if result is not None:
                    QMessageBox.information(self, "Éxito", "Producto actualizado correctamente")
                    self.refresh_producto_table()
            
            elif action == "Eliminar":
                id_producto = self.producto_id.text().strip()
                if not id_producto:
                    QMessageBox.warning(self, "Error", "Seleccione un producto para eliminar")
                    return
                    
                reply = QMessageBox.question(
                    self, 'Confirmar', 
                    '¿Estás seguro de eliminar este producto?',
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )
                
                if reply == QMessageBox.StandardButton.Yes:
                    try:
                        # Verificar si hay ventas asociadas
                        query_check = "SELECT COUNT(*) AS count FROM detalle_ventas WHERE id_producto = %s"
                        count = self.db.execute_query(query_check, (id_producto,), fetch=True)
                        
                        if count and count[0]['count'] > 0:
                            QMessageBox.warning(
                                self, "Error", 
                                "No se puede eliminar: Este producto tiene ventas asociadas"
                            )
                            return
                        
                        query = "DELETE FROM productos WHERE id_producto = %s"
                        result = self.db.execute_query(query, (id_producto,))
                        
                        if result is not None and result > 0:
                            QMessageBox.information(self, "Éxito", "Producto eliminado correctamente")
                            self.refresh_producto_table()
                            self.handle_producto_action("Limpiar")
                        else:
                            QMessageBox.warning(self, "Error", "No se encontró el producto para eliminar")
                    except Error as e:
                        QMessageBox.critical(self, "Error", f"Error al eliminar: {str(e)}")
            
            elif action == "Limpiar":
                self.producto_id.clear()
                self.producto_nombre.clear()
                self.producto_descripcion.clear()
                self.producto_precio_costo.clear()
                self.producto_precio_publico.clear()
                self.producto_stock.clear()
                self.producto_departamento.setCurrentIndex(0)
                self.producto_proveedor.setCurrentIndex(0)

        # ------------------------- SECCIÓN EMPLEADOS -------------------------
        def init_empleado_crud(self):
            widget = QWidget()
            layout = QVBoxLayout()
            
            # Formulario
            form_layout = QVBoxLayout()
            
            self.empleado_id = QLineEdit()
            self.empleado_id.setVisible(False)
            
            campos = [
                ("Nombre:", "empleado_nombre", QLineEdit()),
                ("Domicilio:", "empleado_domicilio", QLineEdit()),
                ("Puesto:", "empleado_puesto", QLineEdit())
            ]
            
            for label_text, attr_name, widget_type in campos:
                hbox = QHBoxLayout()
                hbox.addWidget(QLabel(label_text))
                setattr(self, attr_name, widget_type)
                hbox.addWidget(getattr(self, attr_name))
                form_layout.addLayout(hbox)
            
            # Combobox para departamento
            self.empleado_departamento = QComboBox()
            hbox = QHBoxLayout()
            hbox.addWidget(QLabel("Departamento:"))
            hbox.addWidget(self.empleado_departamento)
            form_layout.addLayout(hbox)
            
            # Botones CRUD
            btn_layout = QHBoxLayout()
            btn_names = ["Crear", "Actualizar", "Eliminar", "Limpiar"]
            for name in btn_names:
                btn = QPushButton(name)
                btn.clicked.connect(lambda _, x=name: self.handle_empleado_action(x))
                btn_layout.addWidget(btn)
            
            # Tabla
            self.empleado_table = QTableWidget()
            self.empleado_table.setColumnCount(5)
            self.empleado_table.setHorizontalHeaderLabels(["ID", "Nombre", "Domicilio", "Puesto", "Departamento"])
            self.empleado_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
            self.empleado_table.cellClicked.connect(lambda r, _: self.load_empleado_data(r))
            
            # Layout final
            layout.addLayout(form_layout)
            layout.addLayout(btn_layout)
            layout.addWidget(self.empleado_table)
            widget.setLayout(layout)
            self.stacked_widget.addWidget(widget)

        def refresh_empleado_table(self):
            query = """SELECT e.id_empleado, e.nombre, e.domicilio, e.puesto, d.nombre as departamento
                FROM empleados e
                LEFT JOIN departamentos d ON e.id_departamento = d.id_departamento"""
            empleados = self.db.execute_query(query, fetch=True)
            
            if empleados is not None:
                self.empleado_table.setRowCount(len(empleados))
                for row_idx, row_data in enumerate(empleados):
                    self.empleado_table.setItem(row_idx, 0, QTableWidgetItem(str(row_data['id_empleado'])))
                    self.empleado_table.setItem(row_idx, 1, QTableWidgetItem(row_data['nombre']))
                    self.empleado_table.setItem(row_idx, 2, QTableWidgetItem(row_data['domicilio']))
                    self.empleado_table.setItem(row_idx, 3, QTableWidgetItem(row_data['puesto']))
                    self.empleado_table.setItem(row_idx, 4, QTableWidgetItem(row_data['departamento']))

        def load_empleado_data(self, row):
            id_item = self.empleado_table.item(row, 0)
            if id_item:
                id_empleado = id_item.text()
                query = "SELECT * FROM empleados WHERE id_empleado = %s"
                empleado = self.db.execute_query(query, (id_empleado,), fetch=True)
                
                if empleado and len(empleado) > 0:
                    empleado = empleado[0]
                    self.empleado_id.setText(str(empleado['id_empleado']))
                    self.empleado_nombre.setText(empleado['nombre'])
                    self.empleado_domicilio.setText(empleado['domicilio'])
                    self.empleado_puesto.setText(empleado['puesto'])
                    
                    if empleado['id_departamento']:
                        index = self.empleado_departamento.findData(empleado['id_departamento'])
                        if index >= 0:
                            self.empleado_departamento.setCurrentIndex(index)

        def handle_empleado_action(self, action):
            if action == "Crear":
                nombre = self.empleado_nombre.text().strip()
                domicilio = self.empleado_domicilio.text().strip()
                puesto = self.empleado_puesto.text().strip()
                
                if not nombre:
                    QMessageBox.warning(self, "Error", "El nombre del empleado es obligatorio")
                    return
                    
                id_departamento = self.empleado_departamento.currentData()
                
                query = """INSERT INTO empleados 
                        (nombre, domicilio, puesto, id_departamento) 
                        VALUES (%s, %s, %s, %s)"""
                params = (
                    nombre,
                    domicilio,
                    puesto,
                    id_departamento if id_departamento else None
                )
                
                result = self.db.execute_query(query, params)
                if result is not None:
                    QMessageBox.information(self, "Éxito", "Empleado creado correctamente")
                    self.refresh_empleado_table()
                    self.handle_empleado_action("Limpiar")
            
            elif action == "Actualizar":
                id_empleado = self.empleado_id.text().strip()
                if not id_empleado:
                    QMessageBox.warning(self, "Error", "Seleccione un empleado para actualizar")
                    return
                    
                nombre = self.empleado_nombre.text().strip()
                if not nombre:
                    QMessageBox.warning(self, "Error", "El nombre del empleado es obligatorio")
                    return
                    
                query = """UPDATE empleados 
                        SET nombre = %s, domicilio = %s, puesto = %s, id_departamento = %s
                        WHERE id_empleado = %s"""
                params = (
                    nombre,
                    self.empleado_domicilio.text().strip(),
                    self.empleado_puesto.text().strip(),
                    self.empleado_departamento.currentData(),
                    id_empleado
                )
                
                result = self.db.execute_query(query, params)
                if result is not None:
                    QMessageBox.information(self, "Éxito", "Empleado actualizado correctamente")
                    self.refresh_empleado_table()
            
            elif action == "Eliminar":
                id_empleado = self.empleado_id.text().strip()
                if not id_empleado:
                    QMessageBox.warning(self, "Error", "Seleccione un empleado para eliminar")
                    return
                    
                reply = QMessageBox.question(
                    self, 'Confirmar', 
                    '¿Estás seguro de eliminar este empleado?',
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )
                
                if reply == QMessageBox.StandardButton.Yes:
                    try:
                        # Verificar si hay ventas asociadas
                        query_check = "SELECT COUNT(*) AS count FROM ventas WHERE id_empleado = %s"
                        count = self.db.execute_query(query_check, (id_empleado,), fetch=True)
                        
                        if count and count[0]['count'] > 0:
                            QMessageBox.warning(
                                self, "Error", 
                                "No se puede eliminar: Este empleado tiene ventas asociadas"
                            )
                            return
                        
                        query = "DELETE FROM empleados WHERE id_empleado = %s"
                        result = self.db.execute_query(query, (id_empleado,))
                        
                        if result is not None and result > 0:
                            QMessageBox.information(self, "Éxito", "Empleado eliminado correctamente")
                            self.refresh_empleado_table()
                            self.handle_empleado_action("Limpiar")
                        else:
                            QMessageBox.warning(self, "Error", "No se encontró el empleado para eliminar")
                    except Error as e:
                        QMessageBox.critical(self, "Error", f"Error al eliminar: {str(e)}")
            
            elif action == "Limpiar":
                self.empleado_id.clear()
                self.empleado_nombre.clear()
                self.empleado_domicilio.clear()
                self.empleado_puesto.clear()
                self.empleado_departamento.setCurrentIndex(0)

        # ------------------------- SECCIÓN CLIENTES -------------------------
        def init_cliente_crud(self):
            widget = QWidget()
            layout = QVBoxLayout()
            
            # Formulario
            form_layout = QVBoxLayout()
            
            self.cliente_id = QLineEdit()
            self.cliente_id.setVisible(False)
            
            # Validación de email
            email_validator = QRegularExpressionValidator(
                QRegularExpression("[^@]+@[^@]+\.[^@]+"))
            
            campos = [
                ("Nombre:", "cliente_nombre", QLineEdit()),
                ("Correo:", "cliente_correo", QLineEdit()),
                ("Teléfono:", "cliente_telefono", QLineEdit())
            ]
            
            for label_text, attr_name, widget_type in campos:
                hbox = QHBoxLayout()
                hbox.addWidget(QLabel(label_text))
                setattr(self, attr_name, widget_type)
                if attr_name == "cliente_correo":
                    getattr(self, attr_name).setValidator(email_validator)
                hbox.addWidget(getattr(self, attr_name))
                form_layout.addLayout(hbox)
            
            # Botones CRUD
            btn_layout = QHBoxLayout()
            btn_names = ["Crear", "Actualizar", "Eliminar", "Limpiar"]
            for name in btn_names:
                btn = QPushButton(name)
                btn.clicked.connect(lambda _, x=name: self.handle_cliente_action(x))
                btn_layout.addWidget(btn)
            
            # Tabla
            self.cliente_table = QTableWidget()
            self.cliente_table.setColumnCount(4)
            self.cliente_table.setHorizontalHeaderLabels(["ID", "Nombre", "Correo", "Teléfono"])
            self.cliente_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
            self.cliente_table.cellClicked.connect(lambda r, _: self.load_cliente_data(r))
            
            # Layout final
            layout.addLayout(form_layout)
            layout.addLayout(btn_layout)
            layout.addWidget(self.cliente_table)
            widget.setLayout(layout)
            self.stacked_widget.addWidget(widget)

        def refresh_cliente_table(self):
            query = "SELECT id_cliente, nombre, correo, telefono FROM clientes"
            clientes = self.db.execute_query(query, fetch=True)
            
            if clientes is not None:
                self.cliente_table.setRowCount(len(clientes))
                for row_idx, row_data in enumerate(clientes):
                    self.cliente_table.setItem(row_idx, 0, QTableWidgetItem(str(row_data['id_cliente'])))
                    self.cliente_table.setItem(row_idx, 1, QTableWidgetItem(row_data['nombre']))
                    self.cliente_table.setItem(row_idx, 2, QTableWidgetItem(row_data['correo']))
                    self.cliente_table.setItem(row_idx, 3, QTableWidgetItem(row_data['telefono']))

        def load_cliente_data(self, row):
            id_item = self.cliente_table.item(row, 0)
            if id_item:
                id_cliente = id_item.text()
                query = "SELECT * FROM clientes WHERE id_cliente = %s"
                cliente = self.db.execute_query(query, (id_cliente,), fetch=True)
                
                if cliente and len(cliente) > 0:
                    cliente = cliente[0]
                    self.cliente_id.setText(str(cliente['id_cliente']))
                    self.cliente_nombre.setText(cliente['nombre'])
                    self.cliente_correo.setText(cliente['correo'])
                    self.cliente_telefono.setText(cliente['telefono'])

        def handle_cliente_action(self, action):
            if action == "Crear":
                nombre = self.cliente_nombre.text().strip()
                correo = self.cliente_correo.text().strip()
                telefono = self.cliente_telefono.text().strip()
                
                if not nombre:
                    QMessageBox.warning(self, "Error", "El nombre del cliente es obligatorio")
                    return
                if not correo:
                    QMessageBox.warning(self, "Error", "El correo del cliente es obligatorio")
                    return
                    
                query = "INSERT INTO clientes (nombre, correo, telefono) VALUES (%s, %s, %s)"
                result = self.db.execute_query(query, (nombre, correo, telefono))
                
                if result is not None:
                    QMessageBox.information(self, "Éxito", "Cliente creado correctamente")
                    self.refresh_cliente_table()
                    self.load_clientes_empleados()  # Actualizar combo de clientes en ventas
                    self.handle_cliente_action("Limpiar")
            
            elif action == "Actualizar":
                id_cliente = self.cliente_id.text().strip()
                if not id_cliente:
                    QMessageBox.warning(self, "Error", "Seleccione un cliente para actualizar")
                    return
                    
                nombre = self.cliente_nombre.text().strip()
                if not nombre:
                    QMessageBox.warning(self, "Error", "El nombre del cliente es obligatorio")
                    return
                    
                correo = self.cliente_correo.text().strip()
                if not correo:
                    QMessageBox.warning(self, "Error", "El correo del cliente es obligatorio")
                    return
                    
                query = """UPDATE clientes 
                        SET nombre = %s, correo = %s, telefono = %s 
                        WHERE id_cliente = %s"""
                params = (
                    nombre,
                    correo,
                    self.cliente_telefono.text().strip(),
                    id_cliente
                )
                
                result = self.db.execute_query(query, params)
                if result is not None:
                    QMessageBox.information(self, "Éxito", "Cliente actualizado correctamente")
                    self.refresh_cliente_table()
                    self.load_clientes_empleados()  # Actualizar combo de clientes en ventas
            
            elif action == "Eliminar":
                id_cliente = self.cliente_id.text().strip()
                if not id_cliente:
                    QMessageBox.warning(self, "Error", "Seleccione un cliente para eliminar")
                    return
                    
                reply = QMessageBox.question(
                    self, 'Confirmar', 
                    '¿Estás seguro de eliminar este cliente?',
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )
                
                if reply == QMessageBox.StandardButton.Yes:
                    try:
                        # Verificar si hay ventas asociadas
                        query_check = "SELECT COUNT(*) AS count FROM ventas WHERE id_cliente = %s"
                        count = self.db.execute_query(query_check, (id_cliente,), fetch=True)
                        
                        if count and count[0]['count'] > 0:
                            QMessageBox.warning(
                                self, "Error", 
                                "No se puede eliminar: Este cliente tiene ventas asociadas"
                            )
                            return
                        
                        query = "DELETE FROM clientes WHERE id_cliente = %s"
                        result = self.db.execute_query(query, (id_cliente,))
                        
                        if result is not None and result > 0:
                            QMessageBox.information(self, "Éxito", "Cliente eliminado correctamente")
                            self.refresh_cliente_table()
                            self.load_clientes_empleados()  # Actualizar combo de clientes en ventas
                            self.handle_cliente_action("Limpiar")
                        else:
                            QMessageBox.warning(self, "Error", "No se encontró el cliente para eliminar")
                    except Error as e:
                        QMessageBox.critical(self, "Error", f"Error al eliminar: {str(e)}")
            
            elif action == "Limpiar":
                self.cliente_id.clear()
                self.cliente_nombre.clear()
                self.cliente_correo.clear()
                self.cliente_telefono.clear()

        # ------------------------- SECCIÓN VENTAS -------------------------
        def init_ventas_view(self):
            widget = QWidget()
            layout = QVBoxLayout()

            # Parte superior: Cliente, Empleado
            top_layout = QHBoxLayout()
            
            self.cliente_combo = QComboBox()
            self.cliente_combo.setMinimumWidth(250)
            
            self.empleado_combo = QComboBox()
            self.empleado_combo.setMinimumWidth(250)
            
            self.cliente_combo.setToolTip("Seleccione el cliente")
            self.empleado_combo.setToolTip("Seleccione el empleado que realiza la venta")
            
            top_layout.addWidget(QLabel("Cliente:"))
            top_layout.addWidget(self.cliente_combo)
            top_layout.addStretch()
            top_layout.addWidget(QLabel("Empleado:"))
            top_layout.addWidget(self.empleado_combo)
            
            layout.addLayout(top_layout)

            # Buscador y selector de productos
            search_layout = QHBoxLayout()
            self.producto_input = QLineEdit()
            self.producto_input.setPlaceholderText("Nombre o Código")
            self.buscar_btn = QPushButton("Buscar")
            self.buscar_btn.clicked.connect(self.buscar_producto)
            search_layout.addWidget(QLabel("Producto:"))
            search_layout.addWidget(self.producto_input)
            search_layout.addWidget(self.buscar_btn)
            layout.addLayout(search_layout)

            # Resultados de productos
            self.resultado_table = QTableWidget(0, 4)
            self.resultado_table.setHorizontalHeaderLabels(["ID", "Nombre", "Precio", "Stock"])
            self.resultado_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
            self.resultado_table.cellClicked.connect(self.actualizar_stock_disponible)
            layout.addWidget(self.resultado_table)

            # Selección de cantidad y botón agregar
            cantidad_layout = QHBoxLayout()
            self.cantidad_input = QSpinBox()
            self.cantidad_input.setRange(1, 9999)
            self.stock_label = QLabel("Stock disponible: 0")
            self.agregar_btn = QPushButton("Agregar a venta")
            self.agregar_btn.clicked.connect(self.agregar_a_venta)
            cantidad_layout.addWidget(QLabel("Cantidad:"))
            cantidad_layout.addWidget(self.cantidad_input)
            cantidad_layout.addWidget(self.stock_label)
            cantidad_layout.addWidget(self.agregar_btn)
            layout.addLayout(cantidad_layout)

            # Carrito de venta con botones de eliminación
            self.venta_table = QTableWidget(0, 5)
            self.venta_table.setHorizontalHeaderLabels(["ID", "Nombre", "Cantidad", "Subtotal", "Quitar"])
            self.venta_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
            layout.addWidget(QLabel("Carrito de venta:"))
            layout.addWidget(self.venta_table)

            # Total y botones
            total_layout = QHBoxLayout()
            self.total_label = QLabel("Total: $0.00")
            
            # Botón para vaciar todo el carrito
            self.limpiar_btn = QPushButton("Vaciar Carrito")
            self.limpiar_btn.clicked.connect(self.limpiar_carrito)
            self.limpiar_btn.setStyleSheet("background-color: #ffcccc;")
            
            # Botón para confirmar venta
            self.confirmar_btn = QPushButton("Confirmar Venta")
            self.confirmar_btn.clicked.connect(self.confirmar_venta)
            self.confirmar_btn.setStyleSheet("background-color: #ccffcc;")
            
            total_layout.addWidget(self.total_label)
            total_layout.addStretch()
            total_layout.addWidget(self.limpiar_btn)
            total_layout.addWidget(self.confirmar_btn)
            layout.addLayout(total_layout)

            # Ticket final
            self.ticket_display = QTextEdit()
            self.ticket_display.setReadOnly(True)
            layout.addWidget(QLabel("Resumen de la venta:"))
            layout.addWidget(self.ticket_display)

            widget.setLayout(layout)
            self.stacked_widget.addWidget(widget)
            self.carrito = []

        def load_clientes_empleados(self):
            try:
                # Limpiar los combobox
                self.cliente_combo.clear()
                self.empleado_combo.clear()
                
                # Cargar clientes (excluyendo al cliente general)
                clientes = self.db.execute_query(
                    "SELECT id_cliente, nombre FROM clientes WHERE id_cliente != 1 ORDER BY nombre", 
                    fetch=True
                )
                
                # Cargar empleados activos (asumiendo que nivel_acceso > 0 significa activo)
                empleados = self.db.execute_query(
                    """SELECT id_empleado, nombre, puesto 
                    FROM empleados 
                    WHERE nivel_acceso > 0 
                    ORDER BY nombre""", 
                    fetch=True
                )
                
                # Añadir opción por defecto
                self.cliente_combo.addItem("Cliente General", 1)  # Usamos el ID 1 para cliente general
                self.empleado_combo.addItem("Seleccione empleado...", None)
                
                # Llenar combobox de clientes
                if clientes:
                    for cliente in clientes:
                        self.cliente_combo.addItem(
                            f"{cliente['nombre']}", 
                            cliente['id_cliente']
                        )
                
                # Llenar combobox de empleados
                if empleados:
                    for empleado in empleados:
                        self.empleado_combo.addItem(
                            f"{empleado['nombre']} ({empleado['puesto']})", 
                            empleado['id_empleado']
                        )
                        
            except Exception as e:
                print(f"Error al cargar clientes/empleados: {e}")
                QMessageBox.warning(self, "Error", "No se pudieron cargar los empleados/clientes")

        def actualizar_stock_disponible(self, row, column):
            # Actualiza el label de stock cuando se selecciona un producto
            stock = int(self.resultado_table.item(row, 3).text())
            self.stock_label.setText(f"Stock disponible: {stock}")
            self.cantidad_input.setMaximum(stock)
            self.cantidad_input.setValue(1)  # Resetear a 1 cada vez que se selecciona un producto

        def buscar_producto(self):
            texto = self.producto_input.text().strip()
            query = """
    SELECT id_producto, nombre, precio_publico, stock 
    FROM productos 
    WHERE nombre LIKE %s OR id_producto = %s OR codigo_barras = %s
"""
            resultados = self.db.execute_query(query, (f"%{texto}%", texto, texto), fetch=True)
            self.resultado_table.setRowCount(0)
            
            if resultados:
                for row in resultados:
                    r = self.resultado_table.rowCount()
                    self.resultado_table.insertRow(r)
                    self.resultado_table.setItem(r, 0, QTableWidgetItem(str(row["id_producto"])))
                    self.resultado_table.setItem(r, 1, QTableWidgetItem(row["nombre"]))
                    self.resultado_table.setItem(r, 2, QTableWidgetItem(f"{row['precio_publico']:.2f}"))
                    self.resultado_table.setItem(r, 3, QTableWidgetItem(str(row["stock"])))

        def agregar_a_venta(self):
            selected = self.resultado_table.currentRow()
            if selected == -1:
                QMessageBox.warning(self, "Error", "Seleccione un producto")
                return
                
            cantidad = self.cantidad_input.value()
            stock = int(self.resultado_table.item(selected, 3).text())
            
            if cantidad > stock:
                QMessageBox.warning(self, "Error", "No hay suficiente stock")
                return
                
            id_prod = int(self.resultado_table.item(selected, 0).text())
            nombre = self.resultado_table.item(selected, 1).text()
            precio = float(self.resultado_table.item(selected, 2).text())
            subtotal = precio * cantidad
            
            # Verificar si el producto ya está en el carrito
            for item in self.carrito:
                if item["id"] == id_prod:
                    # Verificar si al sumar la cantidad supera el stock
                    if (item["cantidad"] + cantidad) > stock:
                        QMessageBox.warning(self, "Error", "No hay suficiente stock para agregar más unidades")
                        return
                    item["cantidad"] += cantidad
                    item["subtotal"] += subtotal
                    self.actualizar_tabla_venta()
                    self.actualizar_total()
                    return
                    
            # Si no está, agregarlo
            self.carrito.append({
                "id": id_prod, 
                "nombre": nombre, 
                "cantidad": cantidad, 
                "subtotal": subtotal,
                "precio_unitario": precio,
                "stock_disponible": stock
            })
            self.actualizar_tabla_venta()
            self.actualizar_total()

        def actualizar_tabla_venta(self):
            self.venta_table.setRowCount(0)
            for row, item in enumerate(self.carrito):
                self.venta_table.insertRow(row)
                self.venta_table.setItem(row, 0, QTableWidgetItem(str(item["id"])))
                self.venta_table.setItem(row, 1, QTableWidgetItem(item["nombre"]))
                self.venta_table.setItem(row, 2, QTableWidgetItem(str(item["cantidad"])))
                self.venta_table.setItem(row, 3, QTableWidgetItem(f"${item['subtotal']:.2f}"))
                
                # Botón para eliminar este producto específico
                btn_eliminar = QPushButton("X")
                btn_eliminar.setStyleSheet("background-color: #ffcccc; max-width: 30px;")
                btn_eliminar.clicked.connect(lambda _, r=row: self.eliminar_producto_carrito(r))
                self.venta_table.setCellWidget(row, 4, btn_eliminar)

        def eliminar_producto_carrito(self, row):
            if 0 <= row < len(self.carrito):
                self.carrito.pop(row)
                self.actualizar_tabla_venta()
                self.actualizar_total()

        def limpiar_carrito(self):
            if self.carrito:
                reply = QMessageBox.question(
                    self, 'Confirmar', 
                    '¿Estás seguro de vaciar todo el carrito?',
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )
                if reply == QMessageBox.StandardButton.Yes:
                    self.carrito.clear()
                    self.venta_table.setRowCount(0)
                    self.actualizar_total()
                    self.ticket_display.clear()

        def actualizar_total(self):
            total = sum(item["subtotal"] for item in self.carrito)
            self.total_label.setText(f"Total: ${total:.2f}")

        def confirmar_venta(self):
            if not self.carrito:
                QMessageBox.warning(self, "Error", "El carrito está vacío")
                return
                
            id_cliente = self.cliente_combo.currentData()
            id_empleado = self.empleado_combo.currentData()
            
            if not id_empleado:
                QMessageBox.warning(self, "Error", "Seleccione un empleado")
                return
            
            # Verificar stock antes de procesar la venta
            for item in self.carrito:
                # Obtener stock actual de la base de datos
                query = "SELECT stock FROM productos WHERE id_producto = %s"
                producto = self.db.execute_query(query, (item["id"],), fetch=True)
                
                if not producto or producto[0]["stock"] < item["cantidad"]:
                    QMessageBox.warning(
                        self, "Error", 
                        f"No hay suficiente stock para {item['nombre']}\nStock actual: {producto[0]['stock'] if producto else 0}"
                    )
                    return
            
            try:
                # Calcular totales
                subtotal = sum(item["subtotal"] for item in self.carrito)
                iva = subtotal * 0.16  # Asumiendo 16% de IVA
                total = subtotal + iva
                
                # Generar folio
                folio = f"V-{time.strftime('%Y%m%d')}-{random.randint(1000, 9999)}"
                
                # Registrar la venta
                result = self.db.execute_query(
                    """INSERT INTO ventas 
                    (folio, id_cliente, id_empleado, fecha, subtotal, iva, total, estado, metodo_pago) 
                    VALUES (%s, %s, %s, NOW(), %s, %s, %s, 'completada', 'efectivo')""", 
                    (folio, id_cliente, id_empleado, subtotal, iva, total)
                )
                
                if result is None:
                    QMessageBox.critical(self, "Error", "No se pudo registrar la venta")
                    return
                    
                id_venta = self.db.connection.cursor().lastrowid
                
                # Registrar detalles de venta y actualizar stock
                resumen = f"Venta #{folio}\n"
                resumen += f"Fecha: {time.strftime('%d/%m/%Y %H:%M')}\n"
                resumen += f"Cliente: {self.cliente_combo.currentText()}\n"
                resumen += f"Empleado: {self.empleado_combo.currentText()}\n\n"
                resumen += "Productos:\n"
                
                for item in self.carrito:
                    # Registrar detalle
                    self.db.execute_query(
                        """INSERT INTO detalle_ventas 
                        (id_venta, id_producto, cantidad, precio_unitario, importe) 
                        VALUES (%s, %s, %s, %s, %s)""",
                        (id_venta, item["id"], item["cantidad"], item["precio_unitario"], item["subtotal"])
                    )
                    
                    # Actualizar stock del producto
                    self.db.execute_query(
                        "UPDATE productos SET stock = stock - %s WHERE id_producto = %s",
                        (item["cantidad"], item["id"])
                    )
                    
                    resumen += f"- {item['nombre']} x {item['cantidad']} @ ${item['precio_unitario']:.2f} = ${item['subtotal']:.2f}\n"
                
                resumen += f"\nSubtotal: ${subtotal:.2f}\n"
                resumen += f"IVA (16%): ${iva:.2f}\n"
                resumen += f"TOTAL: ${total:.2f}"
                
                # Mostrar ticket
                self.ticket_display.setPlainText(resumen)
                
                # Limpiar carrito y actualizar datos
                self.carrito.clear()
                self.venta_table.setRowCount(0)
                self.actualizar_total()
                self.refresh_producto_table()  # Actualizar tabla de productos
                self.buscar_producto()  # Actualizar resultados de búsqueda
                
                QMessageBox.information(self, "Éxito", f"Venta registrada correctamente\nFolio: {folio}")
            
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error al registrar la venta:\n{str(e)}")
                print(f"Error en confirmar_venta: {e}")

        def closeEvent(self, event):
            if hasattr(self, 'db') and hasattr(self.db, 'connection'):
                self.db.connection.close()
            event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    try:
        print("Iniciando aplicación Sears Management System...")
        window = SearsManagementSystem()
        window.show()
        print("Aplicación iniciada correctamente")
        sys.exit(app.exec())
    except Exception as e:
        print(f"Error al iniciar la aplicación: {e}")
        QMessageBox.critical(None, "Error fatal", f"No se pudo iniciar la aplicación:\n{str(e)}")
        sys.exit(1)