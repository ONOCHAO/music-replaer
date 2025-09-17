import sys
import time
import pygame
from mutagen.mp3 import MP3
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QFileDialog, QMessageBox, QLabel, QSlider
)
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QIcon
from PyQt5 import QtCore
from form1 import Ui_MainWindow


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # Инициализация флагов
        self.current_file = None
        self.duration = 0
        self.start_time = 0
        self.is_paused = False

        # Удаляем кнопку "плей", если есть
        if hasattr(self.ui, "pushButton_4"):
            self.ui.pushButton_4.setParent(None)

        # Название трека по центру
        self.track_label = QLabel("🎵 Нет выбранного файла")
        self.track_label.setAlignment(Qt.AlignCenter)
        self.track_label.setStyleSheet("color: #76c7c0; font-size: 16px; font-weight: bold;")
        self.ui.gridLayout_2.addWidget(self.track_label, 1, 0, 1, self.ui.gridLayout_2.columnCount())

        # Добавим слайдер вручную
        self.ui.progressSlider = QSlider(Qt.Horizontal, self)
        self.ui.progressSlider.setGeometry(20, 530, 660, 20)
        self.ui.progressSlider.setMinimum(0)
        self.ui.progressSlider.setMaximum(100)
        self.ui.progressSlider.setValue(0)
        self.ui.progressSlider.setStyleSheet("""
            QSlider::groove:horizontal {
                border: 1px solid #999;
                height: 8px;
                background: #3a3a3a;
                margin: 2px 0;
                border-radius: 4px;
            }
            QSlider::handle:horizontal {
                background: #76c7c0;
                border: 1px solid #5c5c5c;
                width: 14px;
                margin: -4px 0;
                border-radius: 7px;
            }
        """)

        # Иконки кнопок
        self.ui.pushButton_5.setIcon(QIcon("icons/backward.png"))
        self.ui.pushButton_5.setText("")
        self.ui.pushButton_5.setIconSize(QtCore.QSize(32, 32))

        self.ui.pushButton_6.setIcon(QIcon("icons/forward.png"))
        self.ui.pushButton_6.setText("")
        self.ui.pushButton_6.setIconSize(QtCore.QSize(32, 32))

        self.ui.pushButton_7.setIcon(QIcon("icons/pause.png"))
        self.ui.pushButton_7.setText("")
        self.ui.pushButton_7.setIconSize(QtCore.QSize(32, 32))

        # Инициализация pygame
        pygame.mixer.init()

        # Таймер
        self.timer = QTimer()
        self.timer.setInterval(1000)
        self.timer.timeout.connect(self.update_progress)

        self.init_signals()
        self.apply_style()

    def apply_style(self):
        self.setStyleSheet("""
            QWidget {
                background-color: #121212;
                color: #e0e0e0;
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                font-size: 14px;
            }
            QPushButton {
                background-color: #1f1f1f;
                border: 1px solid #444;
                border-radius: 6px;
                padding: 8px 12px;
                color: #e0e0e0;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #2c2c2c;
                border-color: #76c7c0;
            }
            QPushButton:pressed {
                background-color: #3a3a3a;
                border-color: #4ea3a3;
            }
            QProgressBar {
                border: 1px solid #444;
                border-radius: 6px;
                background-color: #222;
                color: #eee;
                text-align: center;
                padding: 2px;
            }
            QProgressBar::chunk {
                background-color: #76c7c0;
                border-radius: 6px;
            }
        """)

    def init_signals(self):
        self.ui.pushButton.clicked.connect(self.load_music)
        self.ui.pushButton_2.clicked.connect(self.play_music)
        self.ui.pushButton_5.clicked.connect(self.stop_music)
        self.ui.pushButton_6.clicked.connect(self.play_music)
        self.ui.pushButton_7.clicked.connect(self.pause_unpause)
        self.ui.pushButton_3.clicked.connect(
            lambda: QMessageBox.information(self, "О программе", "🎧 MP3 плеер на PyQt5 + pygame.")
        )
        self.ui.progressSlider.sliderReleased.connect(self.seek_music)

    def load_music(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Выберите MP3 файл", "", "MP3 Files (*.mp3)"
        )
        if file_path:
            try:
                audio = MP3(file_path)
                self.duration = int(audio.info.length)
                pygame.mixer.music.load(file_path)
                self.current_file = file_path

                self.ui.progressSlider.setMaximum(self.duration)
                self.ui.progressSlider.setValue(0)

                self.ui.progressBar.setMaximum(self.duration)
                self.ui.progressBar.setValue(0)

                self.track_label.setText(f"🎵 {file_path.split('/')[-1]}")
                QMessageBox.information(self, "Файл загружен", f"Загружен файл:\n{file_path}")
            except Exception as e:
                QMessageBox.critical(self, "Ошибка загрузки", str(e))

    def play_music(self):
        if self.current_file:
            pygame.mixer.music.play()
            self.start_time = time.time()
            self.is_paused = False
            self.ui.pushButton_7.setIcon(QIcon("icons/pause.png"))
            self.timer.start()
        else:
            QMessageBox.warning(self, "Нет файла", "Сначала выбери MP3-файл через кнопку 'Файлы'.")

    def pause_unpause(self):
        if self.current_file:
            if not self.is_paused:
                pygame.mixer.music.pause()
                self.timer.stop()
                self.is_paused = True
                self.ui.pushButton_7.setIcon(QIcon("icons/play.png"))
            else:
                pygame.mixer.music.unpause()
                self.start_time = time.time() - self.ui.progressSlider.value()
                self.timer.start()
                self.is_paused = False
                self.ui.pushButton_7.setIcon(QIcon("icons/pause.png"))
        else:
            QMessageBox.warning(self, "Нет файла", "Сначала выбери MP3-файл через кнопку 'Файлы'.")

    def stop_music(self):
        pygame.mixer.music.stop()
        self.timer.stop()
        self.is_paused = False
        self.ui.pushButton_7.setIcon(QIcon("icons/pause.png"))
        self.ui.progressBar.setValue(0)
        self.ui.progressSlider.setValue(0)

    def update_progress(self):
        if pygame.mixer.music.get_busy():
            elapsed = int(time.time() - self.start_time)
            self.ui.progressSlider.setValue(elapsed)
            self.ui.progressBar.setValue(elapsed)
            if elapsed >= self.duration:
                self.timer.stop()
        else:
            self.timer.stop()

    def seek_music(self):
        if self.current_file:
            target_second = self.ui.progressSlider.value()
            try:
                pygame.mixer.music.stop()
                pygame.mixer.music.play(start=float(target_second))
                self.start_time = time.time() - target_second
                self.timer.start()
            except Exception as e:
                QMessageBox.warning(self, "Ошибка перемотки", f"Не удалось перемотать: {str(e)}")


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.setWindowTitle("🎧 Музыкальный плеер")
    window.resize(700, 550)
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
