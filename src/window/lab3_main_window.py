import sys

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QTextCursor
from PySide6.QtSerialPort import QSerialPort
from PySide6.QtWidgets import (
    QDockWidget,
    QHBoxLayout,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QSplitter,
    QTextBrowser,
    QVBoxLayout,
    QWidget,
)
from widget.lab3_dc_motor_group_box import DCMotorWidget
from widget.lab3_serial_combo_box import SerialComboBox
from widget.lab3_stepper_motor_group_box import StepperMotorWidget


class Lab3MainWindow(QMainWindow):
    signal_write = Signal(str)

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.__central_widget = Lab3MainWindowCentralWidget()
        self.setCentralWidget(self.__central_widget)

        # redirect stdout to text browser
        self.__text_browser = QTextBrowser()
        sys.stdout = self
        sys.stderr = self
        self.signal_write.connect(self.__slot_write)

        dock_widget = QDockWidget()
        dock_widget.setWidget(self.__text_browser)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, dock_widget)

    def write(self, text: str) -> None:
        self.signal_write.emit(text)

    def flush(self) -> None:
        pass

    def __slot_write(self, text: str) -> None:
        self.__text_browser.moveCursor(QTextCursor.MoveOperation.End)
        self.__text_browser.insertPlainText(text)
        self.__text_browser.ensureCursorVisible()


class Lab3MainWindowCentralWidget(QWidget):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        # serial port
        self.__serial_port = QSerialPort()
        self.__serial_port.readyRead.connect(self.__slot_on_serial_ready)

        serial_port_layout = QHBoxLayout()
        self.__serial_port_combobox = SerialComboBox()

        self.__serial_connect_button = QPushButton("Connect")
        self.__serial_connect_button.setCheckable(True)
        self.__serial_connect_button.clicked.connect(self.__slot_on_serial_connect)

        serial_port_layout.addWidget(self.__serial_port_combobox)
        serial_port_layout.addWidget(self.__serial_connect_button)

        self.__splitter = QSplitter(Qt.Orientation.Horizontal)
        self.__splitter.setDisabled(True)
        self.__splitter.addWidget(DCMotorWidget(self.__serial_port))
        self.__splitter.addWidget(StepperMotorWidget(self.__serial_port))

        self.setLayout(QVBoxLayout())
        self.layout().addLayout(serial_port_layout)  # type: ignore
        self.layout().addWidget(self.__splitter)

    def __slot_on_serial_connect(self):
        if self.__serial_connect_button.isChecked():
            self.__serial_port.setPortName(self.__serial_port_combobox.currentText())
            self.__serial_port.setBaudRate(QSerialPort.BaudRate.Baud9600)
            self.__serial_port.setDataBits(QSerialPort.DataBits.Data8)
            self.__serial_port.setParity(QSerialPort.Parity.NoParity)
            self.__serial_port.setStopBits(QSerialPort.StopBits.OneStop)
            self.__serial_port.setFlowControl(QSerialPort.FlowControl.NoFlowControl)

            if not self.__serial_port.open(QSerialPort.OpenModeFlag.ReadWrite):
                QMessageBox.critical(self, "Error", "Cannot open serial port")
                self.__serial_connect_button.setChecked(False)
                return
            self.__serial_port_combobox.setEnabled(False)
            self.__serial_connect_button.setText("Disconnect")
            self.__splitter.setEnabled(True)
        else:
            self.__serial_port.close()
            self.__serial_port_combobox.setEnabled(True)
            self.__serial_connect_button.setText("Connect")
            self.__splitter.setDisabled(True)

    def __slot_on_serial_ready(self):
        print(f"{self.__serial_port.readAll().data().hex().upper()}")
