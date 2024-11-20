import io
import sqlite3
import sys
import time
from datetime import datetime

import selenium.webdriver.common.devtools.v125.dom
from PyQt6 import uic, QtGui
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap, QFont
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel, QCheckBox, QFrame, QScrollArea, \
    QLayout, QPushButton, QDialog, QMessageBox, QHBoxLayout, QLineEdit, QFileDialog, QInputDialog, QComboBox

from config import *
from database import *
from models import *


class ExtendedWidget(QWidget):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.db = Database()

    def clear_layout(self, layout):
        if layout is not None:
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                if widget is not None:
                    widget.deleteLater()
                else:
                    self.clear_layout(item.layout())


class Main(QMainWindow):

    def __init__(self):
        super().__init__()
        uic.loadUi('main.ui', self)

        self.loginButton.clicked.connect(self.login)
        self.signupButton.clicked.connect(self.signup)
        self.setFixedSize(1031, 586)

    def login(self):
        self.login = Login()
        self.hide()
        self.login.show()

    def signup(self):
        self.signup = Signup()
        self.hide()
        self.signup.show()


class Login(ExtendedWidget):

    def __init__(self):
        super().__init__()
        uic.loadUi('loginform.ui', self)
        self.setFixedSize(1031, 586)

        self.backButton.clicked.connect(self.back)
        self.registerButton.clicked.connect(self.to_reg)
        self.loginButton.clicked.connect(self.login)

    def login(self):
        db = Database()
        login = self.loginEdit.text()
        password = self.passwordEdit.text()

        real_password = db.execute('''SELECT password FROM users WHERE login=?''', (login,)).fetchone()
        if not real_password:
            self.errorLabel.setText('Пользователь не найден')
        else:
            if real_password[0] == password:
                self.window = Window()
                self.hide()
                self.window.show()
            else:
                self.errorLabel.setText('Неверный логин или пароль')

    def to_reg(self):
        self.reg = Signup()
        self.hide()
        self.reg.show()

    def back(self):
        self.main = Main()
        self.hide()
        self.main.show()


class Signup(ExtendedWidget):

    def __init__(self):
        super().__init__()
        uic.loadUi('signupform.ui', self)
        self.setFixedSize(1031, 586)

        self.backButton.clicked.connect(self.back)
        self.loginButton.clicked.connect(self.to_login)
        self.registerButton.clicked.connect(self.signup)

    def signup(self):
        db = Database()
        login = self.loginEdit.text()
        password = self.passwordEdit.text()
        confirmPassword = self.passwordConfirm.text()

        logins = map(lambda x: x[0], db.execute("""SELECT login FROM users""").fetchall())
        if login in logins:
            self.errorLabel.setText('Логин уже занят')
        elif password != confirmPassword:
            self.errorLabel.setText('Пароли не совпадают')
        else:
            db.execute('''INSERT INTO users (login, password, register_date) VALUES (?, ?, ?)''',
                       (login, password, str(datetime.now().date())))

            self.errorLabel.setText('Успешная регистрация!')
            db.commit()
            self.window = Window()
            self.hide()
            self.window.show()

    def to_login(self):
        self.login = Login()
        self.hide()
        self.login.show()

    def back(self):
        self.main = Main()
        self.hide()
        self.main.show()


