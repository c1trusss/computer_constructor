import io
import sys
import time
from datetime import datetime

from PyQt6 import uic, QtGui
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel, QCheckBox, QFrame, QScrollArea, \
    QLayout, QPushButton

from config import *
from database import Database, JsonDatabase


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


class Login(QWidget):

    def __init__(self):
        super().__init__()
        uic.loadUi('loginform.ui', self)
        self.setFixedSize(1031, 586)

        self.backButton.clicked.connect(self.back)
        self.registerButton.clicked.connect(self.to_reg)
        self.loginButton.clicked.connect(self.login)

    def login(self):
        db = Database('constructor.sqlite')
        login = self.loginEdit.text()
        password = self.passwordEdit.text()

        real_password = db.execute('''SELECT password FROM users WHERE login=?''', (login,)).fetchone()
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


class Signup(QWidget):

    def __init__(self):
        super().__init__()
        uic.loadUi('signupform.ui', self)
        self.setFixedSize(1031, 586)

        self.backButton.clicked.connect(self.back)
        self.loginButton.clicked.connect(self.to_login)
        self.registerButton.clicked.connect(self.signup)

    def signup(self):
        db = Database('constructor.sqlite')
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
            time.sleep(2)
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


class Window(QWidget):

    def __init__(self):
        super().__init__()
        uic.loadUi('window.ui', self)
        self.setFixedSize(1031, 586)

        self.scrollArea.setStyleSheet('background-color: #49507f')
        self.scrollArea.setFixedWidth(211)

        self.params = QWidget(self.scrollArea)
        self.params.setFixedWidth(190)
        self.params.setStyleSheet("font-color: black")
        self.params.move(300, 200)
        self.scrollArea.setWidget(self.params)

        self.layout = QVBoxLayout(self.params)

        self.db = Database("constructor.sqlite")

        self.cb_change()

        self.displayItems.setWidgetResizable(True)

        self.chooseAccessories.currentTextChanged.connect(self.cb_change)

        self.searchButton.clicked.connect(self.apply_changes)

    def apply_changes(self):
        print(self.scrollArea.children())
        db = Database("constructor.sqlite")
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
        products = db.execute(query).fetchall()
        if products:
            main_widget = QWidget()
            layout = QVBoxLayout(main_widget)
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
                for i, p in enumerate(product[2:-2]):
                    params_layout.addWidget(QLabel(f"{param_names_ru[i]}: {p}"))
                params_widget.setLayout(params_layout)
                params_widget.move(310, 20)

                # Кнопка "Добавить в сборку"
                add_button = QPushButton("Добавить в сборку", w)
                add_button.clicked.connect(self.add_product)
                add_button.move(410, 310)
                add_button.setFixedSize(171, 31)

                # Изображение товара
                pixmap = QPixmap('images/img.jpg')

                image = QLabel(w)
                image.move(20, 20)
                image.setFixedSize(271, 271)
                image.setPixmap(pixmap)
                image.setScaledContents(True)

                layout.addWidget(w)

            self.displayItems.setWidget(main_widget)
            self.displayItems.setWidgetResizable(True)
        else:
            print("Ничего не нашлось")

    def cb_change(self):

        current_text = self.chooseAccessories.currentText()

        # Удаление всех элементов из предыдущего layout
        while self.layout.count():
            item = self.layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

        components = {
            "Процессор": 'cpu',
            "Материнская плата": 'motherboards',
            "Оперативная память": 'ram',
            "Видеокарта": 'gpu',
            "Устройство памяти": 'disk',
            "Блок питания": 'power',
            "Кулер для ЦП": 'cpu_coolers',
            "Корпус": 'core',
        }

        data = self.db.execute(f"""SELECT * FROM {components[current_text]}""").fetchall()

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

                self.layout.addWidget(QLabel("Беспроводные интерфейсы"))
                interfaces = set(map(lambda x: x[5], data))

                for interface in interfaces:
                    cb = QCheckBox(interface)
                    self.layout.addWidget(cb)

                self.layout.addWidget(QLabel("Форм-фактор"))
                form_factors = set(map(lambda x: x[6], data))

                for form_factor in form_factors:
                    cb = QCheckBox(form_factor)
                    self.layout.addWidget(cb)

            case "Оперативная память":
                pass
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
                pass
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

            case "Корпус":
                pass

        self.scrollArea.setWidget(self.params)
        self.layout.setSizeConstraint(QVBoxLayout.SizeConstraint.SetMinAndMaxSize)
        self.params.adjustSize()
        self.scrollArea.setWidgetResizable(False)

    def add_product(self):
        pass


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    main = Main()
    main.show()
    sys.excepthook = except_hook
    sys.exit(app.exec())
