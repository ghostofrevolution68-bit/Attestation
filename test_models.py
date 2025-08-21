"""
Модуль unit-тестов для models.py.
"""

import unittest
from datetime import datetime
from models import Client, Product, Order, OrderItem


class TestClient(unittest.TestCase):
    """Тесты для класса Client."""

    def test_valid_client_creation(self):
        """Тест создания клиента с валидными данными."""
        client = Client(
            name="Иван Иванов",
            email="ivan@example.com",
            phone="+7 (123) 456-78-90",
            address="Москва, ул. Примерная, д. 1"
        )

        self.assertEqual(client.name, "Иван Иванов")
        self.assertEqual(client.email, "ivan@example.com")
        self.assertEqual(client.phone, "+7 (123) 456-78-90")
        self.assertEqual(client.address, "Москва, ул. Примерная, д. 1")

    def test_invalid_email(self):
        """Тест создания клиента с невалидным email."""
        with self.assertRaises(ValueError):
            Client(
                name="Иван Иванов",
                email="invalid-email",
                phone="+7 (123) 456-78-90",
                address="Москва, ул. Примерная, д. 1"
            )

    def test_invalid_phone(self):
        """Тест создания клиента с невалидным телефоном."""
        with self.assertRaises(ValueError):
            Client(
                name="Иван Иванов",
                email="ivan@example.com",
                phone="invalid-phone",
                address="Москва, ул. Примерная, д. 1"
            )

    def test_email_validation(self):
        """Тест валидации email."""
        self.assertTrue(Client.is_valid_email("test@example.com"))
        self.assertTrue(Client.is_valid_email("test.name@example.co.uk"))
        self.assertFalse(Client.is_valid_email("invalid-email"))
        self.assertFalse(Client.is_valid_email("test@"))
        self.assertFalse(Client.is_valid_email("@example.com"))

    def test_phone_validation(self):
        """Тест валидации телефона."""
        self.assertTrue(Client.is_valid_phone("+7 (123) 456-78-90"))
        self.assertTrue(Client.is_valid_phone("81234567890"))
        self.assertTrue(Client.is_valid_phone("8-123-456-78-90"))
        self.assertFalse(Client.is_valid_phone("123"))
        self.assertFalse(Client.is_valid_phone("invalid-phone"))

    def test_to_dict(self):
        """Тест преобразования клиента в словарь."""
        client = Client(
            id=1,
            name="Иван Иванов",
            email="ivan@example.com",
            phone="+7 (123) 456-78-90",
            address="Москва, ул. Примерная, д. 1"
        )

        client_dict = client.to_dict()
        expected_dict = {
            'id': 1,
            'name': "Иван Иванов",
            'email': "ivan@example.com",
            'phone': "+7 (123) 456-78-90",
            'address': "Москва, ул. Примерная, д. 1"
        }

        self.assertEqual(client_dict, expected_dict)

    def test_from_dict(self):
        """Тест создания клиента из словаря."""
        client_dict = {
            'id': 1,
            'name': "Иван Иванов",
            'email': "ivan@example.com",
            'phone': "+7 (123) 456-78-90",
            'address': "Москва, ул. Примерная, д. 1"
        }

        client = Client.from_dict(client_dict)

        self.assertEqual(client.id, 1)
        self.assertEqual(client.name, "Иван Иванов")
        self.assertEqual(client.email, "ivan@example.com")
        self.assertEqual(client.phone, "+7 (123) 456-78-90")
        self.assertEqual(client.address, "Москва, ул. Примерная, д. 1")


class TestProduct(unittest.TestCase):
    """Тесты для класса Product."""

    def test_product_creation(self):
        """Тест создания товара."""
        product = Product(
            id=1,
            name="Телефон",
            price=500.0,
            category="Электроника",
            stock=10
        )

        self.assertEqual(product.id, 1)
        self.assertEqual(product.name, "Телефон")
        self.assertEqual(product.price, 500.0)
        self.assertEqual(product.category, "Электроника")
        self.assertEqual(product.stock, 10)

    def test_to_dict(self):
        """Тест преобразования товара в словарь."""
        product = Product(
            id=1,
            name="Телефон",
            price=500.0,
            category="Электроника",
            stock=10
        )

        product_dict = product.to_dict()
        expected_dict = {
            'id': 1,
            'name': "Телефон",
            'price': 500.0,
            'category': "Электроника",
            'stock': 10
        }

        self.assertEqual(product_dict, expected_dict)

    def test_from_dict(self):
        """Тест создания товара из словаря."""
        product_dict = {
            'id': 1,
            'name': "Телефон",
            'price': 500.0,
            'category': "Электроника",
            'stock': 10
        }

        product = Product.from_dict(product_dict)

        self.assertEqual(product.id, 1)
        self.assertEqual(product.name, "Телефон")
        self.assertEqual(product.price, 500.0)
        self.assertEqual(product.category, "Электроника")
        self.assertEqual(product.stock, 10)