class Window(ExtendedWidget):

    def __init__(self):
        super().__init__()
        uic.loadUi('window.ui', self)
        self.setFixedSize(1031, 586)

        self.scrollArea.setStyleSheet('background-color: #49507f')
        self.scrollArea.setFixedWidth(211)

        self.params = QWidget(self.scrollArea)
        self.params.setFixedWidth(190)
        self.params.setStyleSheet("font-color: black; background-color: transparent")
        self.params.move(300, 200)
        self.scrollArea.setWidget(self.params)

        self.layout = QVBoxLayout(self.params)
        self.displayLayout = QVBoxLayout()

        self.db = Database()
        self.jsondb = JsonDatabase()

        self.cb_change()

        self.displayItems.setWidgetResizable(True)
        self.displayItems.setStyleSheet("background-color: #49507f;")

        self.chooseAccessories.currentTextChanged.connect(self.cb_change)
        self.searchButton.clicked.connect(self.apply_changes)
        self.adminButton.clicked.connect(self.to_admin)
        self.createComputerButton.clicked.connect(self.create_computer)
        self.buildsButton.clicked.connect(self.builds)

    def builds(self):
        try:
            self.build = Builds()
        except BuildNotFoundError:
            self.statusLabel.setText('Сохранённых сборок <span style="color: red;">не найдено</span>')
            return
        self.hide()
        self.build.show()

    def create_computer(self):
        name, ok_pressed = QInputDialog.getText(self, "Имя сборки", "Выберите имя сборки")
        if ok_pressed:
            self.jsondb.data["current"]["name"] = name
            self.statusLabel.setText('Сборка <span style="color: #18e130;">сохранена</span>! '
                                 'Вы можете посмотреть ее в своём аккаунте')
        self.jsondb.data["other"].append(self.jsondb.data["current"])
        self.jsondb.data["current"] = {
            "cpu": "",
            "cpu_coolers": "",
            "gpu": "",
            "motherboards": "",
            "ram": "",
            "disk": "",
            "power": "",
            "core": ""
        }
        self.jsondb.dump()


    def to_admin(self):
        self.dlg = CodeDialog()
        self.dlg.exec()

    def apply_changes(self):
        print(self.scrollArea.children())
        current_text = self.chooseAccessories.currentText()
        table_name = COMPONENTS[current_text]
        current_parameter = ''
        query = f"""SELECT * FROM {table_name} WHERE """
        queries = []  # Список запросов, которые потом будут объединены через AND
        cb_group = []  # Группировка чекбоксов по параметрам
        for w in self.params.children():
            if isinstance(w, QLabel):
                current_parameter = w.text()
                if cb_group:
                    queries.append(f"({' OR '.join(cb_group)})")
                cb_group = []
            elif isinstance(w, QCheckBox):
                if w.isChecked():
                    cb_group.append(f'{PARAMS[table_name][current_parameter]}="{w.text()}"')
        if cb_group:
            queries.append(f"({' OR '.join(cb_group)})")

        query += " AND ".join(queries)
        print(query)
        try:
            products = self.db.execute(query).fetchall()
        except sqlite3.OperationalError:
            products = []
        if products:
            main_widget = QWidget()
            self.displayLayout = QVBoxLayout(main_widget)
            # Создание виджета для каждого найденного товара и добавление его в Vertical Layout,
            # который можно будет скроллить
            for product in products:
                w = QWidget()
                w.setFixedSize(611, 401)

                # Название товара
                title = QLabel(product[1], w)
                title.move(20, 300)
                title.setFont(QtGui.QFont("Montserrat Medium", 12))
                # Характеристики товара
                params_widget = QWidget(w)
                params_layout = QVBoxLayout(params_widget)
                param_names_ru = []
                for k, v in PARAMS[table_name].items():
                    param_names_ru.append(k)
                for i, p in enumerate(product[2:-3]):
                    params_layout.addWidget(QLabel(f"{param_names_ru[i]}: {p}"))
                params_widget.setLayout(params_layout)
                params_widget.move(310, 20)

                # Цена товара
                price = QLabel(f'{product[-3]} руб.', w)
                price.move(410, 270)
                price.setFont(QFont("Montserrat Semibold", 12))

                # Кнопка "Добавить в сборку"
                add_button = ExtendedPushButton(table_name, title.text(), "Добавить в сборку", w)
                add_button.clicked.connect(self.add_product)
                add_button.move(410, 310)
                add_button.setFixedSize(171, 31)

                self.displayLayout.addWidget(w)

                # Ссылка на Маркет
                link_text = 'Товар на <span style="color: red;">Я</span>.Маркете'
                market_link = QLabel(
                    f'<a href="{product[-2]}" style="color: white; text-decoration: none;">{link_text}</a>', w
                )
                market_link.setOpenExternalLinks(True)
                market_link.move(410, 350)
                market_link.setFont(QFont("Montserrat Semibold", 12))

                # Изображение товара
                img = product[-1]
                pixmap = QPixmap(f'images/{img}')

                image = QLabel(w)
                image.move(20, 20)
                image.setFixedSize(271, 271)
                image.setPixmap(pixmap)
                image.setScaledContents(True)

                self.displayLayout.addWidget(w)

            self.displayItems.setWidget(main_widget)
            self.displayItems.setWidgetResizable(True)

            variants = ''
            find = 'Нашлось'
            cnt = self.displayLayout.count()
            if cnt in range(5, 20):
                variants = 'товаров'
            elif cnt % 10 == 1:
                variants = 'товар'
                find = 'Нашёлся'
            elif cnt % 10 in range(2, 5):
                variants = 'товара'
            self.statusLabel.setText(f'{find} <span style="color: #18e130;">{cnt}</span> {variants}')
        else:
            self.statusLabel.setText('<span style="color: red">Ничего не нашлось</span>')

    def cb_change(self):

        current_text = self.chooseAccessories.currentText()

        self.clear_layout(self.layout)
        self.clear_layout(self.displayLayout)
        self.statusLabel.setText('')

        data = self.db.execute(f"""SELECT * FROM {COMPONENTS[current_text]}""").fetchall()

        match current_text:
            case "Процессор":
                self.layout.addWidget(QLabel("Бренд"))
                brands = set(map(lambda x: x[2], data))

                for brand in brands:
                    cb = QCheckBox(brand)
                    self.layout.addWidget(cb)

                self.layout.addWidget(QLabel("Линейка процессоров"))
                groups = set(map(lambda x: x[4], data))

                for group in groups:
                    cb = QCheckBox(group)
                    self.layout.addWidget(cb)

                self.layout.addWidget(QLabel("Сокет"))
                sockets = set(map(lambda x: x[3], data))

                for socket in sockets:
                    cb = QCheckBox(socket)
                    self.layout.addWidget(cb)

                self.layout.addWidget(QLabel("Вид поставки"))
                types = set(map(lambda x: x[5], data))

                for t in types:
                    cb = QCheckBox(t)
                    self.layout.addWidget(cb)

            case "Кулер для ЦП":

                self.layout.addWidget(QLabel("Бренд"))
                brands = set(map(lambda x: x[2], data))
                for brand in brands:
                    cb = QCheckBox(brand)
                    self.layout.addWidget(cb)

                self.layout.addWidget(QLabel("Максимальная рассеиваемая\nмощность (TDP), Вт"))
                tdp = set(map(lambda x: x[3], data))
                for t in sorted(tdp, reverse=True):
                    cb = QCheckBox(str(t))
                    self.layout.addWidget(cb)

                self.layout.addWidget(QLabel("Сокет"))
                sockets = set(map(lambda x: x[4], data))
                for socket in sorted(sockets):
                    cb = QCheckBox(socket)
                    self.layout.addWidget(cb)

            case "Материнская плата":

                self.layout.addWidget(QLabel("Бренд"))
                brands = set(map(lambda x: x[2], data))
                for brand in brands:
                    cb = QCheckBox(brand)
                    self.layout.addWidget(cb)

                self.layout.addWidget(QLabel("Сокет"))
                sockets = set(map(lambda x: x[3], data))
                for socket in sockets:
                    cb = QCheckBox(socket)
                    self.layout.addWidget(cb)

                self.layout.addWidget(QLabel("Чипсет"))
                chipsets = set(map(lambda x: x[4], data))
                for chipset in chipsets:
                    cb = QCheckBox(chipset)
                    self.layout.addWidget(cb)

                self.layout.addWidget(QLabel("Форм-фактор"))
                form_factors = set(map(lambda x: x[5], data))
                for form_factor in form_factors:
                    cb = QCheckBox(form_factor)
                    self.layout.addWidget(cb)

            case "Оперативная память":

                self.layout.addWidget(QLabel("Бренд"))
                brands = set(map(lambda x: x[2], data))
                for brand in brands:
                    cb = QCheckBox(brand)
                    self.layout.addWidget(cb)

                self.layout.addWidget(QLabel("Объем памяти, Гб"))
                memories = set(map(lambda x: x[3], data))
                for memory in sorted(memories, reverse=True):
                    cb = QCheckBox(str(memory))
                    self.layout.addWidget(cb)

                self.layout.addWidget(QLabel("Тип памяти"))
                types = set(map(lambda x: x[4], data))
                for t in sorted(types):
                    cb = QCheckBox(t)
                    self.layout.addWidget(cb)

                self.layout.addWidget(QLabel("Частота памяти, МГц"))
                frequencies = set(map(lambda x: x[5], data))
                for frequency in sorted(frequencies, reverse=True):
                    cb = QCheckBox(str(frequency))
                    self.layout.addWidget(cb)

            case "Видеокарта":

                self.layout.addWidget(QLabel("Бренд"))
                brands = set(map(lambda x: x[2], data))
                for brand in sorted(brands):
                    cb = QCheckBox(brand)
                    self.layout.addWidget(cb)

                self.layout.addWidget(QLabel("Объем видеопамяти, Гб"))
                capacities = set(map(lambda x: x[3], data))
                for capacity in sorted(capacities, reverse=True):
                    cb = QCheckBox(str(capacity))
                    self.layout.addWidget(cb)

                self.layout.addWidget(QLabel("Разработчик видеокарты"))
                developers = set(map(lambda x: x[4], data))
                for developer in sorted(developers):
                    cb = QCheckBox(developer)
                    self.layout.addWidget(cb)

                self.layout.addWidget(QLabel("Тип памяти"))
                types = set(map(lambda x: x[5], data))
                for t in sorted(types):
                    cb = QCheckBox(t)
                    self.layout.addWidget(cb)

            case "Устройство памяти":

                self.layout.addWidget(QLabel("Бренд"))
                brands = set(map(lambda x: x[2], data))
                for brand in brands:
                    cb = QCheckBox(brand)
                    self.layout.addWidget(cb)

                self.layout.addWidget(QLabel("Емкость, Гб"))
                capacities = set(map(lambda x: x[3], data))
                for capacity in sorted(capacities, reverse=True):
                    cb = QCheckBox(str(capacity))
                    self.layout.addWidget(cb)

            case "Блок питания":

                self.layout.addWidget(QLabel("Бренд"))
                brands = set(map(lambda x: x[2], data))
                for brand in brands:
                    cb = QCheckBox(brand)
                    self.layout.addWidget(cb)

                self.layout.addWidget(QLabel("Мощность, Вт"))
                powers = set(map(lambda x: x[3], data))
                for power in sorted(powers, reverse=True):
                    cb = QCheckBox(str(power))
                    self.layout.addWidget(cb)

            case "Корпус":

                self.layout.addWidget(QLabel("Бренд"))
                brands = set(map(lambda x: x[2], data))
                for brand in brands:
                    cb = QCheckBox(brand)
                    self.layout.addWidget(cb)

                self.layout.addWidget(QLabel("Тип корпуса"))
                types = set(map(lambda x: x[3], data))
                for t in sorted(types):
                    cb = QCheckBox(t)
                    self.layout.addWidget(cb)

                self.layout.addWidget(QLabel("Форм-фактор материнской платы"))
                form_factors = set(map(lambda x: x[4], data))
                for form_factor in form_factors:
                    cb = QCheckBox(form_factor)
                    self.layout.addWidget(cb)

        self.scrollArea.setWidget(self.params)
        self.layout.setSizeConstraint(QVBoxLayout.SizeConstraint.SetMinAndMaxSize)
        self.params.adjustSize()
        self.scrollArea.setWidgetResizable(False)

    def add_product(self):

        self.jsondb.data["current"][self.sender().component_type] = self.sender().component_title
        self.jsondb.dump()

        self.statusLabel.setText('Успешно <span style="color: #18e130;">добавлено</span>!')


