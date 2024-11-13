import io
import sys
import time

from PyQt6 import uic
from PyQt6.QtWidgets import QApplication, QMainWindow, QWidget


class Main(QMainWindow):

    def __init__(self):
        super().__init__()
        uic.loadUi('main.ui', self)

        self.loginButton.clicked.connect(self.login)
        self.signupButton.clicked.connect(self.signup)

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


class Signup(QWidget):

    def __init__(self):
        super().__init__()
        uic.loadUi('signupform.ui', self)


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    main = Main()
    main.show()
    sys.excepthook = except_hook
    sys.exit(app.exec())
