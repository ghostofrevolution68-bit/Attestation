"""
Модуль содержит классы данных для системы управления заказами.
Включает классы Client, Product, Order и OrderItem.
"""

import re
from datetime import datetime
from typing import List, Optional


class BaseModel:
    """Базовый класс для всех моделей данных."""

    def __init__(self, id: Optional[int] = None):
        """
        Инициализирует базовую модель с идентификатором.

        Parameters
        ----------
        id : int, optional
            Уникальный идентификатор объекта (по умолчанию None)
        """
        self.id = id

    def __repr__(self):
        return f"<{self.__class__.__name__} id={self.id}>"


class Client(BaseModel):
    """Класс, представляющий клиента интернет-магазина."""

    def __init__(self, name: str, email: str, phone: str, address: str, id: Optional[int] = None):
        """
        Инициализирует объект клиента.

        Parameters
        ----------
        name : str
            Полное имя клиента
        email : str
            Адрес электронной почты
        phone : str
            Номер телефона
        address : str
            Физический адрес
        id : int, optional
            Уникальный идентификатор клиента (по умолчанию None)

        Raises
        ------
        ValueError
            Если email или телефон не соответствуют формату
        """
        super().__init__(id)
        self.name = name

        if not self.is_valid_email(email):
            raise ValueError("Неверный формат email")
        self.email = email

        if not self.is_valid_phone(phone):
            raise ValueError("Неверный формат телефона")
        self.phone = phone

        self.address = address

    @staticmethod
    def is_valid_email(email: str) -> bool:
        """
        Проверяет валидность email с помощью регулярного выражения.

        Parameters
        ----------
        email : str
            Email для проверки

        Returns
        -------
        bool
            True если email валиден, иначе False
        """
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None

    @staticmethod
    def is_valid_phone(phone: str) -> bool:
        """
        Проверяет валидность номера телефона с помощью регулярного выражения.

        Parameters
        ----------
        phone : str
            Номер телефона для проверки

        Returns
        -------
        bool
            True если номер валиден, иначе False
        """
        pattern = r'^(\+7|8)[\s-]?\(?\d{3}\)?[\s-]?\d{3}[\s-]?\d{2}[\s-]?\d{2}$'
        return re.match(pattern, phone) is not None

    def to_dict(self) -> dict:
        """
        Преобразует объект клиента в словарь.

        Returns
        -------
        dict
            Словарь с данными клиента
        """
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'phone': self.phone,
            'address': self.address
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Client':
        """
        Создает объект клиента из словаря.

        Parameters
        ----------
        data : dict
            Словарь с данными клиента

        Returns
        -------
        Client
            Объект клиента
        """
        return cls(
            id=data.get('id'),
            name=data['name'],
            email=data['email'],
            phone=data['phone'],
            address=data['address']
        )

    def __repr__(self):
        return f"<Client id={self.id} name='{self.name}'>"


class Product(BaseModel):
    """Класс, представляющий товар в интернет-магазине."""

    def __init__(self, name: str, price: float, category: str, stock: int, id: Optional[int] = None):
        """
        Инициализирует объект товара.

        Parameters
        ----------
        name : str
            Название товара
        price : float
            Цена товара
        category : str
            Категория товара
        stock : int
            Количество товара на складе
        id : int, optional
            Уникальный идентификатор товара (по умолчанию None)
        """
        super().__init__(id)
        self.name = name
        self.price = price
        self.category = category
        self.stock = stock

    def to_dict(self) -> dict:
        """
        Преобразует объект товара в словарь.

        Returns
        -------
        dict
            Словарь с данными товара
        """
        return {
            'id': self.id,
            'name': self.name,
            'price': self.price,
            'category': self.category,
            'stock': self.stock
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Product':
        """
        Создает объект товара из словаря.

        Parameters
        ----------
        data : dict
            Словарь с данными товара

        Returns
        -------
        Product
            Объект товара
        """
        return cls(
            id=data.get('id'),
            name=data['name'],
            price=data['price'],
            category=data['category'],
            stock=data['stock']
        )

    def __repr__(self):
        return f"<Product id={self.id} name='{self.name}' price={self.price}>"


class OrderItem:
    """Класс, представляющий позицию в заказе."""

    def __init__(self, product_id: int, quantity: int, price: float):
        """
        Инициализирует объект позиции заказа.

        Parameters
        ----------
        product_id : int
            Идентификатор товара
        quantity : int
            Количество товара
        price : float
            Цена за единицу на момент заказа
        """
        self.product_id = product_id
        self.quantity = quantity
        self.price = price
        self.total = quantity * price

    def to_dict(self) -> dict:
        """
        Преобразует объект позиции заказа в словарь.

        Returns
        -------
        dict
            Словарь с данными позиции заказа
        """
        return {
            'product_id': self.product_id,
            'quantity': self.quantity,
            'price': self.price,
            'total': self.total
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'OrderItem':
        """
        Создает объект позиции заказа из словаря.

        Parameters
        ----------
        data : dict
            Словарь с данными позиции заказа

        Returns
        -------
        OrderItem
            Объект позиции заказа
        """
        return cls(
            product_id=data['product_id'],
            quantity=data['quantity'],
            price=data['price']
        )

    def __repr__(self):
        return f"<OrderItem product_id={self.product_id} quantity={self.quantity} total={self.total}>"


class Order(BaseModel):
    """Класс, представляющий заказ в интернет-магазине."""

    def __init__(self, client_id: int, items: List[OrderItem],
                 order_date: Optional[datetime] = None, id: Optional[int] = None):
        """
        Инициализирует объект заказа.

        Parameters
        ----------
        client_id : int
            Идентификатор клиента
        items : List[OrderItem]
            Список позиций заказа
        order_date : datetime, optional
            Дата заказа (по умолчанию текущая дата)
        id : int, optional
            Уникальный идентификатор заказа (по умолчанию None)
        """
        super().__init__(id)
        self.client_id = client_id
        self.items = items
        self.order_date = order_date or datetime.now()
        self.total = sum(item.total for item in items)

    def add_item(self, item: OrderItem):
        """
        Добавляет позицию в заказ.

        Parameters
        ----------
        item : OrderItem
            Позиция заказа для добавления
        """
        self.items.append(item)
        self.total += item.total

    def remove_item(self, product_id: int):
        """
        Удаляет позицию из заказа по идентификатору товара.

        Parameters
        ----------
        product_id : int
            Идентификатор товара для удаления

        Returns
        -------
        bool
            True если позиция была удалена, иначе False
        """
        for i, item in enumerate(self.items):
            if item.product_id == product_id:
                self.total -= item.total
                del self.items[i]
                return True
        return False

    def to_dict(self) -> dict:
        """
        Преобразует объект заказа в словарь.

        Returns
        -------
        dict
            Словарь с данными заказа
        """
        return {
            'id': self.id,
            'client_id': self.client_id,
            'order_date': self.order_date.isoformat(),
            'items': [item.to_dict() for item in self.items],
            'total': self.total
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Order':
        """
        Создает объект заказа из словаря.

        Parameters
        ----------
        data : dict
            Словарь с данными заказа

        Returns
        -------
        Order
            Объект заказа
        """
        items = [OrderItem.from_dict(item) for item in data['items']]
        order_date = datetime.fromisoformat(data['order_date']) if 'order_date' in data else None
        return cls(
            id=data.get('id'),
            client_id=data['client_id'],
            items=items,
            order_date=order_date
        )

    def __repr__(self):
        return f"<Order id={self.id} client_id={self.client_id} total={self.total}>"