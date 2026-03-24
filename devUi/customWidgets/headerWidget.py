from Qt import QtCore, QtWidgets

class HeaderWidget(QtWidgets.QWidget):
    
    _WIDGET_STYLESHEET = (
        """
        QWidget#ColorWidget {
        background-color : rgb(#COLOR#) ;
        border-radius : 5px
        }
        """
    )

    def __init__(self, parent = None, title : str = "header", color: tuple[int, int, int] = (20, 100, 100)):
        super().__init__(parent)

        # Color Widget
        color_widget = QtWidgets.QWidget()
        color_widget.setObjectName("ColorWidget")
        color = [str(c) for c in color]
        color_widget.setStyleSheet(self._WIDGET_STYLESHEET.replace("#COLOR#", ",".join(color)) )
        color_widget.setFixedHeight(5)

        # Label Widget
        title_label = QtWidgets.QLabel(title)
        title_label.setAlignment(QtCore.Qt.AlignCenter)

        # Layout
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(title_label)
        layout.addWidget(color_widget)
        layout.addSpacing(5)
        self.setLayout(layout)

if __name__ == '__main__':
    from devMaya.tool_launcher import launch_maya_tool
    launch_maya_tool(HeaderWidget)