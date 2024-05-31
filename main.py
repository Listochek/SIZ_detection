import sys
import os
import cv2
import shutil
import typing
from PyQt5.QtCore import Qt, QSize, QUrl
from PyQt5.QtGui import QImage, QPixmap, QPalette, QBrush, QIcon
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtWidgets import QToolButton, QFormLayout, QGroupBox, QScrollArea, QFrame, QFileDialog, QApplication, QWidget, QLabel, QVBoxLayout, QHBoxLayout, QSlider, QPushButton, QSizePolicy, QLineEdit, QMessageBox, QTableWidget, QTableWidgetItem, QInputDialog, QSplitter
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
        image = QImage("assets/authback.png").scaled(QSize(500, 500))
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

    def authenticate(self, login, password): #C1 ---------------------- C1
        self.cursor.execute("SELECT * FROM users WHERE username=? AND password=?", (login, password))
        result = self.cursor.fetchone()
        if result:
                if result[5] == "3":
                    self.close()
                    self.admin_window = AdminWindow(self.conn)
                    self.admin_window.show()
                    QMessageBox.information(self, "Авторизация", "Вы вошли как администратор")
                elif result[5] == "1":
                    self.close()
                    self.user_window = UserWindow(self.conn, login)
                    self.user_window.show()
                    QMessageBox.information(self, "Авторизация", "Вы вошли как сотрудник")
                elif result[5] == "2":
                    self.close()
                    self.user_window = WatcherWindow(self.conn, login)
                    self.user_window.show()
                    QMessageBox.information(self, "Авторизация", "Вы вошли как смотрящий")
                else:
                    QMessageBox.information(self, "Авторизация", "Не известная ошибка | C1") #C1 ---------------------- C1
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
        p.setBrush(self.backgroundRole(), QBrush(QPixmap("assets/adminback.png")))
        self.setPalette(p)
        self.setStyleSheet("border-radius: 10px;")
        layout = QVBoxLayout()


        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Логин", "Пароль", "Имя", "Фамилия", "Тир"])
        self.table.setStyleSheet("background: rgba(255, 255, 255, 0.5);")
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
                name, okPressed = QInputDialog.getText(self, "Добавить сотрудника","Имя:")
                if okPressed and password != '':
                    surname, okPressed = QInputDialog.getText(self, "Добавить сотрудника","Фамилия:")
                    if okPressed and password != '':
                        tier, okPressed = QInputDialog.getText(self, "Добавить сотрудника","Уровень [1 - сотрудник | 2 - проверяющй]:")
                        try:
                            cursor = self.db_connection.cursor()
                            cursor.execute('INSERT INTO users (username, password, name, surname, tier) VALUES (?, ?, ?, ?, ?)', (username, password, name, surname, tier))
                            self.db_connection.commit()
                            self.load_data()
                            QMessageBox.information(self, "Успех", "Пользоатель успешно добавлен")
                        except Exception as e:
                            QMessageBox.warning(self, "Ошибка", f"Не удалось доавить пользователя: {str(e)}")

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
                QMessageBox.warning(self, "Ошибка", f"Не удалось удалит пользователя: {str(e)}")
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
        self.setFixedSize(1800, 1000)
        self.setAutoFillBackground(True)
        p = self.palette()
        p.setBrush(self.backgroundRole(), QBrush(QPixmap("assets/userback.png")))
        self.setPalette(p)
        self.setStyleSheet("background: rgba(255, 255, 255, 0.5); border-radius: 10px;")
        layout = QVBoxLayout()
        self.video_widget = QVideoWidget()
        self.player = QMediaPlayer()
        self.player.setVideoOutput(self.video_widget)
        self.video_widget.setVisible(False)
        
        self.add_button = QPushButton('Добавить видео')
        self.confirm_button = QPushButton('Подтвердить')
        self.confirm_button.setVisible(False)
        self.delete_button = QPushButton('Удалить')
        self.delete_button.setVisible(False)
        self.back_button = QPushButton('Назад к авторизации')

        self.add_button.setStyleSheet("background-color: #d6001c; color: white; font-size: 16px; padding: 10px; border-radius: 5px; width: 200px;")
        self.confirm_button.setStyleSheet("background-color: #003399; color: white; font-size: 16px; padding: 10px; border-radius: 5px;")
        self.delete_button.setStyleSheet("background-color: #666; color: white; font-size: 16px; padding: 10px; border-radius: 5px;")
        self.back_button.setStyleSheet("background-color: #666; color: white; font-size: 16px; padding: 10px; border-radius: 5px;")

        layout.addWidget(self.video_widget)
        layout.addWidget(self.add_button)
        layout.addWidget(self.confirm_button)
        layout.addWidget(self.delete_button)
        layout.addWidget(self.back_button)

        self.add_button.clicked.connect(self.add_video)
        self.confirm_button.clicked.connect(self.confirm_video)
        self.delete_button.clicked.connect(self.delete_video)
        self.back_button.clicked.connect(self.back_to_login)

        layout.setAlignment(self.add_button, Qt.AlignCenter)

        self.setLayout(layout)

    def add_video(self):
        file_dialog = QFileDialog()
        file_dialog.setFileMode(QFileDialog.ExistingFile)
        file_dialog.setNameFilter("Video files (*.mp4 *.avi)")
        if file_dialog.exec_():
            selected_files = file_dialog.selectedFiles()
            if selected_files:
                self.video_path = selected_files[0]
                self.player.setMedia(QMediaContent(QUrl.fromLocalFile(self.video_path)))
                self.player.play()
                self.video_widget.setVisible(True)
                self.confirm_button.setVisible(True)
                self.delete_button.setVisible(True)
                self.add_button.setVisible(False)

    def confirm_video(self):
        if hasattr(self, 'video_path'):
            video_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'videos')
            os.makedirs(video_dir, exist_ok=True)
            video_count = len(os.listdir(video_dir))
            new_file_name = f"vid{video_count + 1}.mp4"
            destination_path = os.path.join(video_dir, new_file_name)
            shutil.copyfile(self.video_path, destination_path)
        self.player.setMedia(QMediaContent())
        self.player.stop()
        self.video_widget.setVisible(False)
        self.confirm_button.setVisible(False)
        self.delete_button.setVisible(False)
        self.add_button.setVisible(True)
        QMessageBox.information(self, "Подтверждение", "Видео подтверждено")

    def delete_video(self):
        self.player.setMedia(QMediaContent())
        self.player.stop()
        self.video_widget.setVisible(False)
        self.confirm_button.setVisible(False)
        self.delete_button.setVisible(False)
        self.add_button.setVisible(True)
        QMessageBox.warning(self, "Удаление", "Видео удалено")
        
    def back_to_login(self):
        self.close()
        self.auth_window = MenuWidget()
        self.auth_window.show()

