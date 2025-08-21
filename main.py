"""
Главный модуль приложения для управления заказами.
Точка входа в программу.
"""

import tkinter as tk
from gui import OrderManagementApp

def main():
    """
    Главная функция, запускающая приложение.
    """
    root = tk.Tk()
    app = OrderManagementApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()