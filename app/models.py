from PyQt6.QtWidgets import QPushButton

from database import Database
from config import COMPONENTS


class ExtendedPushButton(QPushButton):

    def __init__(self, component_type, component_title, *args):
        super().__init__(*args)
        self.component_type = component_type
        self.component_title = component_title


class Component:

    def __init__(self, table_name, component_title):
        self.table_name = table_name
        self.component_title = component_title

    def get_cost(self):
        db = Database()
        print(f"""SELECT cost FROM {self.table_name} WHERE title="{self.component_title}" """)
        try:
            response = db.execute(f"""SELECT cost FROM {self.table_name} WHERE title="{self.component_title}" """)
            cost = int(response.fetchone()[0])

        except TypeError:
            cost = 0

        return cost


class Parameter:

    def __init__(self, table_name):
        self.table_name = table_name
        self.name = ''
        for param in COMPONENTS.keys():
            if COMPONENTS[param] == table_name:
                self.name = param

    def get_name(self):
        return self.name

    def get_code(self):
        return self.table_name
