from Qt import QtWidgets, QtCore, QtGui

from devUi.utils.api import get_color
from devMaya.utils.api import create_jnts, undo_chunk
from devUi.customWidgets.headerWidget import HeaderWidget

class JointWidget(QtWidgets.QWidget):

    def __init__(self, parent=None):
        super().__init__()

        # Suffix
        self._line_suffix = QtWidgets.QLineEdit()
        self._line_suffix.setPlaceholderText("None")

        # Button
        button = QtWidgets.QPushButton("Create Joints under selection")
        button.clicked.connect(self._create_joint_on_selection)
        button.setFixedHeight(50)

        # Form Layout
        layout = QtWidgets.QFormLayout()
        layout.setLabelAlignment(QtCore.Qt.AlignRight)
        layout.addRow("Suffix :", self._line_suffix)
        layout.addRow(button)

        # Main Layout
        main_layout = QtWidgets.QVBoxLayout()
        main_layout.addWidget(HeaderWidget(title = "Joint", color = get_color("pink")))
        main_layout.addLayout(layout)

        self.setLayout(main_layout)

    @undo_chunk
    def _create_joint_on_selection(self):
        """
        Call the custom maya function to create the joints under selection
        """

        print(">> Creating Joint under Selection")

        suffix = self._line_suffix.text()

        create_jnts(suffix=suffix, in_autorig=False)