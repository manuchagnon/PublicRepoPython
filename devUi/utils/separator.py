from PySide6 import QtWidgets, QtCore, QtGui

class Separator(QtWidgets.QWidget):
    def __init__(self, parent=None, height = 1,  width = 1, space = 10, text=""):
        super().__init__()

        self.label = QtWidgets.QLabel(text)

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.label)

        self.height = height
        self.width = width
        self.space = space
        self.text = text

        self.setLayout(layout)
        self.setFixedWidth(width * space)
        self.setFixedHeight(height * space)

    def set_height(self, height):
        self.height = height
        self.setFixedHeight(height * self.space)

    def set_width(self, width):
        self.width = width
        self.setFixedWidth(width * self.space)

    def set_text(self, text):
        self.label.setText(text)


