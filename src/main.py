import sys
from contextlib import redirect_stderr, redirect_stdout

from loguru import logger
from PySide6.QtWidgets import QApplication
from window.lab3_main_window import Lab3MainWindow

if __name__ == "__main__":
    app = QApplication([])

    main_window = Lab3MainWindow()
    main_window.show()
    with redirect_stdout(main_window):  # type: ignore
        with redirect_stderr(main_window):  # type: ignore
            logger.remove()
            logger.add(sys.stdout)
            logger.enable("function_block")
            app.exec()
