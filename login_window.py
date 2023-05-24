import hashlib
import pickle
import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QLineEdit, QTextEdit, QMessageBox, QFormLayout
from PyQt5.QtGui import QPixmap, QFont
from PyQt5.QtCore import Qt
from video_stream import VideoStream

class LoginWindow(QWidget):
    def __init__(self, parent=None):
        super(LoginWindow, self).__init__(parent)
        self.setWindowTitle('Login Window')
        self.resize(400, 500)
        self.initUI()

    def initUI(self):
        description_text = " ".join([
            "Эта программа разработана для автоматического распознавания лиц и идентификации сотрудников с целью регистрации рабочего времени.",
            "\nОна использует продвинутые технологии обработки изображений и искусственного интеллекта, включая SSD (Single Shot MultiBox Detector) и FaceNet.",
            "\nДля использования программы требуется база данных лиц сотрудников.",
            "\nПрограмма представляет собой мощный инструмент для автоматического контроля рабочего времени, который облегчает процесс учета времени и помогает повысить производительность и эффективность управления персоналом."
        ])

        layout = QVBoxLayout()

        # Заголовок
        title = QLabel('Программа FaceID Tracking')
        title_font = QFont("Arial", 24)
        title.setFont(title_font)
        layout.addWidget(title, alignment=Qt.AlignCenter)

        # Изображение
        image = QLabel(self)
        pixmap = QPixmap('start_image.png')
        image.setPixmap(pixmap)
        layout.addWidget(image, alignment=Qt.AlignCenter)

        # Описание
        description = QTextEdit()
        description.setReadOnly(True)
        description.setText(description_text)
        description.setFixedHeight(100)
        description.setStyleSheet("font-size: 16px")
        layout.addWidget(description)


        # Поля ввода и кнопка
        form_layout = QFormLayout()
        self.login_field = QLineEdit()
        self.password_field = QLineEdit()
        self.password_field.setEchoMode(QLineEdit.Password)
        form_layout.addRow('Login:', self.login_field)
        form_layout.addRow('Password:', self.password_field)
        layout.addLayout(form_layout)

        login_button = QPushButton('ЗАПУСК')
        login_button.clicked.connect(self.check_credentials)
        login_button.setFixedSize(200, 50)
        login_button.setStyleSheet("font-size: 18px")
        layout.addWidget(login_button, alignment=Qt.AlignCenter)

        self.setLayout(layout)

        # Получаем геометрию экрана
        screen_geometry = QApplication.desktop().availableGeometry()
        # Получаем геометрию окна
        window_geometry = self.frameGeometry()
        # Устанавливаем центр окна в центр экрана
        window_geometry.moveCenter(screen_geometry.center())
        # Добавляем смещение: отодвигаем окно вверх на 50 пикселей
        window_geometry.moveTop(window_geometry.top() - 50)
        # Перемещаем главное окно по этим координатам
        self.move(window_geometry.topLeft())


    def check_credentials(self):
        login = self.login_field.text()
        password = self.password_field.text()
        password_hash = hashlib.sha256(password.encode()).hexdigest()

        # Загружаем данные пользователей
        with open('users.pickle', 'rb') as f:
            users = pickle.load(f)

        # Проверка учетных данных
        for user in users:
            if user['login'] == login and user['password'] == password_hash:
                user['active'] = True
                # Сохраняем обновленные данные пользователей
                with open('users.pickle', 'wb') as f:
                    pickle.dump(users, f)
                self.close()
                # Запуск основного окна
                video_stream = VideoStream()  # запуска основного окна
                video_stream.show()
                break
        else:
            QMessageBox.warning(self, 'Ошибка', 'Неверный логин или пароль')

def main():
    app = QApplication(sys.argv)
    login_window = LoginWindow()
    login_window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
