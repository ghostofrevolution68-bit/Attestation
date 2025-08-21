"""
Модуль графического интерфейса для системы управления заказами.
Реализован с использованием tkinter.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from typing import List, Optional
from datetime import datetime

from models import Client, Product, Order, OrderItem
from db import Database
from analysis import DataAnalyzer


class OrderManagementApp:
    """Главное приложение для управления заказами."""

    def __init__(self, root):
        """
        Инициализирует главное окно приложения.

        Parameters
        ----------
        root : tk.Tk
            Корневой элемент tkinter
        """
        self.root = root
        self.root.title("Система управления заказами")
        self.root.geometry("1000x600")

        # Инициализация базы данных
        self.db = Database()

        # Инициализация анализатора данных
        self.analyzer = DataAnalyzer(self.db)

        # Создание вкладок
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Создание вкладок интерфейса
        self.create_clients_tab()
        self.create_products_tab()
        self.create_orders_tab()
        self.create_analysis_tab()

        # Загрузка данных
        self.load_clients()
        self.load_products()
        self.load_orders()

    def create_clients_tab(self):
        """Создает вкладку для управления клиентами."""
        self.clients_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.clients_tab, text="Клиенты")

        # Панель управления
        control_frame = ttk.Frame(self.clients_tab)
        control_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Button(control_frame, text="Добавить", command=self.add_client).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="Редактировать", command=self.edit_client).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="Удалить", command=self.delete_client).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="Обновить", command=self.load_clients).pack(side=tk.LEFT, padx=5)

        # Поиск
        search_frame = ttk.Frame(control_frame)
        search_frame.pack(side=tk.RIGHT, padx=5)

        ttk.Label(search_frame, text="Поиск:").pack(side=tk.LEFT)
        self.client_search_var = tk.StringVar()
        self.client_search_var.trace("w", self.search_clients)
        ttk.Entry(search_frame, textvariable=self.client_search_var).pack(side=tk.LEFT, padx=5)

        # Таблица клиентов
        columns = ("id", "name", "email", "phone", "address")
        self.clients_tree = ttk.Treeview(self.clients_tab, columns=columns, show="headings")

        # Настройка колонок
        self.clients_tree.heading("id", text="ID")
        self.clients_tree.heading("name", text="Имя")
        self.clients_tree.heading("email", text="Email")
        self.clients_tree.heading("phone", text="Телефон")
        self.clients_tree.heading("address", text="Адрес")

        self.clients_tree.column("id", width=50)
        self.clients_tree.column("name", width=150)
        self.clients_tree.column("email", width=150)
        self.clients_tree.column("phone", width=120)
        self.clients_tree.column("address", width=200)

        # Scrollbar
        scrollbar = ttk.Scrollbar(self.clients_tab, orient=tk.VERTICAL, command=self.clients_tree.yview)
        self.clients_tree.configure(yscrollcommand=scrollbar.set)

        self.clients_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=5)

    def create_products_tab(self):
        """Создает вкладку для управления товарами."""
        self.products_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.products_tab, text="Товары")

        # Панель управления
        control_frame = ttk.Frame(self.products_tab)
        control_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Button(control_frame, text="Добавить", command=self.add_product).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="Редактировать", command=self.edit_product).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="Удалить", command=self.delete_product).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="Обновить", command=self.load_products).pack(side=tk.LEFT, padx=5)

        # Поиск
        search_frame = ttk.Frame(control_frame)
        search_frame.pack(side=tk.RIGHT, padx=5)

        ttk.Label(search_frame, text="Поиск:").pack(side=tk.LEFT)
        self.product_search_var = tk.StringVar()
        self.product_search_var.trace("w", self.search_products)
        ttk.Entry(search_frame, textvariable=self.product_search_var).pack(side=tk.LEFT, padx=5)

        # Таблица товаров
        columns = ("id", "name", "price", "category", "stock")
        self.products_tree = ttk.Treeview(self.products_tab, columns=columns, show="headings")

        # Настройка колонок
        self.products_tree.heading("id", text="ID")
        self.products_tree.heading("name", text="Название")
        self.products_tree.heading("price", text="Цена")
        self.products_tree.heading("category", text="Категория")
        self.products_tree.heading("stock", text="На складе")

        self.products_tree.column("id", width=50)
        self.products_tree.column("name", width=150)
        self.products_tree.column("price", width=80)
        self.products_tree.column("category", width=100)
        self.products_tree.column("stock", width=80)

        # Scrollbar
        scrollbar = ttk.Scrollbar(self.products_tab, orient=tk.VERTICAL, command=self.products_tree.yview)
        self.products_tree.configure(yscrollcommand=scrollbar.set)

        self.products_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=5)

    def create_orders_tab(self):
        """Создает вкладку для управления заказами."""
        self.orders_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.orders_tab, text="Заказы")

        # Панель управления
        control_frame = ttk.Frame(self.orders_tab)
        control_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Button(control_frame, text="Добавить", command=self.add_order).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="Просмотреть", command=self.view_order).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="Удалить", command=self.delete_order).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="Обновить", command=self.load_orders).pack(side=tk.LEFT, padx=5)

        # Экспорт/Импорт
        import_export_frame = ttk.Frame(control_frame)
        import_export_frame.pack(side=tk.RIGHT, padx=5)

        ttk.Button(import_export_frame, text="Экспорт JSON",
                   command=lambda: self.export_data('json')).pack(side=tk.LEFT, padx=2)
        ttk.Button(import_export_frame, text="Импорт JSON",
                   command=lambda: self.import_data('json')).pack(side=tk.LEFT, padx=2)
        ttk.Button(import_export_frame, text="Экспорт CSV",
                   command=lambda: self.export_data('csv')).pack(side=tk.LEFT, padx=2)

        # Таблица заказов
        columns = ("id", "client_id", "client_name", "order_date", "total")
        self.orders_tree = ttk.Treeview(self.orders_tab, columns=columns, show="headings")

        # Настройка колонок
        self.orders_tree.heading("id", text="ID")
        self.orders_tree.heading("client_id", text="ID клиента")
        self.orders_tree.heading("client_name", text="Имя клиента")
        self.orders_tree.heading("order_date", text="Дата заказа")
        self.orders_tree.heading("total", text="Сумма")

        self.orders_tree.column("id", width=50)
        self.orders_tree.column("client_id", width=80)
        self.orders_tree.column("client_name", width=150)
        self.orders_tree.column("order_date", width=120)
        self.orders_tree.column("total", width=100)

        # Scrollbar
        scrollbar = ttk.Scrollbar(self.orders_tab, orient=tk.VERTICAL, command=self.orders_tree.yview)
        self.orders_tree.configure(yscrollcommand=scrollbar.set)

        self.orders_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=5)

    def create_analysis_tab(self):
        """Создает вкладку для анализа данных."""
        self.analysis_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.analysis_tab, text="Аналитика")

        # Панель управления
        control_frame = ttk.Frame(self.analysis_tab)
        control_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Button(control_frame, text="Топ клиентов",
                   command=self.show_top_clients).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="Динамика заказов",
                   command=self.show_orders_dynamics).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="Граф связей",
                   command=self.show_connections_graph).pack(side=tk.LEFT, padx=5)

        # Область для отображения графиков
        self.analysis_frame = ttk.Frame(self.analysis_tab)
        self.analysis_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

    def load_clients(self):
        """Загружает клиентов из базы данных и отображает их в таблице."""
        # Очищаем таблицу
        for item in self.clients_tree.get_children():
            self.clients_tree.delete(item)

        # Загружаем клиентов
        clients = self.db.get_all_clients()

        # Добавляем клиентов в таблицу
        for client in clients:
            self.clients_tree.insert("", tk.END, values=(
                client.id, client.name, client.email, client.phone, client.address
            ))

    def load_products(self):
        """Загружает товары из базы данных и отображает их в таблице."""
        # Очищаем таблицу
        for item in self.products_tree.get_children():
            self.products_tree.delete(item)

        # Загружаем товары
        products = self.db.get_all_products()

        # Добавляем товары в таблицу
        for product in products:
            self.products_tree.insert("", tk.END, values=(
                product.id, product.name, product.price, product.category, product.stock
            ))

    def load_orders(self):
        """Загружает заказы из базы данных и отображает их в таблице."""
        # Очищаем таблицу
        for item in self.orders_tree.get_children():
            self.orders_tree.delete(item)

        # Загружаем заказы
        orders = self.db.get_all_orders()

        # Добавляем заказы в таблицу
        for order in orders:
            client = self.db.get_client(order.client_id)
            client_name = client.name if client else "Неизвестный клиент"

            self.orders_tree.insert("", tk.END, values=(
                order.id, order.client_id, client_name,
                order.order_date.strftime("%Y-%m-%d %H:%M"), order.total
            ))

    def search_clients(self, *args):
        """Выполняет поиск клиентов по введенному запросу."""
        query = self.client_search_var.get().lower()

        # Очищаем таблицу
        for item in self.clients_tree.get_children():
            self.clients_tree.delete(item)

        # Загружаем клиентов
        clients = self.db.get_all_clients()

        # Фильтруем клиентов по запросу
        for client in clients:
            if (query in client.name.lower() or
                    query in client.email.lower() or
                    query in client.phone.lower() or
                    query in client.address.lower()):
                self.clients_tree.insert("", tk.END, values=(
                    client.id, client.name, client.email, client.phone, client.address
                ))

    def search_products(self, *args):
        """Выполняет поиск товаров по введенному запросу."""
        query = self.product_search_var.get().lower()

        # Очищаем таблицу
        for item in self.products_tree.get_children():
            self.products_tree.delete(item)

        # Загружаем товары
        products = self.db.get_all_products()

        # Фильтруем товары по запросу
        for product in products:
            if (query in product.name.lower() or
                    query in product.category.lower() or
                    str(product.price).startswith(query) or
                    str(product.stock).startswith(query)):
                self.products_tree.insert("", tk.END, values=(
                    product.id, product.name, product.price, product.category, product.stock
                ))

    def add_client(self):
        """Открывает диалог добавления нового клиента."""
        dialog = ClientDialog(self.root, self.db, None)
        self.root.wait_window(dialog.dialog)
        self.load_clients()

    def edit_client(self):
        """Открывает диалог редактирования выбранного клиента."""
        selection = self.clients_tree.selection()
        if not selection:
            messagebox.showwarning("Предупреждение", "Выберите клиента для редактирования")
            return

        item = self.clients_tree.item(selection[0])
        client_id = item['values'][0]

        client = self.db.get_client(client_id)
        if client:
            dialog = ClientDialog(self.root, self.db, client)
            self.root.wait_window(dialog.dialog)
            self.load_clients()

    def delete_client(self):
        """Удаляет выбранного клиента."""
        selection = self.clients_tree.selection()
        if not selection:
            messagebox.showwarning("Предупреждение", "Выберите клиента для удаления")
            return

        item = self.clients_tree.item(selection[0])
        client_id = item['values'][0]

        if messagebox.askyesno("Подтверждение", "Вы уверены, что хотите удалить этого клиента?"):
            if self.db.delete_client(client_id):
                messagebox.showinfo("Успех", "Клиент успешно удален")
                self.load_clients()
            else:
                messagebox.showerror("Ошибка", "Не удалось удалить клиента")

    def add_product(self):
        """Открывает диалог добавления нового товара."""
        dialog = ProductDialog(self.root, self.db, None)
        self.root.wait_window(dialog.dialog)
        self.load_products()

    def edit_product(self):
        """Открывает диалог редактирования выбранного товара."""
        selection = self.products_tree.selection()
        if not selection:
            messagebox.showwarning("Предупреждение", "Выберите товар для редактирования")
            return

        item = self.products_tree.item(selection[0])
        product_id = item['values'][0]

        product = self.db.get_product(product_id)
        if product:
            dialog = ProductDialog(self.root, self.db, product)
            self.root.wait_window(dialog.dialog)
            self.load_products()

    def delete_product(self):
        """Удаляет выбранный товар."""
        selection = self.products_tree.selection()
        if not selection:
            messagebox.showwarning("Предупреждение", "Выберите товар для удаления")
            return

        item = self.products_tree.item(selection[0])
        product_id = item['values'][0]

        if messagebox.askyesno("Подтверждение", "Вы уверены, что хотите удалить этот товар?"):
            if self.db.delete_product(product_id):
                messagebox.showinfo("Успех", "Товар успешно удален")
                self.load_products()
            else:
                messagebox.showerror("Ошибка", "Не удалось удалить товар")

    def add_order(self):
        """Открывает диалог добавления нового заказа."""
        dialog = OrderDialog(self.root, self.db, None)
        self.root.wait_window(dialog.dialog)
        self.load_orders()

    def view_order(self):
        """Открывает диалог просмотра выбранного заказа."""
        selection = self.orders_tree.selection()
        if not selection:
            messagebox.showwarning("Предупреждение", "Выберите заказ для просмотра")
            return

        item = self.orders_tree.item(selection[0])
        order_id = item['values'][0]

        order = self.db.get_order(order_id)
        if order:
            dialog = OrderDialog(self.root, self.db, order)
            self.root.wait_window(dialog.dialog)

    def delete_order(self):
        """Удаляет выбранный заказ."""
        selection = self.orders_tree.selection()
        if not selection:
            messagebox.showwarning("Предупреждение", "Выберите заказ для удаления")
            return

        item = self.orders_tree.item(selection[0])
        order_id = item['values'][0]

        if messagebox.askyesno("Подтверждение", "Вы уверены, что хотите удалить этот заказ?"):
            if self.db.delete_order(order_id):
                messagebox.showinfo("Успех", "Заказ успешно удален")
                self.load_orders()
            else:
                messagebox.showerror("Ошибка", "Не удалось удалить заказ")

    def export_data(self, format_type: str):
        """Экспортирует данные в выбранном формате."""
        try:
            if format_type == 'json':
                filename = filedialog.asksaveasfilename(
                    defaultextension=".json",
                    filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
                )
                if filename:
                    self.db.export_to_json(filename)
                    messagebox.showinfo("Успех", f"Данные экспортированы в {filename}")

            elif format_type == 'csv':
                # Спросим, какие данные экспортировать
                choice = messagebox.askquestion(
                    "Экспорт CSV",
                    "Экспортировать клиентов? (Нет - товары)"
                )

                entity_type = 'clients' if choice == 'yes' else 'products'
                filename = filedialog.asksaveasfilename(
                    defaultextension=".csv",
                    filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
                )
                if filename:
                    self.db.export_to_csv(entity_type, filename)
                    messagebox.showinfo("Успех", f"Данные экспортированы в {filename}")

        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось экспортировать данные: {e}")

    def import_data(self, format_type: str):
        """Импортирует данные из выбранного формата."""
        try:
            if format_type == 'json':
                filename = filedialog.askopenfilename(
                    filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
                )
                if filename:
                    self.db.import_from_json(filename)
                    messagebox.showinfo("Успех", f"Данные импортированы из {filename}")
                    # Обновляем все вкладки
                    self.load_clients()
                    self.load_products()
                    self.load_orders()

        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось импортировать данные: {e}")

    def show_top_clients(self):
        """Показывает график топ-5 клиентов по количеству заказов."""
        try:
            # Очищаем область анализа
            for widget in self.analysis_frame.winfo_children():
                widget.destroy()

            # Создаем график
            fig = self.analyzer.plot_top_clients()

            # Встраиваем график в интерфейс
            from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
            canvas = FigureCanvasTkAgg(fig, self.analysis_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось создать график: {e}")

    def show_orders_dynamics(self):
        """Показывает график динамики заказов по датам."""
        try:
            # Очищаем область анализа
            for widget in self.analysis_frame.winfo_children():
                widget.destroy()

            # Создаем график
            fig = self.analyzer.plot_orders_dynamics()

            # Встраиваем график в интерфейс
            from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
            canvas = FigureCanvasTkAgg(fig, self.analysis_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось создать график: {e}")

    def show_connections_graph(self):
        """Показывает граф связей клиентов."""
        try:
            # Очищаем область анализа
            for widget in self.analysis_frame.winfo_children():
                widget.destroy()

            # Создаем граф
            fig = self.analyzer.plot_clients_network()

            # Встраиваем граф в интерфейс
            from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
            canvas = FigureCanvasTkAgg(fig, self.analysis_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось создать граф: {e}")


class ClientDialog:
    """Диалог для добавления/редактирования клиента."""

    def __init__(self, parent, db, client: Optional[Client] = None):
        """
        Инициализирует диалог клиента.

        Parameters
        ----------
        parent : tk.Widget
            Родительский виджет
        db : Database
            Объект базы данных
        client : Client, optional
            Объект клиента для редактирования (по умолчанию None - добавление)
        """
        self.db = db
        self.client = client

        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Редактирование клиента" if client else "Добавление клиента")
        self.dialog.geometry("400x300")
        self.dialog.transient(parent)
        self.dialog.grab_set()

        # Поля формы
        ttk.Label(self.dialog, text="Имя:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.name_var = tk.StringVar()
        ttk.Entry(self.dialog, textvariable=self.name_var, width=30).grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(self.dialog, text="Email:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        self.email_var = tk.StringVar()
        ttk.Entry(self.dialog, textvariable=self.email_var, width=30).grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(self.dialog, text="Телефон:").grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
        self.phone_var = tk.StringVar()
        ttk.Entry(self.dialog, textvariable=self.phone_var, width=30).grid(row=2, column=1, padx=5, pady=5)

        ttk.Label(self.dialog, text="Адрес:").grid(row=3, column=0, padx=5, pady=5, sticky=tk.W)
        self.address_var = tk.StringVar()
        ttk.Entry(self.dialog, textvariable=self.address_var, width=30).grid(row=3, column=1, padx=5, pady=5)

        # Кнопки
        button_frame = ttk.Frame(self.dialog)
        button_frame.grid(row=4, column=0, columnspan=2, pady=10)

        ttk.Button(button_frame, text="Сохранить", command=self.save).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Отмена", command=self.dialog.destroy).pack(side=tk.LEFT, padx=5)

        # Если редактирование, заполняем поля
        if client:
            self.name_var.set(client.name)
            self.email_var.set(client.email)
            self.phone_var.set(client.phone)
            self.address_var.set(client.address)

    def save(self):
        """Сохраняет клиента в базу данных."""
        try:
            name = self.name_var.get().strip()
            email = self.email_var.get().strip()
            phone = self.phone_var.get().strip()
            address = self.address_var.get().strip()

            # Валидация
            if not all([name, email, phone, address]):
                messagebox.showerror("Ошибка", "Все поля должны быть заполнены")
                return

            # Проверка email
            if not Client.is_valid_email(email):
                messagebox.showerror("Ошибка", "Неверный формат email")
                return

            # Проверка телефона
            if not Client.is_valid_phone(phone):
                messagebox.showerror("Ошибка", "Неверный формат телефона")
                return

            # Сохранение
            if self.client:
                # Редактирование
                self.client.name = name
                self.client.email = email
                self.client.phone = phone
                self.client.address = address
                if self.db.update_client(self.client):
                    messagebox.showinfo("Успех", "Клиент успешно обновлен")
                    self.dialog.destroy()
                else:
                    messagebox.showerror("Ошибка", "Не удалось обновить клиента")
            else:
                # Добавление
                client = Client(name=name, email=email, phone=phone, address=address)
                client_id = self.db.add_client(client)
                if client_id:
                    messagebox.showinfo("Успех", f"Клиент успешно добавлен с ID {client_id}")
                    self.dialog.destroy()
                else:
                    messagebox.showerror("Ошибка", "Не удалось добавить клиента")

        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить клиента: {e}")


class ProductDialog:
    """Диалог для добавления/редактирования товара."""

    def __init__(self, parent, db, product: Optional[Product] = None):
        """
        Инициализирует диалог товара.

        Parameters
        ----------
        parent : tk.Widget
            Родительский виджет
        db : Database
            Объект базы данных
        product : Product, optional
            Объект товара для редактирования (по умолчанию None - добавление)
        """
        self.db = db
        self.product = product

        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Редактирование товара" if product else "Добавление товара")
        self.dialog.geometry("400x250")
        self.dialog.transient(parent)
        self.dialog.grab_set()

        # Поля формы
        ttk.Label(self.dialog, text="Название:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.name_var = tk.StringVar()
        ttk.Entry(self.dialog, textvariable=self.name_var, width=30).grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(self.dialog, text="Цена:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        self.price_var = tk.DoubleVar()
        ttk.Entry(self.dialog, textvariable=self.price_var, width=30).grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(self.dialog, text="Категория:").grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
        self.category_var = tk.StringVar()
        ttk.Entry(self.dialog, textvariable=self.category_var, width=30).grid(row=2, column=1, padx=5, pady=5)

        ttk.Label(self.dialog, text="Количество:").grid(row=3, column=0, padx=5, pady=5, sticky=tk.W)
        self.stock_var = tk.IntVar()
        ttk.Entry(self.dialog, textvariable=self.stock_var, width=30).grid(row=3, column=1, padx=5, pady=5)

        # Кнопки
        button_frame = ttk.Frame(self.dialog)
        button_frame.grid(row=4, column=0, columnspan=2, pady=10)

        ttk.Button(button_frame, text="Сохранить", command=self.save).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Отмена", command=self.dialog.destroy).pack(side=tk.LEFT, padx=5)

        # Если редактирование, заполняем поля
        if product:
            self.name_var.set(product.name)
            self.price_var.set(product.price)
            self.category_var.set(product.category)
            self.stock_var.set(product.stock)

    def save(self):
        """Сохраняет товар в базу данных."""
        try:
            name = self.name_var.get().strip()
            price = self.price_var.get()
            category = self.category_var.get().strip()
            stock = self.stock_var.get()

            # Валидация
            if not all([name, category]) or price <= 0 or stock < 0:
                messagebox.showerror("Ошибка", "Все поля должны быть заполнены корректно")
                return

            # Сохранение
            if self.product:
                # Редактирование
                self.product.name = name
                self.product.price = price
                self.product.category = category
                self.product.stock = stock
                if self.db.update_product(self.product):
                    messagebox.showinfo("Успех", "Товар успешно обновлен")
                    self.dialog.destroy()
                else:
                    messagebox.showerror("Ошибка", "Не удалось обновить товар")
            else:
                # Добавление
                product = Product(name=name, price=price, category=category, stock=stock)
                product_id = self.db.add_product(product)
                if product_id:
                    messagebox.showinfo("Успех", f"Товар успешно добавлен с ID {product_id}")
                    self.dialog.destroy()
                else:
                    messagebox.showerror("Ошибка", "Не удалось добавить товар")

        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить товар: {e}")


class OrderDialog:
    """Диалог для добавления/редактирования заказа."""

    def __init__(self, parent, db, order: Optional[Order] = None):
        """
        Инициализирует диалог заказа.

        Parameters
        ----------
        parent : tk.Widget
            Родительский виджет
        db : Database
            Объект базы данных
        order : Order, optional
            Объект заказа для редактирования (по умолчанию None - добавление)
        """
        self.db = db
        self.order = order
        self.client = None
        self.items = []

        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Просмотр заказа" if order else "Добавление заказа")
        self.dialog.geometry("600x500")
        self.dialog.transient(parent)
        self.dialog.grab_set()

        # Если просмотр заказа, заполняем данные
        if order:
            self.client = self.db.get_client(order.client_id)
            self.items = order.items

        # Клиент
        client_frame = ttk.LabelFrame(self.dialog, text="Клиент")
        client_frame.pack(fill=tk.X, padx=5, pady=5)

        if order and self.client:
            ttk.Label(client_frame, text=f"ID: {self.client.id}").pack(anchor=tk.W, padx=5, pady=2)
            ttk.Label(client_frame, text=f"Имя: {self.client.name}").pack(anchor=tk.W, padx=5, pady=2)
            ttk.Label(client_frame, text=f"Email: {self.client.email}").pack(anchor=tk.W, padx=5, pady=2)
            ttk.Label(client_frame, text=f"Телефон: {self.client.phone}").pack(anchor=tk.W, padx=5, pady=2)
        else:
            # Выбор клиента
            ttk.Label(client_frame, text="Выберите клиента:").pack(anchor=tk.W, padx=5, pady=2)

            self.client_var = tk.StringVar()
            clients = self.db.get_all_clients()
            client_names = [f"{c.id}: {c.name}" for c in clients]

            client_combo = ttk.Combobox(client_frame, textvariable=self.client_var, values=client_names,
                                        state="readonly")
            client_combo.pack(fill=tk.X, padx=5, pady=2)

        # Товары
        items_frame = ttk.LabelFrame(self.dialog, text="Товары в заказе")
        items_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Таблица товаров
        columns = ("product_id", "name", "quantity", "price", "total")
        self.items_tree = ttk.Treeview(items_frame, columns=columns, show="headings")

        # Настройка колонок
        self.items_tree.heading("product_id", text="ID товара")
        self.items_tree.heading("name", text="Название")
        self.items_tree.heading("quantity", text="Количество")
        self.items_tree.heading("price", text="Цена")
        self.items_tree.heading("total", text="Сумма")

        self.items_tree.column("product_id", width=80)
        self.items_tree.column("name", width=150)
        self.items_tree.column("quantity", width=80)
        self.items_tree.column("price", width=80)
        self.items_tree.column("total", width=80)

        # Scrollbar
        scrollbar = ttk.Scrollbar(items_frame, orient=tk.VERTICAL, command=self.items_tree.yview)
        self.items_tree.configure(yscrollcommand=scrollbar.set)

        self.items_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=5)

        # Если не только просмотр, добавляем кнопки управления
        if not order:
            items_control_frame = ttk.Frame(items_frame)
            items_control_frame.pack(fill=tk.X, padx=5, pady=5)

            ttk.Button(items_control_frame, text="Добавить товар", command=self.add_item).pack(side=tk.LEFT, padx=5)
            ttk.Button(items_control_frame, text="Удалить товар", command=self.remove_item).pack(side=tk.LEFT, padx=5)

        # Итоговая сумма
        total_frame = ttk.Frame(self.dialog)
        total_frame.pack(fill=tk.X, padx=5, pady=5)

        self.total_var = tk.DoubleVar(value=0.0)
        ttk.Label(total_frame, text="Итоговая сумма:").pack(side=tk.LEFT, padx=5)
        ttk.Label(total_frame, textvariable=self.total_var).pack(side=tk.LEFT, padx=5)

        # Кнопки
        button_frame = ttk.Frame(self.dialog)
        button_frame.pack(fill=tk.X, padx=5, pady=10)

        if not order:
            ttk.Button(button_frame, text="Сохранить", command=self.save).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Закрыть", command=self.dialog.destroy).pack(side=tk.LEFT, padx=5)

        # Заполняем таблицу товаров, если это просмотр
        if order:
            self.load_items()

    def load_items(self):
        """Загружает товары заказа в таблицу."""
        for item in self.items:
            product = self.db.get_product(item.product_id)
            product_name = product.name if product else "Неизвестный товар"

            self.items_tree.insert("", tk.END, values=(
                item.product_id, product_name, item.quantity, item.price, item.total
            ))

        self.total_var.set(sum(item.total for item in self.items))

    def add_item(self):
        """Добавляет товар в заказ."""
        # Диалог выбора товара и количества
        dialog = tk.Toplevel(self.dialog)
        dialog.title("Добавление товара")
        dialog.geometry("300x200")
        dialog.transient(self.dialog)
        dialog.grab_set()

        # Выбор товара
        ttk.Label(dialog, text="Товар:").pack(padx=5, pady=5)

        self.product_var = tk.StringVar()
        products = self.db.get_all_products()
        product_names = [f"{p.id}: {p.name} (${p.price})" for p in products]

        product_combo = ttk.Combobox(dialog, textvariable=self.product_var, values=product_names, state="readonly")
        product_combo.pack(fill=tk.X, padx=5, pady=5)

        # Количество
        ttk.Label(dialog, text="Количество:").pack(padx=5, pady=5)

        self.quantity_var = tk.IntVar(value=1)
        ttk.Spinbox(dialog, from_=1, to=100, textvariable=self.quantity_var).pack(fill=tk.X, padx=5, pady=5)

        # Кнопки
        button_frame = ttk.Frame(dialog)
        button_frame.pack(fill=tk.X, padx=5, pady=10)

        ttk.Button(button_frame, text="Добавить", command=lambda: self.add_item_callback(dialog)).pack(side=tk.LEFT,
                                                                                                       padx=5)
        ttk.Button(button_frame, text="Отмена", command=dialog.destroy).pack(side=tk.LEFT, padx=5)

    def add_item_callback(self, dialog):
        """Обработчик добавления товара."""
        try:
            product_str = self.product_var.get()
            if not product_str:
                messagebox.showerror("Ошибка", "Выберите товар")
                return

            # Извлекаем ID товара
            product_id = int(product_str.split(":")[0])
            quantity = self.quantity_var.get()

            # Получаем товар
            product = self.db.get_product(product_id)
            if not product:
                messagebox.showerror("Ошибка", "Товар не найден")
                return

            # Проверяем наличие на складе
            if quantity > product.stock:
                messagebox.showerror("Ошибка", f"Недостаточно товара на складе. Доступно: {product.stock}")
                return

            # Добавляем товар в заказ
            item = OrderItem(product_id=product_id, quantity=quantity, price=product.price)
            self.items.append(item)

            # Добавляем в таблицу
            self.items_tree.insert("", tk.END, values=(
                product_id, product.name, quantity, product.price, item.total
            ))

            # Обновляем итоговую сумму
            self.total_var.set(self.total_var.get() + item.total)

            dialog.destroy()

        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось добавить товар: {e}")

    def remove_item(self):
        """Удаляет товар из заказа."""
        selection = self.items_tree.selection()
        if not selection:
            messagebox.showwarning("Предупреждение", "Выберите товар для удаления")
            return

        item = self.items_tree.item(selection[0])
        product_id = item['values'][0]

        # Находим и удаляем товар из списка
        for i, item in enumerate(self.items):
            if item.product_id == product_id:
                # Обновляем итоговую сумму
                self.total_var.set(self.total_var.get() - item.total)

                # Удаляем из списка и таблицы
                del self.items[i]
                self.items_tree.delete(selection[0])
                break

    def save(self):
        """Сохраняет заказ в базу данных."""
        try:
            # Проверяем, выбран ли клиент
            if not hasattr(self, 'client_var') or not self.client_var.get():
                messagebox.showerror("Ошибка", "Выберите клиента")
                return

            # Извлекаем ID клиента
            client_str = self.client_var.get()
            client_id = int(client_str.split(":")[0])

            # Проверяем, есть ли товары в заказе
            if not self.items:
                messagebox.showerror("Ошибка", "Добавьте хотя бы один товар в заказ")
                return

            # Создаем заказ
            order = Order(client_id=client_id, items=self.items)

            # Сохраняем в базу
            order_id = self.db.add_order(order)
            if order_id:
                messagebox.showinfo("Успех", f"Заказ успешно создан с ID {order_id}")
                self.dialog.destroy()
            else:
                messagebox.showerror("Ошибка", "Не удалось создать заказ")

        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить заказ: {e}")