from window.lab3_main_window import Lab3MainWindow
from PySide6.QtWidgets import QApplication

if __name__ == "__main__":
    app = QApplication([])

    main_window = Lab3MainWindow()
    main_window.show()

    app.exec()
