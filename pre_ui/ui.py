import sys
import os
from PyQt5.QtCore import Qt, QTimer, QSize, QUrl
from PyQt5.QtGui import QImage, QPixmap, QPalette, QBrush
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout, QHBoxLayout, QSlider, QPushButton, QSizePolicy, QLineEdit, QMessageBox, QTableWidget, QTableWidgetItem, QInputDialog
import sqlite3

#sjnfj
#12312321 dfsafqa fdsfsdf
class MenuWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.init_db()

    def init_ui(self):
        layout = QVBoxLayout()
        self.setFixedSize(500, 500)
        
        login_input = QLineEdit()
        login_input.setPlaceholderText("Логин")
        password_input = QLineEdit()
        password_input.setPlaceholderText("Пароль")
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
        image = QImage("pre_ui/authback.jpg").scaled(QSize(500, 500))
        palette = QPalette()
        palette.setBrush(QPalette.Window, QBrush(image))                        
        self.setPalette(palette)
            
        self.setLayout(layout)
        
        auth_button.clicked.connect(lambda: self.authenticate(login_input.text(), password_input.text()))
        login_input.returnPressed.connect(lambda: self.authenticate(login_input.text(), password_input.text()))
        password_input.returnPressed.connect(lambda: self.authenticate(login_input.text(), password_input.text()))

    def init_db(self):
        self.conn = sqlite3.connect('users.db')
        self.cursor = self.conn.cursor()
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                username TEXT NOT NULL,
                password TEXT NOT NULL,
                name TEXT NOT NULL,
                surname TEXT NOT NULL,
                tier INTEGER NOT NULL
            )
        ''')
        self.conn.commit()
#123
    def authenticate(self, login, password):
        self.cursor.execute("SELECT * FROM users WHERE username=? AND password=?", (login, password))
        result = self.cursor.fetchone()
        if result:
            if login == "admin":
                self.close()
                self.admin_window = AdminWindow(self.conn)
                self.admin_window.show()
                QMessageBox.information(self, "Авторизация", "Вы вошли как администратор")
            else:
                print(result)
                if result[5] == "1":
                    self.close()
                    self.user_window = UserWindow(self.conn, login)
                    self.user_window.show()
                    QMessageBox.information(self, "Авторизация", "Вы вошли как сотрудник")

                else:
                    QMessageBox.information(self, "Авторизация", "Вы вошли никак")
        else:
            QMessageBox.warning(self, "Авторизация", "Неверный логин или пароль")
 
 
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
        self.setFixedSize(800, 600)
        self.setAutoFillBackground(True)
        p = self.palette()
        p.setBrush(self.backgroundRole(), QBrush(QPixmap("C:/SIZ_detection/pre_ui/adminback.png")))
        self.setPalette(p)
        self.setStyleSheet("border-radius: 10px;")
        layout = QVBoxLayout()


        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Логин", "Пароль", "Имя", "Фамилия", "Тир"])
        self.load_data()

        self.add_button = QPushButton('Добавить сотрудника')
        self.delete_button = QPushButton('Удалить сотрудника')
        self.back_button = QPushButton('Назад к авторизации')
        self.add_button.setStyleSheet("background-color: #d6001c; color: white; font-size: 16px; padding: 10px; border-radius: 5px;")
        self.delete_button.setStyleSheet("background-color: #003399; color: white; font-size: 16px; padding: 10px; border-radius: 5px;")
        self.back_button.setStyleSheet("background-color: #666; color: white; font-size: 16px; padding: 10px; border-radius: 5px;")

        layout.addWidget(self.table)
        layout.addWidget(self.add_button)
        layout.addWidget(self.delete_button)
        layout.addWidget(self.back_button)

        self.setLayout(layout)

        self.add_button.clicked.connect(self.add_user)
        self.delete_button.clicked.connect(self.delete_user)
        self.back_button.clicked.connect(self.back_to_login)

    def back_to_login(self):
        self.close()
        self.auth_window = MenuWidget()
        self.auth_window.show()


    def load_data(self):
        cursor = self.db_connection.cursor()
        cursor.execute("SELECT username, password, name, surname, tier FROM users")
        records = cursor.fetchall()
        self.table.setRowCount(len(records))
        for index, (username, password, name, surname, tier) in enumerate(records):
            self.table.setItem(index, 0, QTableWidgetItem(username))
            self.table.setItem(index, 1, QTableWidgetItem(password))
            self.table.setItem(index, 2, QTableWidgetItem(name))
            self.table.setItem(index, 3, QTableWidgetItem(surname))
            self.table.setItem(index, 4, QTableWidgetItem(tier))

    def add_user(self):
        username, okPressed = QInputDialog.getText(self, "Добавить сотрудника","Логин:")
        if okPressed and username != '':
            password, okPressed = QInputDialog.getText(self, "Добавить сотрудника","Пароль:")
            if okPressed and password != '':
                try:
                    cursor = self.db_connection.cursor()
                    cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, password))
                    self.db_connection.commit()
                    self.load_data()
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

class UserWindow(QWidget):
    def __init__(self, db_connection, username, parent=None):
        super().__init__(parent)
        self.db_connection = db_connection
        self.username = username
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Сотрудник")
        self.setFixedSize(800, 600)
        self.setAutoFillBackground(True)
        p = self.palette()
        p.setBrush(self.backgroundRole(), QBrush(QPixmap("C:/SIZ_detection/pre_ui/userback.png")))
        self.setPalette(p)
        self.setStyleSheet("border-radius: 10px;")
        layout = QVBoxLayout()


        self.setLayout(layout)


    def confirm_video(self):
        QMessageBox.information(self, "Подтверждение", "Видео подтверждено")

    def delete_video(self):
        QMessageBox.warning(self, "Удаление", "Видео удалено")

if __name__ == '__main__':
    print("SIZ>> __main__ запущен!")
    app = QApplication(sys.argv)
    window = MenuWidget()
    window.show()
    sys.exit(app.exec_())
