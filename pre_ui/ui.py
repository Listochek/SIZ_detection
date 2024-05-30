import sys
import os
from PyQt5.QtCore import Qt, QTimer, QSize
from PyQt5.QtGui import QImage, QPixmap, QPalette, QBrush
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout, QHBoxLayout, QSlider, QPushButton, QSizePolicy, QLineEdit, QMessageBox, QTableWidget, QTableWidgetItem, QInputDialog
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
        if login == "admin" and password == "admin":
            self.close()  # Закрыть текущее окно авторизации
            self.admin_window = AdminWindow(self.conn)
            self.admin_window.show()
        elif login == "user" and password == "password":
            QMessageBox.information(self, "Авторизация", "Вы вошли как сотрудник")
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

class AdminWindow(QWidget):
    def __init__(self, db_connection):
        super().__init__()
        self.db_connection = db_connection
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Администратор")
        self.setGeometry(100, 100, 600, 400)
        self.setStyleSheet("background-color: white;")
        layout = QVBoxLayout()

        self.table = QTableWidget()
        self.table.setColumnCount(2)  # Две колонки: логин и пароль
        self.table.setHorizontalHeaderLabels(["Логин", "Пароль"])
        self.load_data()

        self.add_button = QPushButton('Добавить сотрудника')
        self.delete_button = QPushButton('Удалить сотрудника')
        self.add_button.setStyleSheet("background-color: #d6001c; color: white; font-size: 16px; padding: 10px;")
        self.delete_button.setStyleSheet("background-color: #003399; color: white; font-size: 16px; padding: 10px;")

        layout.addWidget(self.table)
        layout.addWidget(self.add_button)
        layout.addWidget(self.delete_button)

        self.setLayout(layout)

        self.add_button.clicked.connect(self.add_user)
        self.delete_button.clicked.connect(self.delete_user)

    def load_data(self):
        cursor = self.db_connection.cursor()
        cursor.execute("SELECT username, password FROM users")
        records = cursor.fetchall()
        self.table.setRowCount(len(records))
        for index, (username, password) in enumerate(records):
            self.table.setItem(index, 0, QTableWidgetItem(username))
            self.table.setItem(index, 1, QTableWidgetItem(password))

    def add_user(self):
        username, okPressed = QInputDialog.getText(self, "Добавить сотрудника","Логин:")
        if okPressed and username != '':
            password, okPressed = QInputDialog.getText(self, "Добавить сотрудника","Пароль:")
            if okPressed and password != '':
                try:
                    cursor = self.db_connection.cursor()
                    cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, password))
                    self.db_connection.commit()
                    self.load_data()  # Обновить таблицу
                    QMessageBox.information(self, "Успех", "Пользователь успешно добавлен")
                except Exception as e:
                    QMessageBox.warning(self, "Ошибка", f"Не удалось добавить пользователя: {str(e)}")

    def delete_user(self):
        selected_items = self.table.selectedItems()
        if selected_items:
            username = selected_items[0].text()
            try:
                cursor = self.db_connection.cursor()
                cursor.execute('DELETE FROM users WHERE username = ?', (username,))
                self.db_connection.commit()
                self.load_data() 
                QMessageBox.information(self, "Успех", "Пользователь успешно удален")
            except Exception as e:
                QMessageBox.warning(self, "Ошибка", f"Не удалось удалить пользователя: {str(e)}")
        else:
            QMessageBox.warning(self, "Ошибка", "Пожалуйста, выберите пользователя для удаления")

if __name__ == '__main__':
    print("SIZ>> __main__ запущен!")
    app = QApplication(sys.argv)
    window = MenuWidget()
    window.show()
    sys.exit(app.exec_())
