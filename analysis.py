"""
Модуль для анализа и визуализации данных о заказах, клиентах и товарах.
Использует pandas, matplotlib, seaborn и networkx.
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import networkx as nx
from datetime import datetime, timedelta
from typing import List, Dict, Tuple, Optional

from models import Client, Product, Order
from db import Database


class DataAnalyzer:
    """Класс для анализа и визуализации данных."""

    def __init__(self, db: Database):
        """
        Инициализирует анализатор данных.

        Parameters
        ----------
        db : Database
            Объект базы данных для анализа
        """
        self.db = db

    def get_orders_dataframe(self) -> pd.DataFrame:
        """
        Создает DataFrame с данными о заказах.

        Returns
        -------
        pd.DataFrame
            DataFrame с заказами
        """
        orders = self.db.get_all_orders()
        data = []

        for order in orders:
            client = self.db.get_client(order.client_id)
            for item in order.items:
                product = self.db.get_product(item.product_id)
                data.append({
                    'order_id': order.id,
                    'client_id': order.client_id,
                    'client_name': client.name if client else 'Неизвестный',
                    'order_date': order.order_date,
                    'product_id': item.product_id,
                    'product_name': product.name if product else 'Неизвестный',
                    'product_category': product.category if product else 'Неизвестная',
                    'quantity': item.quantity,
                    'price': item.price,
                    'total': item.total
                })

        return pd.DataFrame(data)

    def get_clients_dataframe(self) -> pd.DataFrame:
        """
        Создает DataFrame с данными о клиентах.

        Returns
        -------
        pd.DataFrame
            DataFrame с клиентами
        """
        clients = self.db.get_all_clients()
        data = []

        for client in clients:
            orders = self.db.get_orders_by_client(client.id)
            total_spent = sum(order.total for order in orders)

            data.append({
                'client_id': client.id,
                'client_name': client.name,
                'email': client.email,
                'phone': client.phone,
                'address': client.address,
                'orders_count': len(orders),
                'total_spent': total_spent
            })

        return pd.DataFrame(data)

    def get_products_dataframe(self) -> pd.DataFrame:
        """
        Создает DataFrame с данными о товарах.

        Returns
        -------
        pd.DataFrame
            DataFrame с товарами
        """
        products = self.db.get_all_products()
        data = []

        for product in products:
            # Подсчитываем общее количество проданного товара
            orders = self.db.get_all_orders()
            total_sold = 0
            total_revenue = 0

            for order in orders:
                for item in order.items:
                    if item.product_id == product.id:
                        total_sold += item.quantity
                        total_revenue += item.total

            data.append({
                'product_id': product.id,
                'product_name': product.name,
                'price': product.price,
                'category': product.category,
                'stock': product.stock,
                'total_sold': total_sold,
                'total_revenue': total_revenue
            })

        return pd.DataFrame(data)

    def plot_top_clients(self, top_n: int = 5) -> plt.Figure:
        """
        Создает график топ-N клиентов по количеству заказов.

        Parameters
        ----------
        top_n : int, optional
            Количество клиентов для отображения (по умолчанию 5)

        Returns
        -------
        plt.Figure
            Объект рисунка matplotlib
        """
        clients_df = self.get_clients_dataframe()

        # Сортируем по количеству заказов
        top_clients = clients_df.nlargest(top_n, 'orders_count')

        # Создаем график
        fig, ax = plt.subplots(figsize=(10, 6))
        bars = ax.bar(
            range(len(top_clients)),
            top_clients['orders_count'],
            color=sns.color_palette("husl", len(top_clients))
        )

        # Настраиваем график
        ax.set_title(f'Топ-{top_n} клиентов по количеству заказов', fontsize=16)
        ax.set_xlabel('Клиенты', fontsize=12)
        ax.set_ylabel('Количество заказов', fontsize=12)

        # Добавляем подписи к столбцам
        for i, bar in enumerate(bars):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width() / 2., height + 0.1,
                    f'{int(height)}', ha='center', va='bottom')

        # Устанавливаем подписи по оси X
        client_names = [f'{row.client_name}\n(ID: {row.client_id})' for row in top_clients.itertuples()]
        ax.set_xticks(range(len(top_clients)))
        ax.set_xticklabels(client_names, rotation=45, ha='right')

        plt.tight_layout()
        return fig

    def plot_orders_dynamics(self, days: int = 30) -> plt.Figure:
        """
        Создает график динамики количества заказов по датам.

        Parameters
        ----------
        days : int, optional
            Количество дней для анализа (по умолчанию 30)

        Returns
        -------
        plt.Figure
            Объект рисунка matplotlib
        """
        orders_df = self.get_orders_dataframe()

        if orders_df.empty:
            fig, ax = plt.subplots(figsize=(10, 6))
            ax.text(0.5, 0.5, 'Нет данных для отображения',
                    ha='center', va='center', transform=ax.transAxes, fontsize=14)
            return fig

        # Преобразуем даты и группируем по дням
        orders_df['order_date'] = pd.to_datetime(orders_df['order_date'])
        orders_df['date'] = orders_df['order_date'].dt.date

        # Фильтруем по последним дням
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=days)
        filtered_orders = orders_df[orders_df['date'] >= start_date]

        # Группируем по дате и подсчитываем заказы
        daily_orders = filtered_orders.groupby('date').agg({
            'order_id': 'nunique',
            'total': 'sum'
        }).reset_index()
        daily_orders.columns = ['date', 'orders_count', 'total_revenue']

        # Создаем график с двумя осями Y
        fig, ax1 = plt.subplots(figsize=(12, 6))

        # Первая ось Y: количество заказов
        color = 'tab:blue'
        ax1.set_xlabel('Дата', fontsize=12)
        ax1.set_ylabel('Количество заказов', color=color, fontsize=12)
        ax1.plot(daily_orders['date'], daily_orders['orders_count'],
                 color=color, marker='o', linestyle='-', linewidth=2, markersize=4)
        ax1.tick_params(axis='y', labelcolor=color)

        # Вторая ось Y: выручка
        ax2 = ax1.twinx()
        color = 'tab:red'
        ax2.set_ylabel('Выручка', color=color, fontsize=12)
        ax2.plot(daily_orders['date'], daily_orders['total_revenue'],
                 color=color, marker='s', linestyle='--', linewidth=2, markersize=4)
        ax2.tick_params(axis='y', labelcolor=color)

        # Заголовок и сетка
        ax1.set_title('Динамика заказов и выручки по дням', fontsize=16)
        ax1.grid(True, linestyle='--', alpha=0.7)

        # Форматирование дат на оси X
        fig.autofmt_xdate(rotation=45)

        plt.tight_layout()
        return fig

    def plot_clients_network(self) -> plt.Figure:
        """
        Создает граф связей клиентов по общим товарам.

        Returns
        -------
        plt.Figure
            Объект рисунка matplotlib
        """
        orders_df = self.get_orders_dataframe()

        if orders_df.empty:
            fig, ax = plt.subplots(figsize=(10, 8))
            ax.text(0.5, 0.5, 'Нет данных для отображения',
                    ha='center', va='center', transform=ax.transAxes, fontsize=14)
            return fig

        # Создаем граф
        G = nx.Graph()

        # Добавляем узлы (клиенты)
        clients = orders_df[['client_id', 'client_name']].drop_duplicates()
        for _, row in clients.iterrows():
            G.add_node(row['client_id'], name=row['client_name'])

        # Добавляем ребра между клиентами, которые покупали одинаковые товары
        client_products = orders_df.groupby('client_id')['product_id'].apply(set).to_dict()

        for client1, products1 in client_products.items():
            for client2, products2 in client_products.items():
                if client1 != client2:
                    common_products = products1 & products2
                    if common_products:
                        if G.has_edge(client1, client2):
                            # Увеличиваем вес существующего ребра
                            G[client1][client2]['weight'] += len(common_products)
                        else:
                            # Добавляем новое ребро
                            G.add_edge(client1, client2, weight=len(common_products))

        # Визуализируем граф
        fig, ax = plt.subplots(figsize=(12, 8))

        # Позиционирование узлов
        pos = nx.spring_layout(G, k=1, iterations=50)

        # Рисуем ребра
        edges = G.edges(data=True)
        weights = [edge[2]['weight'] for edge in edges]

        nx.draw_networkx_edges(
            G, pos,
            width=[w * 0.5 for w in weights],
            alpha=0.6,
            edge_color=weights,
            edge_cmap=plt.cm.Blues
        )

        # Рисуем узлы
        node_sizes = [len(list(G.neighbors(node))) * 200 for node in G.nodes()]
        nx.draw_networkx_nodes(
            G, pos,
            node_size=node_sizes,
            node_color='lightblue',
            alpha=0.9
        )

        # Подписываем узлы
        labels = {node: f"{G.nodes[node]['name']}\n(ID: {node})" for node in G.nodes()}
        nx.draw_networkx_labels(G, pos, labels, font_size=8)

        # Добавляем легенду для весов ребер
        from matplotlib.cm import ScalarMappable
        from matplotlib.colors import Normalize

        sm = ScalarMappable(cmap=plt.cm.Blues, norm=Normalize(vmin=min(weights), vmax=max(weights)))
        sm.set_array([])
        cbar = plt.colorbar(sm, ax=ax)
        cbar.set_label('Количество общих товаров')

        ax.set_title('Граф связей клиентов по общим товарам', fontsize=16)
        ax.axis('off')

        plt.tight_layout()
        return fig

    def plot_product_categories(self) -> plt.Figure:
        """
        Создает круговую диаграмму распределения товаров по категориям.

        Returns
        -------
        plt.Figure
            Объект рисунка matplotlib
        """
        products_df = self.get_products_dataframe()

        if products_df.empty:
            fig, ax = plt.subplots(figsize=(8, 8))
            ax.text(0.5, 0.5, 'Нет данных для отображения',
                    ha='center', va='center', transform=ax.transAxes, fontsize=14)
            return fig

        # Группируем по категориям
        category_stats = products_df.groupby('category').agg({
            'product_id': 'count',
            'total_revenue': 'sum'
        }).reset_index()
        category_stats.columns = ['category', 'product_count', 'total_revenue']

        # Создаем круговую диаграмму
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 7))

        # Первая диаграмма: количество товаров по категориям
        ax1.pie(
            category_stats['product_count'],
            labels=category_stats['category'],
            autopct='%1.1f%%',
            startangle=90,
            colors=sns.color_palette("Set3", len(category_stats))
        )
        ax1.set_title('Распределение товаров по категориям', fontsize=14)

        # Вторая диаграмма: выручка по категориям
        ax2.pie(
            category_stats['total_revenue'],
            labels=category_stats['category'],
            autopct='%1.1f%%',
            startangle=90,
            colors=sns.color_palette("Set3", len(category_stats))
        )
        ax2.set_title('Распределение выручки по категориям', fontsize=14)

        plt.tight_layout()
        return fig

    def get_sales_statistics(self) -> Dict[str, float]:
        """
        Рассчитывает основные статистические показатели продаж.

        Returns
        -------
        Dict[str, float]
            Словарь с статистическими показателями
        """
        orders_df = self.get_orders_dataframe()

        if orders_df.empty:
            return {
                'total_orders': 0,
                'total_revenue': 0,
                'avg_order_value': 0,
                'total_clients': 0,
                'avg_orders_per_client': 0
            }

        # Основные показатели
        total_orders = orders_df['order_id'].nunique()
        total_revenue = orders_df['total'].sum()
        avg_order_value = total_revenue / total_orders if total_orders > 0 else 0

        # Показатели по клиентам
        clients_df = self.get_clients_dataframe()
        total_clients = len(clients_df)
        avg_orders_per_client = total_orders / total_clients if total_clients > 0 else 0

        return {
            'total_orders': total_orders,
            'total_revenue': total_revenue,
            'avg_order_value': avg_order_value,
            'total_clients': total_clients,
            'avg_orders_per_client': avg_orders_per_client
        }