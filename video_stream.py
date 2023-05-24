import sys
import os
import cv2
import json
import datetime
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout, QHBoxLayout, QPushButton, QDesktopWidget
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import QThread, QTimer, Qt
from PyQt5.QtCore import pyqtSignal, pyqtSlot # face_detected = pyqtSignal(str, datetime.datetime) # сигнал для обнаружения лица
from PyQt5.QtWidgets import QMessageBox, QMainWindow
from image_viewer import ImageViewer  # импортируем класс ImageViewer


TEMP_RESOLUTION_FILE = "video_resolution.json"

class VideoCaptureThread(QThread):
    # face_detected = pyqtSignal(str, datetime.datetime) # сигнал для обнаружения лица
    close_window_signal = pyqtSignal()   # новый сигнал для закрытия окна
    error_signal = pyqtSignal(str)       # для определения сигнала ошибки
    show_image_signal = pyqtSignal(str)  # для открытия ImageViewer

    def __init__(self, camera_index=0):
        super().__init__()
        # super(VideoCaptureThread, self).__init__(parent)
        self.camera = cv2.VideoCapture(camera_index)
        self.camera_connected = self.camera.isOpened()
        if not self.camera_connected:
            print("Ошибка: Камера не найдена")
            self.error_signal.emit("Ошибка: Камера не найдена")
            return
        self.running = False

        # Установка разрешения видеопотока на 720p [1280, 720]
        self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)


    def run(self):
        if not self.camera_connected:
            return

        self.running = True
        frame_count = 0 # Тестовая заглушка для проверки кода
        while self.running:
            ret, self.frame = self.camera.read()
            # Распознавание лиц
            #face_id, detection_time = identify_face(self.frame)
            # if face_id is not None:  # РАБОЧЕЕ УСЛОВИЕ!!!
            face_id = 'ID.11'
            frame_count += 1
            if frame_count % 750 == 0:  # Тестовая заглушка для проверки кода
                print(frame_count)
                # отправляем сигнал для закрытия текущего окна
                #self.close_window_signal.emit()
                # отправляем сигнал для открытия ImageViewer при распознавании лица
                self.show_image_signal.emit(face_id) # face_id


    def stop(self):
        if not self.camera_connected:
            return

        self.running = False
        self.wait()
        self.camera.release()


    def change_resolution(self, width, height):
        if not self.camera_connected:
            return False

        self.camera.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
        new_width = self.camera.get(cv2.CAP_PROP_FRAME_WIDTH)
        new_height = self.camera.get(cv2.CAP_PROP_FRAME_HEIGHT)

        return new_width == width and new_height == height


