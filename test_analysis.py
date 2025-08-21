"""
Модуль unit-тестов для analysis.py.
"""

import unittest
from unittest.mock import MagicMock, patch
import pandas as pd
from datetime import datetime, timedelta

from analysis import DataAnalyzer
from models import Client, Product, Order, OrderItem


class TestDataAnalyzer(unittest.TestCase):
    """Тесты для класса DataAnalyzer."""

    def setUp(self):
        """Настройка тестовых данных."""
        # Создаем mock базы данных
        self.mock_db = MagicMock()

        # Настраиваем mock данные клиентов
        self.clients = [
            Client(id=1, name="Иван Иванов", email="ivan@example.com",
                   phone="+7-123-456-78-90", address="Москва"),
            Client(id=2, name="Петр Петров", email="petr@example.com",
                   phone="+7-987-654-32-10", address="Санкт-Петербург")
        ]
        self.mock_db.get_all_clients.return_value = self.clients
        self.mock_db.get_client.side_effect = lambda id: next((c for c in self.clients if c.id == id), None)

        # Настраиваем mock данные товаров
        self.products = [
            Product(id=1, name="Телефон", price=500.0, category="Электроника", stock=10),
            Product(id=2, name="Ноутбук", price=1000.0, category="Электроника", stock=5),
            Product(id=3, name="Книга", price=20.0, category="Книги", stock=100)
        ]
        self.mock_db.get_all_products.return_value = self.products
        self.mock_db.get_product.side_effect = lambda id: next((p for p in self.products if p.id == id), None)

        # Настраиваем mock данные заказов
        self.orders = [
            Order(
                id=1,
                client_id=1,
                items=[
                    OrderItem(product_id=1, quantity=2, price=500.0),
                    OrderItem(product_id=3, quantity=1, price=20.0)
                ],
                order_date=datetime(2023, 1, 1)
            ),
            Order(
                id=2,
                client_id=2,
                items=[
                    OrderItem(product_id=2, quantity=1, price=1000.0),
                    OrderItem(product_id=3, quantity=2, price=20.0)
                ],
                order_date=datetime(2023, 1, 2)
            )
        ]
        self.mock_db.get_all_orders.return_value = self.orders
        self.mock_db.get_orders_by_client.side_effect = lambda client_id: [
            order for order in self.orders if order.client_id == client_id
        ]

        # Создаем анализатор с mock базой данных
        self.analyzer = DataAnalyzer(self.mock_db)

    def test_get_orders_dataframe(self):
        """Тест создания DataFrame с заказами."""
        df = self.analyzer.get_orders_dataframe()

        # Проверяем структуру DataFrame
        expected_columns = ['order_id', 'client_id', 'client_name', 'order_date',
                            'product_id', 'product_name', 'product_category',
                            'quantity', 'price', 'total']
        self.assertListEqual(list(df.columns), expected_columns)

        # Проверяем количество строк
        # Два заказа с 2 и 2 товарами = 4 строки
        self.assertEqual(len(df), 4)

        # Проверяем данные
        order_1_data = df[df['order_id'] == 1]
        self.assertEqual(len(order_1_data), 2)
        self.assertEqual(order_1_data['total'].sum(), 1020.0)  # 2*500 + 1*20

    def test_get_clients_dataframe(self):
        """Тест создания DataFrame с клиентами."""
        df = self.analyzer.get_clients_dataframe()

        # Проверяем структуру DataFrame
        expected_columns = ['client_id', 'client_name', 'email', 'phone',
                            'address', 'orders_count', 'total_spent']
        self.assertListEqual(list(df.columns), expected_columns)

        # Проверяем количество строк
        self.assertEqual(len(df), 2)

        # Проверяем данные
        client_1 = df[df['client_id'] == 1].iloc[0]
        self.assertEqual(client_1['orders_count'], 1)
        self.assertEqual(client_1['total_spent'], 1020.0)

    def test_get_products_dataframe(self):
        """Тест создания DataFrame с товарами."""
        df = self.analyzer.get_products_dataframe()

        # Проверяем структуру DataFrame
        expected_columns = ['product_id', 'product_name', 'price', 'category',
                            'stock', 'total_sold', 'total_revenue']
        self.assertListEqual(list(df.columns), expected_columns)

        # Проверяем количество строк
        self.assertEqual(len(df), 3)

        # Проверяем данные
        product_3 = df[df['product_id'] == 3].iloc[0]
        self.assertEqual(product_3['total_sold'], 3)  # 1 + 2
        self.assertEqual(product_3['total_revenue'], 60.0)  # 1*20 + 2*20

    def test_get_sales_statistics(self):
        """Тест расчета статистики продаж."""
        stats = self.analyzer.get_sales_statistics()

        # Проверяем рассчитанные показатели
        self.assertEqual(stats['total_orders'], 2)
        self.assertEqual(stats['total_revenue'], 1020.0 + 1040.0)  # оба заказа
        self.assertEqual(stats['total_clients'], 2)
        self.assertEqual(stats['avg_orders_per_client'], 1.0)  # 2 заказа / 2 клиента
        self.assertAlmostEqual(stats['avg_order_value'], (1020.0 + 1040.0) / 2)

    @patch('analysis.plt.subplots')
    def test_plot_top_clients(self, mock_subplots):
        """Тест создания графика топ клиентов."""
        # Настраиваем mock для matplotlib
        mock_fig = MagicMock()
        mock_ax = MagicMock()
        mock_subplots.return_value = (mock_fig, mock_ax)

        # Вызываем метод
        fig = self.analyzer.plot_top_clients()

        # Проверяем, что метод subplots был вызван
        mock_subplots.assert_called_once()

        # Проверяем, что возвращен правильный объект
        self.assertEqual(fig, mock_fig)

    @patch('analysis.plt.subplots')
    def test_plot_orders_dynamics(self, mock_subplots):
        """Тест создания графика динамики заказов."""
        # Настраиваем mock для matplotlib
        mock_fig = MagicMock()
        mock_ax = MagicMock()
        mock_subplots.return_value = (mock_fig, mock_ax)

        # Вызываем метод
        fig = self.analyzer.plot_orders_dynamics()

        # Проверяем, что метод subplots был вызван
        mock_subplots.assert_called_once()

        # Проверяем, что возвращен правильный объект
        self.assertEqual(fig, mock_fig)

    @patch('analysis.nx.spring_layout')
    @patch('analysis.nx.draw_networkx_edges')
    @patch('analysis.nx.draw_networkx_nodes')
    @patch('analysis.nx.draw_networkx_labels')
    @patch('analysis.plt.subplots')
    def test_plot_clients_network(self, mock_subplots, mock_draw_labels,
                                  mock_draw_nodes, mock_draw_edges, mock_spring_layout):
        """Тест создания графа связей клиентов."""
        # Настраиваем mock для matplotlib и networkx
        mock_fig = MagicMock()
        mock_ax = MagicMock()
        mock_subplots.return_value = (mock_fig, mock_ax)
        mock_spring_layout.return_value = {1: (0, 0), 2: (1, 1)}

        # Вызываем метод
        fig = self.analyzer.plot_clients_network()

        # Проверяем, что метод subplots был вызван
        mock_subplots.assert_called_once()

        # Проверяем, что возвращен правильный объект
        self.assertEqual(fig, mock_fig)


if __name__ == "__main__":
    unittest.main()