class TestOrderItem(unittest.TestCase):
    """Тесты для класса OrderItem."""

    def test_order_item_creation(self):
        """Тест создания позиции заказа."""
        item = OrderItem(
            product_id=1,
            quantity=2,
            price=500.0
        )

        self.assertEqual(item.product_id, 1)
        self.assertEqual(item.quantity, 2)
        self.assertEqual(item.price, 500.0)
        self.assertEqual(item.total, 1000.0)

    def test_to_dict(self):
        """Тест преобразования позиции заказа в словарь."""
        item = OrderItem(
            product_id=1,
            quantity=2,
            price=500.0
        )

        item_dict = item.to_dict()
        expected_dict = {
            'product_id': 1,
            'quantity': 2,
            'price': 500.0,
            'total': 1000.0
        }

        self.assertEqual(item_dict, expected_dict)

    def test_from_dict(self):
        """Тест создания позиции заказа из словаря."""
        item_dict = {
            'product_id': 1,
            'quantity': 2,
            'price': 500.0
        }

        item = OrderItem.from_dict(item_dict)

        self.assertEqual(item.product_id, 1)
        self.assertEqual(item.quantity, 2)
        self.assertEqual(item.price, 500.0)
        self.assertEqual(item.total, 1000.0)


class TestOrder(unittest.TestCase):
    """Тесты для класса Order."""

    def setUp(self):
        """Настройка тестовых данных."""
        self.items = [
            OrderItem(product_id=1, quantity=2, price=500.0),
            OrderItem(product_id=2, quantity=1, price=300.0)
        ]

    def test_order_creation(self):
        """Тест создания заказа."""
        order = Order(
            id=1,
            client_id=1,
            items=self.items
        )

        self.assertEqual(order.id, 1)
        self.assertEqual(order.client_id, 1)
        self.assertEqual(len(order.items), 2)
        self.assertEqual(order.total, 1300.0)  # 2*500 + 1*300

    def test_add_item(self):
        """Тест добавления позиции в заказ."""
        order = Order(
            id=1,
            client_id=1,
            items=self.items
        )

        # Добавляем новую позицию
        new_item = OrderItem(product_id=3, quantity=1, price=200.0)
        order.add_item(new_item)

        self.assertEqual(len(order.items), 3)
        self.assertEqual(order.total, 1500.0)  # 1300 + 200

    def test_remove_item(self):
        """Тест удаления позиции из заказа."""
        order = Order(
            id=1,
            client_id=1,
            items=self.items
        )

        # Удаляем позицию
        result = order.remove_item(1)

        self.assertTrue(result)
        self.assertEqual(len(order.items), 1)
        self.assertEqual(order.total, 300.0)  # только вторая позиция

    def test_remove_nonexistent_item(self):
        """Тест удаления несуществующей позиции из заказа."""
        order = Order(
            id=1,
            client_id=1,
            items=self.items
        )

        # Пытаемся удалить несуществующую позицию
        result = order.remove_item(999)

        self.assertFalse(result)
        self.assertEqual(len(order.items), 2)
        self.assertEqual(order.total, 1300.0)

    def test_to_dict(self):
        """Тест преобразования заказа в словарь."""
        order = Order(
            id=1,
            client_id=1,
            items=self.items,
            order_date=datetime(2023, 1, 1, 12, 0, 0)
        )

        order_dict = order.to_dict()

        self.assertEqual(order_dict['id'], 1)
        self.assertEqual(order_dict['client_id'], 1)
        self.assertEqual(order_dict['total'], 1300.0)
        self.assertEqual(len(order_dict['items']), 2)
        self.assertEqual(order_dict['order_date'], '2023-01-01T12:00:00')

    def test_from_dict(self):
        """Тест создания заказа из словаря."""
        order_dict = {
            'id': 1,
            'client_id': 1,
            'order_date': '2023-01-01T12:00:00',
            'items': [
                {'product_id': 1, 'quantity': 2, 'price': 500.0},
                {'product_id': 2, 'quantity': 1, 'price': 300.0}
            ],
            'total': 1300.0
        }

        order = Order.from_dict(order_dict)

        self.assertEqual(order.id, 1)
        self.assertEqual(order.client_id, 1)
        self.assertEqual(len(order.items), 2)
        self.assertEqual(order.total, 1300.0)
        self.assertEqual(order.order_date, datetime(2023, 1, 1, 12, 0, 0))


if __name__ == "__main__":
    unittest.main()