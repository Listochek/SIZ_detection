import sys
import os
from PyQt5.QtCore import Qt, QTimer, QSize
from PyQt5.QtGui import QImage, QPixmap, QPalette, QBrush
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout, QHBoxLayout, QSlider, QPushButton, QSizePolicy, QLineEdit, QMessageBox
import sqlite3

class MenuWidget(QWidget):
    def __init__(self):
        
        super().__init__()
        self.init_ui()
        self.init_db()

    def init_ui(self):
        layout = QVBoxLayout()
        self.setFixedSize(500, 500)
        
        login_input = QLineEdit()
        password_input = QLineEdit()
        auth_button = QPushButton('Авторизация')
        
        login_input.setStyleSheet("font-size: 20px;")
        password_input.setStyleSheet("font-size: 20px;")
        auth_button.setStyleSheet("background-color: #cc0000; color: white; font-size: 20px;")
        
        login_input.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed) 
        password_input.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        auth_button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        
        layout.addStretch(1)
        layout.addWidget(login_input)
        layout.addWidget(password_input)
        layout.addWidget(auth_button)
        layout.addStretch(1)
        layout.setAlignment(Qt.AlignCenter)
        layout.setAlignment(auth_button, Qt.AlignCenter)
        image = QImage("C:/SIZ_detection/pre_ui/authback.jpg").scaled(QSize(500, 500))
        palette = QPalette()
        palette.setBrush(QPalette.Window, QBrush(image))                        
        self.setPalette(palette)
            
        self.setLayout(layout)
        
        auth_button.clicked.connect(lambda: self.authenticate(login_input.text(), password_input.text()))

    def init_db(self):
        self.conn = sqlite3.connect('users.db')
        self.cursor = self.conn.cursor()
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                username TEXT NOT NULL,
                password TEXT NOT NULL
            )
        ''')
        self.conn.commit()

    def authenticate(self, login, password):
        self.cursor.execute('SELECT * FROM users WHERE username=? AND password=?', (login, password))
        result = self.cursor.fetchone()
        if result:
            QMessageBox.information(self, "Авторизация", "Вы успешно вошли!")
        else:
            QMessageBox.warning(self, "Авторизация", "Неверный логин или пароль")
 
    # Предполагается, что остальные части класса уже реализованы

    def add_user(self, username, password):
        try:
            self.cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, password))
            self.conn.commit()
            QMessageBox.information(self, "Регистрация", "Новый пользователь успешно добавлен!")
        except sqlite3.IntegrityError:
            QMessageBox.warning(self, "Регистрация", "Пользователь с таким именем уже существует")
        except Exception as e:
            QMessageBox.critical(self, "Регистрация", f"Произошла ошибка: {str(e)}")


    def __del__(self):
        self.conn.close()

'''
    def authenticate(self, login, password):
        if login == "admin" and password == "admin":
            QMessageBox.information(self, "Авторизация", "Вы вошли как администратор")
        elif 1 == 1:
            pass
        elif login == "user" and password == "password":
            QMessageBox.information(self, "Авторизация", "Вы вошли как сотрудник")
        else:
            QMessageBox.warning(self, "Авторизация", "Неверный логин или пароль")
'''

if __name__ == '__main__':
    print("SIZ>> __main__ запущен!")
    app = QApplication(sys.argv)
    window = MenuWidget()
    window.show()
    sys.exit(app.exec_())
