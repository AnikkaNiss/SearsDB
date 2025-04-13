import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem,
                             QMessageBox, QStackedWidget, QComboBox, QHeaderView)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QDoubleValidator, QIntValidator

class DatabaseManager:
    def __init__(self):
        # Esta sería la conexión real a la base de datos
        # self.connection = mysql.connector.connect(...)
        self.departamentos = []
        self.proveedores = []
        self.productos = []
        self.empleados = []
        self.clientes = []

class CrudApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.db = DatabaseManager()
        self.setWindowTitle("Sistema de Gestión Sears - CRUD Catálogos")
        self.setGeometry(100, 100, 1000, 700)
        
        # Configuración principal
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)
        
        # Selector de tablas (solo tablas catálogo sin relaciones complejas)
        self.table_selector = QComboBox()
        self.table_selector.addItems(["Departamentos", "Proveedores", "Productos", "Empleados", "Clientes"])
        self.table_selector.currentIndexChanged.connect(self.switch_crud)
        
        # Stacked Widget para los diferentes CRUDs
        self.stacked_widget = QStackedWidget()
        
        # Inicializar los CRUDs
        self.init_departamento_crud()
        self.init_proveedor_crud()
        self.init_producto_crud()
        self.init_empleado_crud()
        self.init_cliente_crud()
        
        # Agregar componentes
        self.main_layout.addWidget(QLabel("Seleccione el catálogo a gestionar:"))
        self.main_layout.addWidget(self.table_selector)
        self.main_layout.addWidget(self.stacked_widget)
    
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
        
        # Layout final
        layout.addLayout(form_layout)
        layout.addLayout(btn_layout)
        layout.addWidget(self.departamento_table)
        widget.setLayout(layout)
        self.stacked_widget.addWidget(widget)
    
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
        
        # Layout final
        layout.addLayout(form_layout)
        layout.addLayout(btn_layout)
        layout.addWidget(self.proveedor_table)
        widget.setLayout(layout)
        self.stacked_widget.addWidget(widget)
    
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
            ("Precio Público:", self.producto_precio_publico)
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
        self.producto_table.setColumnCount(6)
        self.producto_table.setHorizontalHeaderLabels(["ID", "Nombre", "Descripción", "Precio Costo", "Precio Público", "Departamento"])
        self.producto_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.producto_table.cellClicked.connect(lambda r, _: self.load_producto_data(r))
        
        # Layout final
        layout.addLayout(form_layout)
        layout.addLayout(btn_layout)
        layout.addWidget(self.producto_table)
        widget.setLayout(layout)
        self.stacked_widget.addWidget(widget)
    
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
    
    def init_cliente_crud(self):
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Formulario
        form_layout = QVBoxLayout()
        
        self.cliente_id = QLineEdit()
        self.cliente_id.setVisible(False)
        
        campos = [
            ("Nombre:", "cliente_nombre", QLineEdit()),
            ("Correo:", "cliente_correo", QLineEdit()),
            ("Teléfono:", "cliente_telefono", QLineEdit())
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
    
    def switch_crud(self, index):
        self.stacked_widget.setCurrentIndex(index)
    
    # Métodos para cargar datos en formularios al seleccionar fila
    def load_departamento_data(self, row):
        pass
    
    def load_proveedor_data(self, row):
        pass
    
    def load_producto_data(self, row):
        pass
    
    def load_empleado_data(self, row):
        pass
    
    def load_cliente_data(self, row):
        pass
    
    # Handlers para acciones CRUD (implementación vacía)
    def handle_departamento_action(self, action):
        if action == "Limpiar":
            self.departamento_id.clear()
            self.departamento_nombre.clear()
            self.departamento_ubicacion.clear()
            self.departamento_encargado.clear()
    
    def handle_proveedor_action(self, action):
        if action == "Limpiar":
            self.proveedor_id.clear()
            self.proveedor_nombre.clear()
            self.proveedor_contacto.clear()
            self.proveedor_telefono.clear()
    
    def handle_producto_action(self, action):
        if action == "Limpiar":
            self.producto_id.clear()
            self.producto_nombre.clear()
            self.producto_descripcion.clear()
            self.producto_precio_costo.clear()
            self.producto_precio_publico.clear()
            self.producto_departamento.setCurrentIndex(0)
            self.producto_proveedor.setCurrentIndex(0)
    
    def handle_empleado_action(self, action):
        if action == "Limpiar":
            self.empleado_id.clear()
            self.empleado_nombre.clear()
            self.empleado_domicilio.clear()
            self.empleado_puesto.clear()
            self.empleado_departamento.setCurrentIndex(0)
    
    def handle_cliente_action(self, action):
        if action == "Limpiar":
            self.cliente_id.clear()
            self.cliente_nombre.clear()
            self.cliente_correo.clear()
            self.cliente_telefono.clear()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CrudApp()
    window.show()
    sys.exit(app.exec())