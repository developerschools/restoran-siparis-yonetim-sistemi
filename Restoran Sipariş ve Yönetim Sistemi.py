import sys
import sqlite3
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QLabel, QPushButton, QLineEdit, QTextEdit, QListWidget, QComboBox

class Restaurant:
    def __init__(self, name):
        self.name = name
        self.menu = []

    def add_product(self, product):
        self.menu.append(product)

    def update_stock(self, product_name, new_stock):
        for product in self.menu:
            if product.name == product_name:
                product.stock = new_stock
                return True
        return False

class RestaurantApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.create_connection()
        self.create_table()
        self.load_products()
        self.load_orders()

    def initUI(self):
        self.setWindowTitle("Restoran Sipariş ve Yönetim Sistemi")
        self.setGeometry(100, 100, 600, 600)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.layout = QVBoxLayout()

        self.add_product_label = QLabel("Ürün Ekle")
        self.layout.addWidget(self.add_product_label)

        self.product_name_label = QLabel("Ürün Adı:")
        self.layout.addWidget(self.product_name_label)

        self.product_name_input = QLineEdit()
        self.layout.addWidget(self.product_name_input)

        self.product_stock_label = QLabel("Stok:")
        self.layout.addWidget(self.product_stock_label)

        self.product_stock_input = QLineEdit()
        self.layout.addWidget(self.product_stock_input)

        self.product_price_label = QLabel("Fiyat:")
        self.layout.addWidget(self.product_price_label)

        self.product_price_input = QLineEdit()
        self.layout.addWidget(self.product_price_input)

        self.add_product_button = QPushButton("Ürün Ekle")
        self.add_product_button.clicked.connect(self.add_product)
        self.layout.addWidget(self.add_product_button)

        self.layout.addWidget(QLabel("Ürünler"))
        self.product_list_widget = QListWidget()
        self.product_list_widget.itemClicked.connect(self.update_product_form)
        self.layout.addWidget(self.product_list_widget)

        self.update_stock_label = QLabel("Stok Güncelle")
        self.layout.addWidget(self.update_stock_label)

        self.update_stock_input = QLineEdit()
        self.layout.addWidget(self.update_stock_input)

        self.update_stock_button = QPushButton("Stok Güncelle")
        self.update_stock_button.clicked.connect(self.update_stock)
        self.layout.addWidget(self.update_stock_button)

        self.layout.addWidget(QLabel("Sipariş Oluştur"))
        self.customer_name_label = QLabel("Müşteri Adı:")
        self.layout.addWidget(self.customer_name_label)

        self.customer_name_input = QLineEdit()
        self.layout.addWidget(self.customer_name_input)

        self.order_info_label = QLabel("Sipariş Bilgisi:")
        self.layout.addWidget(self.order_info_label)

        self.order_info_combobox = QComboBox()
        self.layout.addWidget(self.order_info_combobox)

        self.customer_address_label = QLabel("Adres:")
        self.layout.addWidget(self.customer_address_label)

        self.customer_address_input = QLineEdit()
        self.layout.addWidget(self.customer_address_input)

        self.create_order_button = QPushButton("Sipariş Ver")
        self.create_order_button.clicked.connect(self.create_order)
        self.layout.addWidget(self.create_order_button)

        self.layout.addWidget(QLabel("Siparişler"))
        self.order_list_widget = QListWidget()
        self.layout.addWidget(self.order_list_widget)

        self.central_widget.setLayout(self.layout)

    def create_connection(self):
        self.conn = sqlite3.connect('restaurant.db')
        self.cur = self.conn.cursor()

    def create_table(self):
        self.cur.execute("""CREATE TABLE IF NOT EXISTS products (
                            id INTEGER PRIMARY KEY,
                            name TEXT,
                            price REAL,
                            stock INTEGER
                            )""")
        self.cur.execute("""CREATE TABLE IF NOT EXISTS orders (
                            id INTEGER PRIMARY KEY,
                            customer_name TEXT,
                            order_info TEXT,
                            customer_address TEXT
                            )""")

    def load_products(self):
        self.restaurant = Restaurant("Lezzet Restoran")
        self.cur.execute("SELECT * FROM products")
        products = self.cur.fetchall()
        for product in products:
            name, price, stock = product[1], product[2], product[3]
            self.restaurant.add_product(Product(name, price, stock))
            self.product_list_widget.addItem(f"{name}: {stock} adet - Fiyat: {price}")
            self.order_info_combobox.addItem(name)

    def load_orders(self):
        self.cur.execute("SELECT * FROM orders")
        orders = self.cur.fetchall()
        for order in orders:
            customer_name, order_info, customer_address = order[1], order[2], order[3]
            self.order_list_widget.addItem(f"Müşteri: {customer_name}, Bilgi: {order_info}, Adres: {customer_address}")

    def add_product(self):
        name = self.product_name_input.text()
        stock = int(self.product_stock_input.text())
        price = float(self.product_price_input.text())
        product = Product(name, price, stock)
        self.restaurant.add_product(product)
        self.add_product_to_db(product)
        self.update_product_list()
        self.clear_product_form()
        # Yeni ürün eklenince sipariş bilgi combobox'ını güncelle
        self.order_info_combobox.addItem(name)

    def add_product_to_db(self, product):
        self.cur.execute("INSERT INTO products (name, price, stock) VALUES (?, ?, ?)",
                         (product.name, product.price, product.stock))
        self.conn.commit()

    def update_product_list(self):
        self.product_list_widget.clear()
        for product in self.restaurant.menu:
            self.product_list_widget.addItem(f"{product.name}: {product.stock} adet - Fiyat: {product.price}")

    def clear_product_form(self):
        self.product_name_input.clear()
        self.product_stock_input.clear()
        self.product_price_input.clear()

    def update_product_form(self, item):
        product_name = item.text().split(":")[0]
        for product in self.restaurant.menu:
            if product.name == product_name:
                self.update_stock_input.setText(str(product.stock))
                break

    def update_stock(self):
        selected_product = self.product_list_widget.currentItem().text().split(":")[0]
        new_stock = int(self.update_stock_input.text())
        success = self.restaurant.update_stock(selected_product, new_stock)
        if success:
            self.update_product_list()
            self.clear_product_form()
            print("Stok güncellendi.")
        else:
            print("Ürün bulunamadı.")

    def create_order(self):
        customer_name = self.customer_name_input.text()
        order_info = self.order_info_combobox.currentText()
        customer_address = self.customer_address_input.text()
        order = Order(None, order_info, Customer(customer_name, customer_address))
        self.order_list_widget.addItem(f"Müşteri: {customer_name}, Bilgi: {order_info}, Adres: {customer_address}")
        self.add_order_to_db(order)

    def add_order_to_db(self, order):
        self.cur.execute("INSERT INTO orders (customer_name, order_info, customer_address) VALUES (?, ?, ?)",
                         (order.customer_info.name, order.contents, order.customer_info.address))
        self.conn.commit()

    def closeEvent(self, event):
        self.conn.close()

class Product:
    def __init__(self, name, price, stock):
        self.name = name
        self.price = price
        self.stock = stock

class Order:
    def __init__(self, id, contents, customer_info):
        self.id = id
        self.contents = contents
        self.customer_info = customer_info

class Customer:
    def __init__(self, name, address):
        self.name = name
        self.address = address

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = RestaurantApp()
    window.show()
    sys.exit(app.exec_())
