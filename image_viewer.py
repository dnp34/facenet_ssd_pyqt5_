import os
import sys
from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QHBoxLayout, QPushButton, QLineEdit, QDesktopWidget
from PyQt5.QtWidgets import QApplication, QFileDialog, QTextEdit
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtCore import QSize, Qt

class ImageViewer(QWidget):
    def __init__(self, image_folder, ID='ID.01'):
        super().__init__()
        person_data = f'Степанов Григорий Андреевич\nРуководитель Отдела управления имуществом' \
                      f'\ngreg_s@piligrim.ru\n12.12.1981\nmob.:+7962-113-8877\n{id}'

        self.image_folder = image_folder
        self.ID = ID
        self.images = [os.path.join(image_folder, f) for f in sorted(os.listdir(image_folder)) if f.endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp'))]
        self.current_image_index = 0

        # Задаем индекс текущего изображения на основе имени файла вида 'ID.11.jpg'
        initial_image_name = self.ID + '.jpg'
        initial_image_path = os.path.join(self.image_folder, initial_image_name)
        if initial_image_path in self.images:
            self.current_image_index = self.images.index(initial_image_path)

        self.init_ui(person_data)

    def init_ui(self, person_data):
        self.setWindowTitle('Сотрудники компании "Пилигрим"')

        self.label = QLabel(self)
        self.pixmap = QPixmap(self.images[self.current_image_index])
        self.label.setPixmap(self.pixmap)

        self.first_btn = QPushButton('⏮', self)
        self.first_btn.clicked.connect(self.first_image)

        self.prev_btn = QPushButton('⏪', self)
        self.prev_btn.clicked.connect(self.previous_image)

        self.center_btn = QPushButton('⏺', self)
        self.center_btn.clicked.connect(self.center_image)

        self.next_btn = QPushButton('⏩', self)
        self.next_btn.clicked.connect(self.next_image)

        self.last_btn = QPushButton('⏭', self)
        self.last_btn.clicked.connect(self.last_image)

        self.stop_btn = QPushButton('--- ОТКАЗАТЬ ---', self)
        self.stop_btn.setStyleSheet("font-size: 24px")
        self.stop_btn.setFixedHeight(70) # Задаем высоту виджета
        self.stop_btn.clicked.connect(self.prohibited)

        self.month_btn = QPushButton('📊', self)
        self.month_btn.setStyleSheet("font-size: 24px")
        self.month_btn.setFixedSize(70, 70)
        self.month_btn.clicked.connect(self.calendar)

        self.pass_btn = QPushButton('🆗  ПРОПУСТИТЬ', self)
        self.pass_btn.setStyleSheet("font-size: 24px")
        self.pass_btn.setFixedHeight(70) # Задаем высоту виджета
        self.pass_btn.clicked.connect(self.allowed)

        self.file_name_edit = QLineEdit(self)
        # self.file_name_edit.setPlaceholderText('ID')
        self.file_name_edit.setPlaceholderText(self.ID)
        self.file_name_edit.returnPressed.connect(self.load_image_by_name)
        self.file_name_edit.setFixedWidth(80)  # Задаем ширину виджета


        #self.adds_btn = QPushButton('ДОБАВИТЬ СОТРУДНИКА', self)
        #self.adds_btn.clicked.connect(self.add_person)
        #self.adds_btn.setFixedHeight(70) # Задаем высоту виджета

        #print("First button width:", self.first_btn.sizeHint().width())
        #print("Previous button width:", self.prev_btn.sizeHint().width())
        #print("Center button width:", self.center_btn.sizeHint().width())
        #print("Next button width:", self.next_btn.sizeHint().width())
        #print("Last button width:", self.last_btn.sizeHint().width())

        # виджет QTextEdit для отображения текста
        self.text_widget = QTextEdit(self)
        self.text_widget.setReadOnly(True)  # сделаем его только для чтения
        self.text_widget.setFixedHeight(110) # Задаем высоту виджета
        self.text_widget.setStyleSheet("font-size: 18px")

        hbox = QHBoxLayout()
        hbox.addWidget(self.first_btn)
        hbox.addWidget(self.prev_btn)
        hbox.addWidget(self.center_btn)
        hbox.addWidget(self.file_name_edit)  # добавляем виджет QLineEdit справа от кнопки "середина"
        hbox.addWidget(self.next_btn)
        hbox.addWidget(self.last_btn)

        bigs = QHBoxLayout()
        bigs.addWidget(self.stop_btn)
        bigs.addWidget(self.month_btn)
        bigs.addWidget(self.pass_btn)


        vbox = QVBoxLayout(self)
        vbox.addWidget(self.label)
        vbox.addWidget(self.text_widget) # виджет текста в вертикальный слой vbox
        vbox.addLayout(hbox)
        vbox.addLayout(bigs)

        self.setLayout(vbox)
        self.set_text(person_data)
        # Центрировать окно на экране
        #self.center()
        # Получаем геометрию экрана
        screen_geometry = QApplication.desktop().availableGeometry()
        # Получаем геометрию окна
        window_geometry = self.frameGeometry()
        # Устанавливаем центр окна в центр экрана
        window_geometry.moveCenter(screen_geometry.center())
        # Добавляем смещение: отодвигаем окно вверх на 250 пикселей
        window_geometry.moveTop(window_geometry.top() - 250)
        # Перемещаем главное окно по этим координатам
        self.move(window_geometry.topLeft())

    def center(self):
        screen = QDesktopWidget().screenGeometry()
        window = self.geometry()
        self.move((screen.width() - window.width()) // 2, (screen.height() - window.height()) // 2)

    def first_image(self):
        self.current_image_index = 0
        self.update_image()

    def previous_image(self):
        self.current_image_index -= 1
        if self.current_image_index < 0:
            self.current_image_index = 0
        self.update_image()

    def center_image(self):
        self.current_image_index = len(self.images) // 2
        self.update_image()

    def next_image(self):
        self.current_image_index += 1
        if self.current_image_index >= len(self.images):
            self.current_image_index = len(self.images) - 1
        self.update_image()

    def last_image(self):
        self.current_image_index = len(self.images) - 1
        self.update_image()

    def allowed(self):
        pass

    def prohibited(self):
        pass

    def calendar(self):
        pass

    def load_image_by_name(self):
        file_name = self.file_name_edit.text()
        if not file_name:
            return

        file_path = os.path.join(self.image_folder, f"{file_name}.jpg")
        if os.path.exists(file_path):
            self.current_image_index = self.images.index(file_path)
            self.update_image()

    def update_image(self):
        self.pixmap.load(self.images[self.current_image_index])
        self.label.setPixmap(self.pixmap)

        # Выводим размеры виджета для изображения
        # print(f'Image widget width: {self.label.size().width()} x {self.label.size().height()}')

        # Получаем имя файла без расширения и устанавливаем его в виджет QLineEdit
        file_name = os.path.splitext(os.path.basename(self.images[self.current_image_index]))[0]
        self.file_name_edit.setText(file_name)

        # получаем размер файла
        file_size = os.path.getsize(self.images[self.current_image_index]) / 1024  # размер в килобайтах

        # Выводим новый текст в виджет QTextEdit
        image_info = f'Сотрудник: {file_name}' \
                     f'\nРазмер изображения: {self.pixmap.width()}x{self.pixmap.height()} пикселей' \
                     f'\nРазмер файла: {file_size:.2f} КБ'
        self.set_text(image_info)


    # метод для установки текста в виджете QTextEdit
    def set_text(self, text):
        self.text_widget.setText(text)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    id = 'ID.11'
    # image_folder = './Faces.Best'  # путь к папке с изображениями
    # viewer = ImageViewer(image_folder, id)

    # Пути по умолчанию для Linux и Windows
    default_folder_linux = '/app/Faces.Best'
    default_folder_windows = 'C:/Faces.Best'

    # Выберите папку по умолчанию в зависимости от операционной системы
    default_folder = default_folder_windows if os.name == 'nt' else default_folder_linux

    if not os.path.exists(default_folder):
        print(f"Папка {default_folder} не найдена. Запускается интерактивный выбор папки.")
        # default_folder = QFileDialog.getExistingDirectory(None, "Выберите папку")
        dialog = QFileDialog()
        dialog.setWindowFlags(Qt.WindowStaysOnTopHint)  # устанавливаем окно поверх остальных
        dialog.setFileMode(QFileDialog.Directory)
        dialog.setOption(QFileDialog.ShowDirsOnly)

        if dialog.exec_():
            default_folder = dialog.selectedFiles()[0]

    viewer = ImageViewer(default_folder, id)
    #viewer.set_text(f'Степанов Григорий Андреевич\nРуководитель Отдела управления имуществом\ngreg_s@piligrim.ru\n12.12.1981\nmob.:+7962-113-8877\n{id}')
    viewer.show()
    sys.exit(app.exec_())
