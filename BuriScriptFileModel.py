import sys
import os
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import shutil
from pathlib import Path
from handle_logs import BuriScriptLogHandler


TREEVIEW_STYLE_SHEET = \
                        """
                        QTreeView::item:hover{
                            background-color: #323437;
                            color: white;
                        }
                        """


class CustomTreeView(QTreeView):
    def __init__(self, path: str, home_path, parent_window: QMainWindow, parent=None):
        super().__init__(parent)
        self.setStyleSheet(TREEVIEW_STYLE_SHEET)
        self.editor_home_path = home_path
        self.current_working_directory = path
        self._parent_window = parent_window

        self.dir_model = QFileSystemModel()
        self.dir_model.setRootPath(self.current_working_directory)
        self.setModel(self.dir_model)
        self.setRootIndex(self.dir_model.index(self.current_working_directory))
        self.setSelectionMode(QTreeView.SingleSelection)

        self.setSortingEnabled(True)
        self.header().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.setIndentation(10)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setEditTriggers(QTreeView.NoEditTriggers)
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.custom_context_menu_tree_view)
        self.doubleClicked.connect(self.on_clicked)

        self.dir_model.setReadOnly(False)

        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.setDropIndicatorShown(True)
        self.setDragDropMode(QAbstractItemView.DragDrop)

        self.rename_shortcut = QShortcut(QKeySequence("F2"), self)
        self.delete_file_shortcut = QShortcut(QKeySequence("Delete"), self)
        self.make_new_file_shortcut = QShortcut(QKeySequence("Ctrl+Shift+N"), self)
        self.rename_shortcut.activated.connect(self.on_rename)
        self.delete_file_shortcut.activated.connect(self.on_delete_file)
        self.make_new_file_shortcut.activated.connect(self.on_make_new_file)

    def dragEnterEvent(self, e: QDragEnterEvent) -> None:
        if e.mimeData().hasUrls():
            e.accept()
        else:
            e.ignore()

    def dropEvent(self, e: QDropEvent) -> None:
        try:
            root_path = Path(self.dir_model.rootPath())
            if e.mimeData().hasUrls():
                for url in e.mimeData().urls():
                    path = Path(url.toLocalFile())
                    if path.is_dir():
                        shutil.copytree(path, root_path / path.name)
                    else:
                        if root_path.samefile(self.dir_model.rootPath()):
                            idx: QModelIndex = self.indexAt(e.pos())
                            if idx.column() == -1:
                                shutil.move(path, root_path / path.name)
                            else:
                                folder_path = Path(self.dir_model.filePath(idx))
                                shutil.move(path, folder_path / path.name)
                        else:
                            shutil.copy(path, root_path / path.name)
            e.accept()

            return super().dropEvent(e)
        except FileNotFoundError:
            print('error')
            return super().dropEvent(e)
        except BaseException as error:
            if self.editor_home_path is not None and self._parent_window is not None:
                BuriScriptLogHandler(self.editor_home_path, qApp, self._parent_window).custom_log_exceptions(
                    error.__class__.__name__, error, BuriScriptLogHandler.traceback_formatter(error.__traceback__))
            return super().dropEvent(e)

    def custom_context_menu_tree_view(self, position):
        tree_view_pos = self.indexAt(position)
        menu = QMenu()
        menu.setStyleSheet("""
        QMenuBar {
            background-color: #111111;
            color: rgb(255,255,255);
            border: 1px solid #000;
        }

        QMenuBar::item {
            background-color: #111111;
            color: rgb(255,255,255);
        }

        QMenuBar::item::selected {
            background-color: #111111;
        }

        QMenu {
            background-color: #111111;
            color: rgb(255,255,255);
            border: 1px solid #000;           
        }

        QMenu::item::selected {
            background-color: rgb(30,30,30);
        }""")
        menu.setFont(QFont("JetBrains Mono"))
        menu.addAction("Delete")
        menu.addAction("New File")
        menu.addAction("New Folder")
        menu.addAction("Open")
        menu.addAction("Rename")

        action = menu.exec_(self.viewport().mapToGlobal(position))

        if not action:
            return

        if action.text() == "Rename":
            self.rename_object(tree_view_pos)
        elif action.text() == "Delete":
            self.delete_object(tree_view_pos)
        elif action.text() == "New Folder":
            self.make_new_dir(tree_view_pos)
        elif action.text() == "New File":
            self.make_new_file(tree_view_pos)
        elif action.text() == "Open":
            absolute_path = self.dir_model.fileInfo(tree_view_pos).absoluteFilePath()
            self.override_method_open_in_editor(absolute_path)
        else:
            pass

    def on_clicked(self, index):
        ...

    def on_rename(self):
        self.rename_object(self.currentIndex())

    def on_delete_file(self):
        self.delete_object(self.currentIndex())

    def on_make_new_file(self):
        if self.hasFocus():
            self.make_new_file(self.currentIndex())

    def rename_object(self, position_to_rename):
        self.edit(position_to_rename)

    def make_new_dir(self, position_to_make_new_dir):
        file_object = Path(self.dir_model.rootPath()) / "New Folder"
        count = 1
        while file_object.exists():
            file_object = Path(file_object.parent / f"New Folder{count}")
            count += 1
        idx = self.dir_model.mkdir(self.rootIndex(), file_object.name)
        self.edit(idx)

    def override_method_open_in_editor(self, absolute_file_path_to_open: str):
        pass

    def make_new_file(self, ix: QModelIndex):
        root_path = self.dir_model.rootPath()
        if ix.column() != -1 and self.dir_model.isDir(ix):
            self.expand(ix)
            root_path = self.dir_model.filePath(ix)

        f = Path(root_path) / "file"
        count = 1
        while f.exists():
            f = Path(f.parent / f"file{count}")
            count += 1
        f.touch()
        idx = self.dir_model.index(str(f.absolute()))
        self.edit(idx)

    @staticmethod
    def delete_file(path: Path):
        if path.is_dir():
            shutil.rmtree(path)
        else:
            path.unlink()

    def delete_object(self, ix):
        # check if selection
        try:
            file_name = self.dir_model.fileName(ix)
            dialog = self.message_box_dialog("Delete", f"Are you sure you want to delete {file_name}")
            if dialog == QMessageBox.Yes:
                if self.selectionModel().selectedRows():
                    for i in self.selectionModel().selectedRows():
                        path = Path(self.dir_model.filePath(i))
                        self.delete_file(path)
        except Exception as error:
            print(error.__class__.__name__, error, __name__)

    @staticmethod
    def message_box_dialog(title, message) -> int:
        message_box_to_display = QMessageBox()
        message_box_to_display.setIcon(QMessageBox.Warning)
        message_box_to_display.setText(message)
        message_box_to_display.setWindowTitle(title)
        message_box_to_display.setStandardButtons(QMessageBox.Yes | QMessageBox.Cancel)
        return message_box_to_display.exec_()


class BuriScriptCwdExplorer(QWidget):
    def __init__(self, directory_path: str, home_path: str, parent_window: QMainWindow, parent=None):
        super().__init__(parent)
        self.__parent_window_having_editor = parent_window
        self.__lyt = QHBoxLayout(self)
        self.setStyleSheet('''background-color: #111111;
                              color: white;
                              border: 0px''')
        self.treeview = CustomTreeView(directory_path, home_path, self.__parent_window_having_editor)
        self.__lyt.addWidget(self.treeview)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = BuriScriptCwdExplorer(r"C:\Users\BURI\Desktop\add_all_extra\python\BuriScript", None, None)
    w.show()
    sys.exit(app.exec_())