class CodeDialog(QDialog):

    def __init__(self):
        super().__init__()
        uic.loadUi('code_dialog.ui', self)
        self.setFixedSize(445, 115)

        self.enterButton.clicked.connect(self.enter)
        self.backButton.clicked.connect(self.back)

    def enter(self):
        code = self.codeEdit.text()
        if code == ADMIN_KEY:
            self.admin_window = Admin()
            self.admin_window.show()
            self.close()
        else:
            self.errorLabel.setText("Неверный код!")

    def back(self):
        self.close()


class Admin(ExtendedWidget):

    def __init__(self):
        super().__init__()
        uic.loadUi('admin.ui', self)
        self.setFixedSize(457, 547)

        self.widget.setStyleSheet("font: black")

        self.db = Database()
        self.table = ''

        self.chooseComponent.currentTextChanged.connect(self.comp_change)
        self.addButton.clicked.connect(self.add)
        self.addImage.clicked.connect(self.add_image)

        self.comp_change()

    def add_image(self):
        self.file_path = QFileDialog.getOpenFileName(
            self, 'Добавить изображение', '', 'Картинка (*.jpg);;Картинка (*.png);;Все файлы (*)'
        )[0]
        if self.file_path:
            self.statusLabel.setText("Изображение загружено!")
            print(self.file_path)

    def add(self):

        columns = []
        values = []
        for hbox in self.verticalLayout.children():
            label, edit = hbox.itemAt(0).widget(), hbox.itemAt(1).widget()
            print(label, edit)
            column = label.text().split()[0]
            value = edit.text()

            if value:
                columns.append(column)
                values.append(value)
        query = f"""INSERT INTO {self.table}({', '.join(columns)}) VALUES ("{'", "'.join(values)}")"""
        print(query)
        self.db.execute(query)
        try:
            self.db.execute(f"""UPDATE {self.table}
                                SET image = "{self.file_path.split('/')[-1]}"
                                WHERE title = "{values[0]}" """)
            self.db.commit()
            self.statusLabel.setText("Запись добавлена!")
        except sqlite3.IntegrityError:
            self.statusLabel.setText("Ошибка: такое имя уже существует")

    def comp_change(self):

        self.clear_layout(self.verticalLayout)

        current_text = self.chooseComponent.currentText()
        self.table = COMPONENTS[current_text]
        columns = self.db.columns(self.table)

        # Берутся все столбцы, кроме первичного ключа и пути к изображению
        for column in columns[1:-1]:
            hbox = QHBoxLayout()
            hbox.addWidget(QLabel(f"{column} = "))
            hbox.addWidget(QLineEdit())
            self.verticalLayout.addLayout(hbox)

        self.widget.setLayout(self.verticalLayout)

    def clear_layout(self, layout):
        if layout is not None:
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                if widget is not None:
                    widget.deleteLater()
                else:
                    self.clear_layout(item.layout())


