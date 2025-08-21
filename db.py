"""
Модуль для работы с базой данных SQLite.
Обеспечивает сохранение и загрузку данных о клиентах, товарах и заказах.
"""

import sqlite3
import json
from typing import List, Optional
from datetime import datetime

from models import Client, Product, Order, OrderItem


class Database:
    """Класс для работы с базой данных SQLite."""

    def __init__(self, db_name: str = "database.db"):
        """
        Инициализирует подключение к базе данных.

        Parameters
        ----------
        db_name : str, optional
            Имя файла базы данных (по умолчанию "database.db")
        """
        self.db_name = db_name
        self.init_db()

    def init_db(self):
        """Инициализирует таблицы в базе данных, если они не существуют."""
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()

            # Таблица клиентов
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS clients (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    phone TEXT NOT NULL,
                    address TEXT NOT NULL
                )
            ''')

            # Таблица товаров
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS products (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    price REAL NOT NULL,
                    category TEXT NOT NULL,
                    stock INTEGER NOT NULL
                )
            ''')

            # Таблица заказов
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS orders (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    client_id INTEGER NOT NULL,
                    order_date TEXT NOT NULL,
                    total REAL NOT NULL,
                    FOREIGN KEY (client_id) REFERENCES clients (id)
                )
            ''')

            # Таблица позиций заказов
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS order_items (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    order_id INTEGER NOT NULL,
                    product_id INTEGER NOT NULL,
                    quantity INTEGER NOT NULL,
                    price REAL NOT NULL,
                    FOREIGN KEY (order_id) REFERENCES orders (id),
                    FOREIGN KEY (product_id) REFERENCES products (id)
                )
            ''')

            conn.commit()

    def add_client(self, client: Client) -> int:
        """
        Добавляет клиента в базу данных.

        Parameters
        ----------
        client : Client
            Объект клиента для добавления

        Returns
        -------
        int
            ID добавленного клиента

        Raises
        ------
        sqlite3.Error
            Если произошла ошибка при работе с базой данных
        """
        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    'INSERT INTO clients (name, email, phone, address) VALUES (?, ?, ?, ?)',
                    (client.name, client.email, client.phone, client.address)
                )
                conn.commit()
                return cursor.lastrowid
        except sqlite3.Error as e:
            raise Exception(f"Ошибка при добавлении клиента: {e}")

    def get_client(self, client_id: int) -> Optional[Client]:
        """
        Получает клиента по ID.

        Parameters
        ----------
        client_id : int
            ID клиента

        Returns
        -------
        Client or None
            Объект клиента или None, если не найден
        """
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM clients WHERE id = ?', (client_id,))
            row = cursor.fetchone()

            if row:
                return Client(id=row[0], name=row[1], email=row[2], phone=row[3], address=row[4])
            return None

    def get_all_clients(self) -> List[Client]:
        """
        Получает всех клиентов из базы данных.

        Returns
        -------
        List[Client]
            Список всех клиентов
        """
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM clients')
            rows = cursor.fetchall()

            clients = []
            for row in rows:
                clients.append(Client(id=row[0], name=row[1], email=row[2], phone=row[3], address=row[4]))
            return clients

    def update_client(self, client: Client) -> bool:
        """
        Обновляет данные клиента в базе данных.

        Parameters
        ----------
        client : Client
            Объект клиента с обновленными данными

        Returns
        -------
        bool
            True если клиент был обновлен, иначе False
        """
        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    'UPDATE clients SET name=?, email=?, phone=?, address=? WHERE id=?',
                    (client.name, client.email, client.phone, client.address, client.id)
                )
                conn.commit()
                return cursor.rowcount > 0
        except sqlite3.Error:
            return False

    def delete_client(self, client_id: int) -> bool:
        """
        Удаляет клиента из базы данных.

        Parameters
        ----------
        client_id : int
            ID клиента для удаления

        Returns
        -------
        bool
            True если клиент был удален, иначе False
        """
        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                cursor.execute('DELETE FROM clients WHERE id=?', (client_id,))
                conn.commit()
                return cursor.rowcount > 0
        except sqlite3.Error:
            return False

    def add_product(self, product: Product) -> int:
        """
        Добавляет товар в базу данных.

        Parameters
        ----------
        product : Product
            Объект товара для добавления

        Returns
        -------
        int
            ID добавленного товара
        """
        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    'INSERT INTO products (name, price, category, stock) VALUES (?, ?, ?, ?)',
                    (product.name, product.price, product.category, product.stock)
                )
                conn.commit()
                return cursor.lastrowid
        except sqlite3.Error as e:
            raise Exception(f"Ошибка при добавлении товара: {e}")

    def get_product(self, product_id: int) -> Optional[Product]:
        """
        Получает товар по ID.

        Parameters
        ----------
        product_id : int
            ID товара

        Returns
        -------
        Product or None
            Объект товара или None, если не найден
        """
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM products WHERE id = ?', (product_id,))
            row = cursor.fetchone()

            if row:
                return Product(id=row[0], name=row[1], price=row[2], category=row[3], stock=row[4])
            return None

    def get_all_products(self) -> List[Product]:
        """
        Получает все товары из базы данных.

        Returns
        -------
        List[Product]
            Список всех товаров
        """
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM products')
            rows = cursor.fetchall()

            products = []
            for row in rows:
                products.append(Product(id=row[0], name=row[1], price=row[2], category=row[3], stock=row[4]))
            return products

    def update_product(self, product: Product) -> bool:
        """
        Обновляет данные товара в базе данных.

        Parameters
        ----------
        product : Product
            Объект товара с обновленными данными

        Returns
        -------
        bool
            True если товар был обновлен, иначе False
        """
        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    'UPDATE products SET name=?, price=?, category=?, stock=? WHERE id=?',
                    (product.name, product.price, product.category, product.stock, product.id)
                )
                conn.commit()
                return cursor.rowcount > 0
        except sqlite3.Error:
            return False

    def delete_product(self, product_id: int) -> bool:
        """
        Удаляет товар из базы данных.

        Parameters
        ----------
        product_id : int
            ID товара для удаления

        Returns
        -------
        bool
            True если товар был удален, иначе False
        """
        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                cursor.execute('DELETE FROM products WHERE id=?', (product_id,))
                conn.commit()
                return cursor.rowcount > 0
        except sqlite3.Error:
            return False

    def add_order(self, order: Order) -> int:
        """
        Добавляет заказ в базу данных.

        Parameters
        ----------
        order : Order
            Объект заказа для добавления

        Returns
        -------
        int
            ID добавленного заказа
        """
        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()

                # Добавляем заказ
                cursor.execute(
                    'INSERT INTO orders (client_id, order_date, total) VALUES (?, ?, ?)',
                    (order.client_id, order.order_date.isoformat(), order.total)
                )
                order_id = cursor.lastrowid

                # Добавляем позиции заказа
                for item in order.items:
                    cursor.execute(
                        'INSERT INTO order_items (order_id, product_id, quantity, price) VALUES (?, ?, ?, ?)',
                        (order_id, item.product_id, item.quantity, item.price)
                    )

                conn.commit()
                return order_id
        except sqlite3.Error as e:
            raise Exception(f"Ошибка при добавлении заказа: {e}")

    def get_order(self, order_id: int) -> Optional[Order]:
        """
        Получает заказ по ID.

        Parameters
        ----------
        order_id : int
            ID заказа

        Returns
        -------
        Order or None
            Объект заказа или None, если не найден
        """
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()

            # Получаем данные заказа
            cursor.execute('SELECT * FROM orders WHERE id = ?', (order_id,))
            order_row = cursor.fetchone()

            if not order_row:
                return None

            # Получаем позиции заказа
            cursor.execute('SELECT * FROM order_items WHERE order_id = ?', (order_id,))
            item_rows = cursor.fetchall()

            # Создаем объекты позиций заказа
            items = []
            for row in item_rows:
                items.append(OrderItem(
                    product_id=row[2],  # product_id
                    quantity=row[3],  # quantity
                    price=row[4]  # price
                ))

            # Создаем объект заказа
            order_date = datetime.fromisoformat(order_row[2])  # order_date
            return Order(
                id=order_row[0],  # id
                client_id=order_row[1],  # client_id
                items=items,
                order_date=order_date
            )

    def get_all_orders(self) -> List[Order]:
        """
        Получает все заказы из базы данных.

        Returns
        -------
        List[Order]
            Список всех заказов
        """
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()

            # Получаем все заказы
            cursor.execute('SELECT id FROM orders')
            order_ids = [row[0] for row in cursor.fetchall()]

            # Получаем каждый заказ по ID
            orders = []
            for order_id in order_ids:
                order = self.get_order(order_id)
                if order:
                    orders.append(order)

            return orders

    def get_orders_by_client(self, client_id: int) -> List[Order]:
        """
        Получает все заказы клиента.

        Parameters
        ----------
        client_id : int
            ID клиента

        Returns
        -------
        List[Order]
            Список заказов клиента
        """
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()

            # Получаем ID заказов клиента
            cursor.execute('SELECT id FROM orders WHERE client_id = ?', (client_id,))
            order_ids = [row[0] for row in cursor.fetchall()]

            # Получаем каждый заказ по ID
            orders = []
            for order_id in order_ids:
                order = self.get_order(order_id)
                if order:
                    orders.append(order)

            return orders

    def delete_order(self, order_id: int) -> bool:
        """
        Удаляет заказ из базы данных.

        Parameters
        ----------
        order_id : int
            ID заказа для удаления

        Returns
        -------
        bool
            True если заказ был удален, иначе False
        """
        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()

                # Удаляем позиции заказа
                cursor.execute('DELETE FROM order_items WHERE order_id=?', (order_id,))

                # Удаляем заказ
                cursor.execute('DELETE FROM orders WHERE id=?', (order_id,))

                conn.commit()
                return cursor.rowcount > 0
        except sqlite3.Error:
            return False

    def export_to_json(self, filename: str):
        """
        Экспортирует все данные в JSON файл.

        Parameters
        ----------
        filename : str
            Имя файла для экспорта
        """
        data = {
            'clients': [client.to_dict() for client in self.get_all_clients()],
            'products': [product.to_dict() for product in self.get_all_products()],
            'orders': [order.to_dict() for order in self.get_all_orders()]
        }

        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def import_from_json(self, filename: str):
        """
        Импортирует данные из JSON файла.

        Parameters
        ----------
        filename : str
            Имя файла для импорта
        """
        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Импортируем клиентов
        for client_data in data.get('clients', []):
            client = Client.from_dict(client_data)
            if self.get_client(client.id):
                self.update_client(client)
            else:
                self.add_client(client)

        # Импортируем товары
        for product_data in data.get('products', []):
            product = Product.from_dict(product_data)
            if self.get_product(product.id):
                self.update_product(product)
            else:
                self.add_product(product)

        # Импортируем заказы
        for order_data in data.get('orders', []):
            order = Order.from_dict(order_data)
            if not self.get_order(order.id):
                self.add_order(order)

    def export_to_csv(self, entity_type: str, filename: str):
        """
        Экспортирует данные в CSV файл.

        Parameters
        ----------
        entity_type : str
            Тип сущности ('clients', 'products' или 'orders')
        filename : str
            Имя файла для экспорта
        """
        import csv

        if entity_type == 'clients':
            data = self.get_all_clients()
            fieldnames = ['id', 'name', 'email', 'phone', 'address']
            rows = [client.to_dict() for client in data]

        elif entity_type == 'products':
            data = self.get_all_products()
            fieldnames = ['id', 'name', 'price', 'category', 'stock']
            rows = [product.to_dict() for product in data]

        elif entity_type == 'orders':
            data = self.get_all_orders()
            fieldnames = ['id', 'client_id', 'order_date', 'total']
            rows = [order.to_dict() for order in data]
            # Убираем items из CSV, так как это сложная структура
            for row in rows:
                if 'items' in row:
                    del row['items']

        else:
            raise ValueError("Неверный тип сущности. Используйте 'clients', 'products' или 'orders'")

        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)