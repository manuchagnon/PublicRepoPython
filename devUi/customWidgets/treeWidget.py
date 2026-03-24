from Qt import QtCore, QtWidgets, QtGui


class TreeWidget(QtWidgets.QTreeWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        self._placeholder_text = ""
        self.setRootIsDecorated(False)

    def set_placeholder_text(self, text):
        """ Set text to display when the list is empty """
        self._placeholder_text = text

    def placeholder_text(self):
        """ Returns placeholder text shown when list is empty """
        return self._placeholder_text

    def paintEvent(self, event):
        """ Paint placeholder message if tree is empty """

        # Call super, bail out if there is no placeholder to show
        super().paintEvent(event)
        if self.model().rowCount(QtCore.QModelIndex()):
            return
        if not self._placeholder_text:
            return

        # Get painter
        viewport = self.viewport()
        rect = viewport.rect()
        painter = QtGui.QPainter(viewport)

        # Place text
        text_rect = painter.fontMetrics().boundingRect(self._placeholder_text)
        text_rect.moveCenter(rect.center())
        painter.drawText(text_rect, QtCore.Qt.AlignCenter, self._placeholder_text)

    def set_items(self, items: dict | list[str]):

        if isinstance(items, dict):
            self.addTopLevelItems(items)

        if isinstance(items, list):
            self.addTopLevelItems(items)