class Builds(ExtendedWidget):

    def __init__(self):
        super().__init__()
        uic.loadUi('builds.ui', self)
        self.setFixedSize(1031, 586)

        self.db = Database()
        self.jsondb = JsonDatabase()

        self.build_names = self.jsondb.get_build_names()

        self.params = QVBoxLayout()
        self.txt_format = ''

        self.chooseBuild.addItems(self.build_names)
        self.chooseBuild.currentTextChanged.connect(self.build_change)
        self.downloadButton.clicked.connect(self.download)
        self.backButton.clicked.connect(self.back)

        self.build_change()

    def back(self):
        self.w = Window()
        self.hide()
        self.w.show()

    def build_change(self):
        build_name = self.chooseBuild.currentText()
        print(build_name)
        build = self.jsondb.build_by_name(build_name)
        if not build:
            raise BuildNotFoundError("Активных сборок не найдено")
        self.clear_layout(self.params)

        total_cost = 0
        self.txt_format = ''
        for param, value in build.items():
            p = Parameter(param)
            table_name = param
            c = Component(table_name, value)
            if param == 'name':
                continue
            cost = c.get_cost()
            if cost == 0:
                continue
            total_cost += cost
            product_label = f"{p.get_name()}: {value}"
            string = f"{product_label:.<{135 - len(str(cost))}}{cost}"
            self.txt_format += string + '\n'
            label = QLabel(string)
            label.setFont(QFont("Courier"))
            print(len(label.text()))
            self.params.addWidget(label)

        string = f"Итого: {total_cost} рублей"
        self.txt_format += '\n' + string
        self.params.addWidget(QLabel(string))

        self.buildDisplay.setLayout(self.params)

    def download(self):
        file_path = QFileDialog.getSaveFileName(self, 'Скачать результат', '', 'Текстовый документ (*.txt)')[0]
        if file_path:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(self.txt_format)


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    main = Main()
    main.show()
    sys.excepthook = except_hook
    sys.exit(app.exec())
