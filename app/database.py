import json
import sqlite3


class Database:

    def __init__(self):
        self.db_name = 'constructor.sqlite'
        self.connection = sqlite3.connect(self.db_name)

    def columns(self, table):
        p = self.execute(f"SELECT * FROM {table}")
        columns = [description[0] for description in p.description]

        return columns

    def execute(self, query, *args):
        cursor = self.connection.cursor()
        return cursor.execute(query, *args)

    def __del__(self):
        self.connection.close()

    def commit(self):
        self.connection.commit()

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

        self.dump()

    def get_build_names(self):
        try:
            return list(map(lambda x: x["name"], self.data["other"]))
        except KeyError:  # Ошибка вызывается, если человек попытается открыть свои сборки, не сохранив ни одну из них
            return []

    def build_by_name(self, name):
        for build in self.data["other"]:
            if build["name"] == name:
                return build

    def dump(self):
        with open("computers.json", "w", encoding="utf-8") as f:
            json.dump(self.data, f, indent=4, ensure_ascii=False)

