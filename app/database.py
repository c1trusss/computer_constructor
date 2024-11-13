import json
import sqlite3


class Database:

    def __init__(self, db_name):
        self.db_name = db_name
        self.connection = sqlite3.connect(self.db_name)

    def execute(self, query):
        cursor = self.connection.cursor()
        cursor.execute(query)

    def __del__(self):
        self.connection.close()


class JsonDatabase:

    def __init__(self):
        with open("computers.json", "r", encoding="utf-8") as f:
            self.data = json.load(f)

    def add_computer(self, user, **kwargs):
        """

        :param user: айди пользователя в базе данных
        :param kwargs:
        cpu - процессор
        cpu_cooler - кулер для процессора
        gpu - видеокарта
        mb - материнская плата
        ram - оперативная память
        disk - устройство памяти
        power - блок питания
        core - корпус
        """

        new_id = max(map(int, self.data.keys())) + 1

        computer = {
            "user": user,
            "cpu": kwargs.get("cpu"),
            "cpu_cooler": kwargs.get("cpu_cooler"),
            "gpu": kwargs.get("gpu"),
            "mb": kwargs.get("mb"),
            "ram": kwargs.get("ram"),
            "disk": kwargs.get("disk"),
            "power": kwargs.get("power"),
            "core": kwargs.get("core")
        }

        self.data[new_id] = computer

        with open("computers.json", "w", encoding="utf-8") as f:
            json.dump(self.data, f, indent=4, ensure_ascii=False)