class WatcherWindow(QWidget):
    def __init__(self, db_connection, username, parent=None):
        super().__init__(parent)
        self.db_connection = db_connection
        self.username = username
        self.init_ui()

    def init_ui(self):
        video_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'videos')
        video_files = [f for f in os.listdir(video_dir) if f.endswith('.mp4') or f.endswith('.avi')]

        self.setWindowTitle("Смотрящий")
        self.setFixedSize(1800, 1000)
        self.setAutoFillBackground(True)
        p = self.palette()
        p.setBrush(self.backgroundRole(), QBrush(QPixmap("assets/userback.png")))
        self.setPalette(p)
        self.setStyleSheet("border-radius: 10px;")

        self.video_widget = QVideoWidget()
        self.player = QMediaPlayer()
        self.player.setVideoOutput(self.video_widget)
        self.player.setMuted(True)

        self.slider = QSlider(Qt.Horizontal)
        self.slider.setRange(0, 0)
        self.slider.sliderMoved.connect(self.set_position)
        self.slider.setSingleStep(1)

        self.player.positionChanged.connect(self.position_changed)
        self.player.durationChanged.connect(self.duration_changed)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        video_list_widget = QWidget()
        video_list_layout = QVBoxLayout()
        video_list_widget.setLayout(video_list_layout)

        for video_file in video_files:
            video_path = os.path.join(video_dir, video_file)
            video_button = QToolButton()
            video_button.setIcon(self.get_video_thumbnail(video_path))
            video_button.setIconSize(QSize(200, 150))
            video_button.setText(video_file)
            video_button.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
            video_button.setStyleSheet("QToolButton { text-align: center; }")
            video_button.clicked.connect(lambda checked, path=video_path: self.play_video(path))
            video_list_layout.addWidget(video_button)

        self.scroll_area.setWidget(video_list_widget)

        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(self.video_widget)
        splitter.addWidget(self.scroll_area)
        splitter.setSizes([1550, 250])

        self.pause_button = QPushButton('Пауза')
        self.pause_button.setStyleSheet("background-color: #666; color: white; font-size: 16px; padding: 10px; border-radius: 5px;")
        self.pause_button.clicked.connect(self.toggle_pause)

        layout = QVBoxLayout()
        layout.addWidget(splitter)
        layout.addWidget(self.slider)
        layout.addWidget(self.pause_button)

        self.setLayout(layout)

    def play_video(self, video_path):
        self.player.setMedia(QMediaContent(QUrl.fromLocalFile(video_path)))
        self.player.play()

    def get_video_thumbnail(self, video_path):
        cap = cv2.VideoCapture(video_path)
        ret, frame = cap.read()
        cap.release()
        if ret:
            height, width, channel = frame.shape
            bytes_per_line = 3 * width
            q_img = QImage(frame.data, width, height, bytes_per_line, QImage.Format_RGB888).rgbSwapped()
            return QIcon(QPixmap.fromImage(q_img))
        return QIcon()

    def position_changed(self, position):
        self.slider.setValue(position)

    def duration_changed(self, duration):
        self.slider.setRange(0, duration)

    def set_position(self, position):
        self.player.setPosition(position)

    def toggle_pause(self):
        if self.player.state() == QMediaPlayer.PlayingState:
            self.player.pause()
            self.pause_button.setText('Воспроизвести')
            self.pause_button.setStyleSheet("background-color: green; color: white; font-size: 16px; padding: 10px; border-radius: 5px;")
        else:
            self.player.play()
            self.pause_button.setText('Пауза')
            self.pause_button.setStyleSheet("background-color: #c91616; color: white; font-size: 16px; padding: 10px; border-radius: 5px;")

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Space:
            self.toggle_pause()
        super().keyPressEvent(event)

if __name__ == '__main__': 
    print("SIZ>> __main__ запущен!")
    app = QApplication(sys.argv)
    window = MenuWidget()
    window.show()   
    sys.exit(app.exec_())