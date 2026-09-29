import sys
import cv2
from PySide6 import QtCore, QtWidgets, QtGui
from PySide6.QtWidgets import QLabel, QPushButton, QFileDialog, QVBoxLayout, QHBoxLayout, QFrame, QScrollArea
from PIL import Image
import pytesseract
from braille_constants import CHARACTERS_UNICODE


class Ventana(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle('Conversor de Imágenes a Braille')
        self.path_original_image = ''

        # Layout principal
        self.layout = QHBoxLayout(self)

        # Sección 1: Cuadro para la imagen
        self.label_original_image = QLabel(self)
        self.label_original_image.setAlignment(QtCore.Qt.AlignCenter)
        self.label_original_image.setFixedSize(400, 400)  # Tamaño de imagen ajustado

        frame_image = QFrame(self)
        frame_image_layout = QVBoxLayout(frame_image)
        frame_image_layout.addWidget(self.label_original_image)

        self.btn_file = QPushButton("Seleccionar imagen...")
        self.btn_file.clicked.connect(self.load_image)
        frame_image_layout.addWidget(self.btn_file)

        # Sección 2: Cuadro para Braille
        self.label_braille_text = QLabel("Texto en Braille:", alignment=QtCore.Qt.AlignLeft)
        self.label_braille_text.setStyleSheet("margin: 0; padding: 0;")  # Sin márgenes ni padding

        self.text_braille_output = QLabel("", self)
        self.text_braille_output.setWordWrap(True)  # Permitir el ajuste de línea
        self.text_braille_output.setStyleSheet("margin: 0; padding: 0;")  # Sin padding

        # Scroll para Braille
        scroll_braille = QScrollArea(self)
        scroll_braille.setWidgetResizable(True)
        scroll_braille.setWidget(self.text_braille_output)
        scroll_braille.setFixedHeight(150)  # Ajustar altura

        frame_braille = QFrame(self)
        frame_braille_layout = QVBoxLayout(frame_braille)
        frame_braille_layout.setContentsMargins(5, 5, 5, 5)  # Márgenes pequeños
        frame_braille_layout.setSpacing(5)
        frame_braille_layout.addWidget(self.label_braille_text)
        frame_braille_layout.addWidget(scroll_braille)

        # Sección 3: Cuadro para el texto extraído
        self.label_extracted_text = QLabel("Texto extraído:", alignment=QtCore.Qt.AlignLeft)
        self.label_extracted_text.setStyleSheet("margin: 0; padding: 0;")

        self.text_extracted_output = QLabel("", self)
        self.text_extracted_output.setWordWrap(True)
        self.text_extracted_output.setStyleSheet("margin: 0; padding: 0;")

        # Scroll para texto extraído
        scroll_extracted = QScrollArea(self)
        scroll_extracted.setWidgetResizable(True)
        scroll_extracted.setWidget(self.text_extracted_output)
        scroll_extracted.setFixedHeight(150)

        frame_extracted = QFrame(self)
        frame_extracted_layout = QVBoxLayout(frame_extracted)
        frame_extracted_layout.setContentsMargins(5, 5, 5, 5)
        frame_extracted_layout.setSpacing(5)
        frame_extracted_layout.addWidget(self.label_extracted_text)
        frame_extracted_layout.addWidget(scroll_extracted)

        # Sección de texto combinada (Braille y texto extraído)
        frame_text_combined = QFrame(self)
        frame_text_combined_layout = QVBoxLayout(frame_text_combined)
        frame_text_combined_layout.setContentsMargins(0, 0, 0, 150)
        frame_text_combined_layout.setSpacing(50)
        frame_text_combined_layout.addWidget(frame_braille)   # Braille arriba
        frame_text_combined_layout.addWidget(frame_extracted)  # Texto extraído abajo

        # Añadir todos los cuadros al layout principal
        self.layout.addWidget(frame_image)         # Imagen en el lado izquierdo
        self.layout.addWidget(frame_text_combined) # Cuadros de texto en el lado derecho

        # Ajustes de margen para layout principal
        self.layout.setContentsMargins(20, 20, 20, 20)
        self.layout.setSpacing(20)

        # Centrar ventana
        self.setGeometry(100, 100, 800, 600)
        self.center()

    def center(self):
        """Centrar la ventana en la pantalla."""
        screen = QtWidgets.QApplication.primaryScreen()
        size = screen.size()
        self.move((size.width() - self.width()) // 2, (size.height() - self.height()) // 2)

    def load_image(self):
        dlg = QFileDialog()
        dlg.setFileMode(QFileDialog.AnyFile)
        dlg.selectNameFilter("Images (*.png *.jpg *.jpeg)")
        if dlg.exec():
            filenames = dlg.selectedFiles()
            self.path_original_image = filenames[0]
            self.display_image()
            self.translate_image_to_braille(self.path_original_image)

    def display_image(self):
        pixmap = QtGui.QPixmap(self.path_original_image)
        pixmap = pixmap.scaled(self.label_original_image.size(), QtCore.Qt.KeepAspectRatio,
                               QtCore.Qt.SmoothTransformation)
        self.label_original_image.setPixmap(pixmap)

    def translate_image_to_braille(self, image_path):
        img = cv2.imread(image_path)
        gray_image = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        thresh, im_bw = cv2.threshold(gray_image, 210, 230, cv2.THRESH_BINARY)

        # Remover ruido
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 1))
        no_noise = cv2.morphologyEx(im_bw, cv2.MORPH_CLOSE, kernel)
        no_noise = cv2.medianBlur(no_noise, 3)

        # OCR
        img_pil = Image.fromarray(no_noise)
        ocr_result = pytesseract.image_to_string(img_pil, lang='eng')

        # Mostrar texto extraído
        self.text_extracted_output.setText(ocr_result)

        # Convertir a Braille
        braille_result = self.convertir_a_braille(ocr_result)
        self.text_braille_output.setText(braille_result)

    def convertir_a_braille(self, text):
        text = text.lower()
        braille_text = ''.join(CHARACTERS_UNICODE.get(char, char) for char in text)
        return braille_text


if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    widget = Ventana()
    widget.resize(800, 600)
    widget.show()
    sys.exit(app.exec())
