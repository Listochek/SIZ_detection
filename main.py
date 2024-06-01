import sys
import os
import cv2
import shutil
import typing
import math
import cvzone
import time
from PyQt5.QtCore import Qt, QSize, QUrl
from PyQt5.QtGui import QImage, QPixmap, QPalette, QBrush, QIcon
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtWidgets import QComboBox, QToolButton, QFormLayout, QGroupBox, QScrollArea, QFrame, QFileDialog, QApplication, QWidget, QLabel, QVBoxLayout, QHBoxLayout, QSlider, QPushButton, QSizePolicy, QLineEdit, QMessageBox, QTableWidget, QTableWidgetItem, QInputDialog, QSplitter, QProgressBar
import sqlite3
from ultralytics import YOLO
import concurrent.futures

selected_model = "01_nano_1215.pt"

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

    def authenticate(self, login, password):
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
                    QMessageBox.information(self, "Авторизация", "Не известная ошибка | C1")
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

        self.model_combo_box = QComboBox()
        self.model_combo_box.addItems(self.get_model_list())
        self.model_combo_box.setStyleSheet("font-size: 16px; padding: 5px;")
        self.model_combo_box.currentIndexChanged.connect(self.set_global_model)
        layout.addWidget(self.model_combo_box)

        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Логин", "Пароль", "Имя", "Фамилия", "Тир"])
        self.table.setStyleSheet("background: rgba(255, 255, 255, 1);")
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

    def get_model_list(self):
        model_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'models')
        return [f for f in os.listdir(model_dir) if f.endswith('.pt')]

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
    
    def set_global_model(self):
        global selected_model
        selected_model = self.model_combo_box.currentText()

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
        self.setStyleSheet("border-radius: 10px;")
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
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.processing_label = QLabel("Дождитесь окончания обработки")
        self.processing_label.setVisible(False)
        self.processing_label.setMaximumSize(1000, 50)

        self.processing_label.setStyleSheet("font-size: 16px; color: red; font-size: 16px; padding: 10px; border-radius: 5px;")
        self.add_button.setStyleSheet("background-color: #d6001c; color: white; font-size: 16px; padding: 10px; border-radius: 5px; width: 200px;")
        self.confirm_button.setStyleSheet("background-color: #003399; color: white; font-size: 16px; padding: 10px; border-radius: 5px;")
        self.delete_button.setStyleSheet("background-color: #666; color: white; font-size: 16px; padding: 10px; border-radius: 5px;")
        self.back_button.setStyleSheet("background-color: #666; color: white; font-size: 16px; padding: 10px; border-radius: 5px;")

        layout.addWidget(self.video_widget)
        layout.addWidget(self.add_button)
        layout.addWidget(self.confirm_button)
        layout.addWidget(self.delete_button)
        layout.addWidget(self.progress_bar)
        layout.addWidget(self.back_button)
        layout.addWidget(self.processing_label)

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
                self.back_button.setVisible(False)

    def confirm_video(self):
        self.confirm_button.setVisible(False)
        self.delete_button.setVisible(False)
        self.add_button.setVisible(False)
        self.processing_label.setVisible(True)
        
        if hasattr(self, 'video_path'):
            video_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'videos')
            os.makedirs(video_dir, exist_ok=True)
            video_count = len(os.listdir(video_dir))
            new_file_name = f"vid{video_count + 1}.mp4"
            destination_path = os.path.join(video_dir, new_file_name)
            self.progress_bar.setVisible(True)
            self.process_and_save_video(self.video_path, destination_path, new_file_name)
        
        self.player.setMedia(QMediaContent())
        self.player.stop()
        self.processing_label.setVisible(False)
        self.video_widget.setVisible(False)
        self.add_button.setVisible(True)
        self.progress_bar.setVisible(False)
        self.back_button.setVisible(True)
        self.add_button.setVisible(True)
        self.back_button.setVisible(True)

    def delete_video(self):
        self.player.setMedia(QMediaContent())
        self.player.stop()
        self.video_widget.setVisible(False)
        self.confirm_button.setVisible(False)
        self.delete_button.setVisible(False)
        self.add_button.setVisible(True)
        self.back_button.setVisible(True)
        QMessageBox.warning(self, "Удаление", "Видео удалено")
        
    def back_to_login(self):
        self.close()
        self.auth_window = MenuWidget()
        self.auth_window.show()
    
    
    def process_and_save_video(self, input_path, output_path, rlyname):
        self.model = YOLO("models/" + selected_model)
        cap = cv2.VideoCapture(input_path)
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(output_path, fourcc, 20.0, (int(cap.get(3)), int(cap.get(4))))

        self.classNames = ['train', 'cap', 'human', 'rail', 'vest']
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        processed_frames = 0

        self.wear_violation_marks = []

        while cap.isOpened():
            success, frame = cap.read()
            if not success:
                break
            processed_frame = self.process_frame(frame, processed_frames)
            out.write(processed_frame)
            processed_frames += 1
            self.progress_bar.setValue(int((processed_frames / total_frames) * 100))

        cap.release()
        out.release()

        self.save_violation_marks(input_path, rlyname)
        

    def process_frame(self, frame, frame_number):
        color_map = {
            'train': (0, 255, 0),
            'cap': (255, 0, 0),
            'human': (0, 0, 255),
            'rail': (255, 255, 0),
            'vest': (255, 0, 255)
        }
        
        results = self.model(frame)
        humans = []
        vests = []
        caps = []
        trains = []
        rails = []
        self.g = []

        for result in results:
            boxes = result.boxes
            for box in boxes:
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                conf = math.ceil((box.conf[0] * 100)) / 100
                cls = int(box.cls[0])
                
                if cls < len(self.classNames):
                    class_name = self.classNames[cls]
                    if class_name == 'human':
                        humans.append((x1, y1, x2, y2))
                    elif class_name == 'vest':
                        vests.append((x1, y1, x2, y2))
                    elif class_name == 'cap':
                        caps.append((x1, y1, x2, y2))
                    elif class_name == 'train':
                        trains.append((x1, y1, x2, y2))
                    elif class_name == "rail":
                        rails.append((x1, y1, x2, y2))

        def calculate_train_speed(trains, frame_rate):
            if len(trains) < 2:
                return 0.0

            x1, y1, x2, y2 = trains[0]
            x1_last, y1_last, x2_last, y2_last = trains[-1]

            center_first = ((x1 + x2) / 2, (y1 + y2) / 2)
            center_last = ((x1_last + x2_last) / 2, (y1_last + y2_last) / 2)

            distance = math.sqrt((center_last[0] - center_first[0]) ** 2 + (center_last[1] - center_first[1]) ** 2)

            time_diff = len(trains) / frame_rate

            speed = distance / time_diff

            return speed

        frame_rate = 30
        train_speed = calculate_train_speed(trains, frame_rate)
        self.g.append(f"Train speed: {train_speed} pixels/second")

        def is_inside(box1, box2):
            return sum(b1 <= b2 for b1, b2 in zip(box1, box2)) >= 2

        wear_violation_detected = False

        for human in humans:
            has_vest = any(is_inside(human, vest) for vest in vests)
            has_cap = any(is_inside(human, cap) for cap in caps)
            if has_vest and has_cap:
                color = (0, 255, 0)
            else:
                color = (0, 0, 255)
                wear_violation_detected = True

            cvzone.cornerRect(frame, (human[0], human[1], human[2] - human[0], human[3] - human[1]), l=9, rt=1, colorC=color, colorR=color)
            label = 'human'
            cvzone.putTextRect(frame, label, (max(0, human[0]), max(35, human[1])), scale=1, thickness=1, colorR=color)

        if wear_violation_detected:
            self.wear_violation_marks.append(frame_number)

        return frame
    
    def save_violation_marks(self, output_path, rlyname):
        print("GGGGGG")
        print(self.g)
        video_name = os.path.basename(output_path)
        warn_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'warns')
        os.makedirs(warn_dir, exist_ok=True)
        warn_file_path = os.path.join(warn_dir, f"{rlyname}.txt")

        with open(warn_file_path, 'w') as warn_file:
            for mark in self.wear_violation_marks:
                warn_file.write(f"{mark}|WEAR\n")

            warn_file.close()

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
        time.sleep(1)
        self.check_for_violations(video_path)

    def check_for_violations(self, video_path):
        video_name = os.path.basename(video_path)
        video_base_name = os.path.splitext(video_name)[0]
        warn_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'warns', f"{video_base_name}.mp4.txt")
        if os.path.exists(warn_file_path):
            with open(warn_file_path, 'r') as warn_file:
                for line in warn_file:
                    frame_number = int(line.strip().split('|')[0])
                    self.mark_violation_on_slider(frame_number)

    def mark_violation_on_slider(self, frame_number):
        cap = cv2.VideoCapture(self.player.currentMedia().canonicalUrl().toLocalFile())
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        cap.release()

        if total_frames > 0:
            tick_position = int((frame_number / total_frames) * self.slider.width())
            tick = QLabel('|')
            tick.setStyleSheet("color: red;")
            tick.setAlignment(Qt.AlignCenter)
            tick.setFixedWidth(2)
            tick.setParent(self.slider)
            tick.move(tick_position, 0)
            tick.show()

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