class VideoStream(QWidget):
    error_signal = pyqtSignal(str) # определяем error_signal в классе VideoStream

    def __init__(self):
        super().__init__()
        # super(VideoStream, self).__init__(parent)
        self.init_ui()
        self.center_on_screen()  # Центрировать окно перед началом видеопотока
        # Создаем экземпляр VideoCaptureThread
        self.capture_thread = VideoCaptureThread()
        # Подключаем сигнал к слоту
        self.capture_thread.error_signal.connect(self.show_error_message)
        # Подключаем еще один сигнал к слоту
        self.capture_thread.close_window_signal.connect(self.close_window)
        # Подключаем еще один сигнал к слоту
        self.capture_thread.show_image_signal.connect(self.show_image_viewer)

        # Загружаем сохраненные настройки и устанавливаем их
        settings = self.load_settings()
        if settings:
            x, y, width, height = settings
            self.move(x, y)
            self.capture_thread.change_resolution(width, height)

            # Обновляем заголовок окна с текущим разрешением
            self.update_window_title(width, height)

        self.capture_thread.start()

        self.timer = QTimer(self)
        if not self.capture_thread.camera_connected:
            self.video_label.setText("Камера не найдена")
        else:
            self.timer.timeout.connect(self.update_video)
            self.timer.start(30)

    # Определяем слот для вывода сообщения об ошибке
    @pyqtSlot(str)
    def show_error_message(self, message):
        error_dialog = QMessageBox()
        error_dialog.setIcon(QMessageBox.Critical)
        error_dialog.setText(message)
        error_dialog.setWindowTitle("Ошибка")
        error_dialog.exec_()

    # Определяем слот для закрытия окна
    @pyqtSlot()
    def close_window(self):
        self.close() # закрыть текущее окно в главном потоке GUI

    # Определяем слот для открытия окна
    @pyqtSlot(str)
    def show_image_viewer(self, face_id):
        # Пути по умолчанию для Linux и Windows
        default_folder_linux = './Faces.Best'
        default_folder_windows = 'C:/Faces.Best'
        # Выбор папки по умолчанию в зависимости от операционной системы
        default_folder = default_folder_windows if os.name == 'nt' else default_folder_linux

        #self.image_viewer = ImageViewer(default_folder, face_id)
        print(face_id)
        self.close_window()
        # создаем новое окно и открываем его
        self.image_viewer = ImageViewer(default_folder, 'ID.11')
        self.image_viewer.show()


    def load_resolution(self):
        if os.path.exists(TEMP_RESOLUTION_FILE):
            with open(TEMP_RESOLUTION_FILE, "r") as f:
                res = json.load(f)
                return res["width"], res["height"]
        else:
            # Если файл не найден, то будет оптимальное разрешение (720p)
            return 1280, 720


    def init_ui(self):
        self.setWindowTitle('Видеопоток с USB-камеры [1280x720]')
        self.video_label = QLabel(self)
        self.video_label.setAlignment(Qt.AlignCenter)
        # Создаем размещение с кнопками разрешения
        self.resolution_buttons = QHBoxLayout()

        for resolution in ["1080p", "720p", "WSVGA", "VGA", "360p"]:
            button = QPushButton(resolution)
            button.clicked.connect(lambda checked, r=resolution: self.change_resolution(r))
            self.resolution_buttons.addWidget(button)

        self.action_buttons = QHBoxLayout()

        for label, func in [("Сотрудники", self.settings), ("Снимок", self.take_snapshot), ("Перезапуск", self.restart_video_stream)]:
            button = QPushButton(label)
            button.clicked.connect(func)
            self.action_buttons.addWidget(button)

        vbox = QVBoxLayout(self)  # Создаем vbox перед добавлением размещений
        vbox.addWidget(self.video_label)
        vbox.addLayout(self.resolution_buttons)  # Добавляем размещение с кнопками разрешения в основной контейнер
        vbox.addLayout(self.action_buttons)
        self.setLayout(vbox)


    def update_video(self):
        if not self.capture_thread.camera_connected or not hasattr(self.capture_thread, 'frame') or self.capture_thread.frame is None:
            return
        rgb_image = cv2.cvtColor(self.capture_thread.frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        qt_image = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(qt_image)
        self.video_label.setPixmap(pixmap)


    # "Сотрудники"
    def settings(self):
        print("Сотрудники")
        # Пути по умолчанию для Linux и Windows
        default_folder_linux = './Faces.Best'
        default_folder_windows = 'C:/Faces.Best'
        # Выбор папки по умолчанию в зависимости от операционной системы
        default_folder = default_folder_windows if os.name == 'nt' else default_folder_linux
        # закрываем текущее окно
        self.close_window()
        # создаем новое окно и открываем его
        self.image_viewer = ImageViewer(default_folder, 'ID.11')
        self.image_viewer.show()


    # "Снимок"
    def take_snapshot(self):
        if not hasattr(self.capture_thread, 'frame') or self.capture_thread.frame is None:
            print("Ошибка: Нет доступных кадров для снимка")
            self.error_signal.emit("Ошибка: Нет доступных кадров для снимка")
            return

        snapshot = self.capture_thread.frame.copy()
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        file_name = f"photo_{timestamp}.jpg"

        cv2.imwrite(file_name, snapshot)


    # "Перезапуск"
    def restart_video_stream(self):
        self.close()             # Закрываем текущее окно
        self.__init__()          # Инициализируем новое окно
        self.show()              # Показываем новое окно
        self.center_on_screen()  # Центрируем новое окно на экране


    def closeEvent(self, event):
        if hasattr(self, 'timer'):
            self.timer.stop()
        self.capture_thread.stop()
        event.accept()


    def center_on_screen(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())


    def showEvent(self, event):
        super().showEvent(event)
        self.center_on_screen()


    def save_settings(self, x, y, width, height):
        settings = {"x": x, "y": y, "width": width, "height": height}
        with open(TEMP_RESOLUTION_FILE, "w") as f:
            json.dump(settings, f)


    def load_settings(self):
        if os.path.exists(TEMP_RESOLUTION_FILE):
            with open(TEMP_RESOLUTION_FILE, "r") as f:
                settings = json.load(f)
                return settings["x"], settings["y"], settings["width"], settings["height"]
        else:
            return None


    def change_resolution(self, resolution):
        if hasattr(self, 'timer'): # Это предотвратит попытку остановить таймер, если он еще не был инициализирован
            self.timer.stop()

        res_dict = {"1080p": (1920, 1080), "720p": (1280, 720), "WSVGA": (1024, 576), "VGA": (640, 480), "360p": (480, 360)}

        if resolution in res_dict:
            width, height = res_dict[resolution]

            # Останавливаем текущий поток видеозахвата и освобождаем камеру
            self.timer.stop()
            self.capture_thread.stop()

            # Создаем и запускаем новый поток видеозахвата с новым разрешением
            self.capture_thread = VideoCaptureThread()
            # Изменяем разрешение !!! Важен порядок команд !!!
            self.capture_thread.camera.set(cv2.CAP_PROP_FRAME_WIDTH, width)
            self.capture_thread.camera.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
            self.capture_thread.start()

            self.timer = QTimer(self)
            self.timer.timeout.connect(self.update_video)
            self.timer.start(30)

            # Обновляем заголовок окна с новым разрешением
            self.update_window_title(width, height)
            # Изменяем размер виджета в соответствии с новым разрешением
            self.resize_video_widget(width, height)

            # Обновляем размер окна с виджетами
            self.adjustSize()

            # Сохраняем настройки окна и разрешение
            x, y = self.pos().x(), self.pos().y()
            self.save_settings(x, y, width, height)

            # После изменения размера виджета обновляем его положение
            self.center_on_screen()

    def update_window_title(self, width, height):
        self.setWindowTitle(f"Видеопоток с USB-камеры [{width}x{height}]")


    def resize_video_widget(self, width, height):
        screen_geometry = QDesktopWidget().availableGeometry()
        screen_width = screen_geometry.width()
        screen_height = screen_geometry.height()

        # Проверяем, подходит ли новый размер виджета для экрана
        if width > screen_width or height > screen_height:
            width = min(width, screen_width)
            height = min(height, screen_height)

        # Изменяем размер виджета
        self.video_label.setFixedSize(int(width), int(height))
        self.adjustSize()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    video_stream = VideoStream()
    video_stream.show()
    sys.exit(app.exec_())
