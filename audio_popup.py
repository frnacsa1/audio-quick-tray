import sys
import sounddevice as sd
from PyQt6.QtCore import QTimer, Qt
from PyQt6.QtGui import QIcon, QAction, QPixmap, QPainter, QColor
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QComboBox, QPushButton, QProgressBar, QSystemTrayIcon, QMenu
)

def create_tray_icon_pixmap():
    """Crea un'icona grafica semplice per la System Tray."""
    pixmap = QPixmap(32, 32)
    pixmap.fill(QColor(0, 0, 0, 0))
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    painter.setBrush(QColor(107, 70, 193)) # Colore Viola Accent
    painter.setPen(Qt.PenStyle.NoPen)
    painter.drawEllipse(2, 2, 28, 28)
    painter.setBrush(QColor(255, 255, 255))
    painter.drawEllipse(10, 10, 12, 12)
    painter.end()
    return QIcon(pixmap)

class AudioSelectorApp(QWidget):
    def __init__(self):
        super().__init__()
        self.countdown_seconds = 5
        self.init_ui()
        self.load_audio_devices()
        self.setup_timer()

    def init_ui(self):
        self.setWindowTitle("Selettore Audio QuickTray")
        self.setFixedSize(400, 320)
        self.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Tool)

        layout = QVBoxLayout()
        layout.setSpacing(12)

        # Header
        title = QLabel("🔊 Configurazione Audio")
        title.setStyleSheet("font-size: 16px; font-weight: bold; color: #6b46c1;")
        layout.addWidget(title)

        # Dispositivo di Input (Microfono)
        layout.addWidget(QLabel("🎤 Ingresso (Microfono):"))
        self.combo_input = QComboBox()
        layout.addWidget(self.combo_input)

        # Dispositivo di Output (Altoparlanti/Cuffie)
        layout.addWidget(QLabel("🎧 Uscita (Altoparlanti/Cuffie):"))
        self.combo_output = QComboBox()
        layout.addWidget(self.combo_output)

        # Timer & Status
        self.lbl_timer = QLabel(f"Riduzione automatica nella tray tra {self.countdown_seconds}s...")
        self.lbl_timer.setStyleSheet("color: #718096; font-style: italic;")
        layout.addWidget(self.lbl_timer)

        # Pulsanti
        btn_layout = QHBoxLayout()
        self.btn_confirm = QPushButton("Conferma e Minimizza")
        self.btn_confirm.setStyleSheet("background-color: #6b46c1; color: white; padding: 6px; font-weight: bold;")
        self.btn_confirm.clicked.connect(self.hide_to_tray)

        self.btn_cancel_timer = QPushButton("Blocca Timer")
        self.btn_cancel_timer.clicked.connect(self.stop_timer)

        btn_layout.addWidget(self.btn_confirm)
        btn_layout.addWidget(self.btn_cancel_timer)
        layout.addLayout(btn_layout)

        self.setLayout(layout)

    def load_audio_devices(self):
        """Carica i dispositivi audio disponibili nel sistema."""
        try:
            devices = sd.query_devices()
            default_input = sd.default.device[0]
            default_output = sd.default.device[1]

            for i, dev in enumerate(devices):
                name = dev['name']
                if dev['max_input_channels'] > 0:
                    self.combo_input.addItem(f"{name}", i)
                    if i == default_input:
                        self.combo_input.setCurrentIndex(self.combo_input.count() - 1)
                
                if dev['max_output_channels'] > 0:
                    self.combo_output.addItem(f"{name}", i)
                    if i == default_output:
                        self.combo_output.setCurrentIndex(self.combo_output.count() - 1)
        except Exception as e:
            self.combo_input.addItem("Impossibile rilevare dispositivi")
            self.combo_output.addItem("Impossibile rilevare dispositivi")

    def setup_timer(self):
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_timer)
        self.timer.start(1000)

    def update_timer(self):
        self.countdown_seconds -= 1
        if self.countdown_seconds > 0:
            self.lbl_timer.setText(f"Riduzione automatica nella tray tra {self.countdown_seconds}s...")
        else:
            self.timer.stop()
            self.hide_to_tray()

    def stop_timer(self):
        if self.timer.isActive():
            self.timer.stop()
            self.lbl_timer.setText("Timer bloccato. Scegli le impostazioni e conferma.")

    def hide_to_tray(self):
        self.timer.stop()
        self.hide()
        tray_icon.showMessage(
            "Audio QuickTray",
            "L'applicazione è attiva nell'area di notifica (Tray).",
            QSystemTrayIcon.MessageIcon.Information,
            2000
        )

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)

    window = AudioSelectorApp()

    # Inizializzazione System Tray Icon
    tray_icon = QSystemTrayIcon(create_tray_icon_pixmap(), app)
    
    tray_menu = QMenu()
    show_action = QAction("🔊 Apri Selettore Audio", app)
    show_action.triggered.connect(window.show)
    exit_action = QAction("❌ Esci", app)
    exit_action.triggered.connect(app.quit)

    tray_menu.addAction(show_action)
    tray_menu.addSeparator()
    tray_menu.addAction(exit_action)

    tray_icon.setContextMenu(tray_menu)
    tray_icon.activated.connect(lambda reason: window.show() if reason == QSystemTrayIcon.ActivationReason.Trigger else None)
    tray_icon.show()

    window.show()
    sys.exit(app.exec())