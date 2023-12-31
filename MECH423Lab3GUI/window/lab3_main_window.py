from datetime import datetime
from itertools import batched

from loguru import logger
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

from ..function_block.lab3_2axis_control_widget import TwoAxisControlWidget
from ..function_block.lab3_dc_motor_widget import DCMotorWidget
from ..function_block.lab3_stepper_motor_widget import StepperMotorWidget
from ..serial_protocol.lab3_serial_protocol import MCUPacket
from ..widget.serial_combo_box import SerialComboBox


class Lab3MainWindow(QMainWindow):
    signal_write = Signal(str)

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.__central_widget = Lab3MainWindowCentralWidget()
        self.setCentralWidget(self.__central_widget)

        self.__text_browser = QTextBrowser()
        self.signal_write.connect(self.__slot_write)

        dock_widget = QDockWidget()
        dock_widget.setWidget(self.__text_browser)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, dock_widget)

        self.setWindowTitle("MECH423Lab3GUI")

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
        self.__serial_rx_buffer = bytearray()
        self.__serial_port.readyRead.connect(self.__slot_on_serial_ready)

        serial_port_layout = QHBoxLayout()
        self.__serial_port_combobox = SerialComboBox()

        self.__serial_connect_button = QPushButton("Connect")
        self.__serial_connect_button.setCheckable(True)
        self.__serial_connect_button.clicked.connect(self.__slot_on_serial_connect)

        serial_port_layout.addWidget(self.__serial_port_combobox)
        serial_port_layout.addWidget(self.__serial_connect_button)

        self.__dc_motor_widget = DCMotorWidget()
        self.__dc_motor_widget.signal_serial_write.connect(self.__slot_on_serial_write)
        self.__stepper_motor_widget = StepperMotorWidget()
        self.__stepper_motor_widget.signal_serial_write.connect(
            self.__slot_on_serial_write
        )
        self.__2_axis_control_widget = TwoAxisControlWidget()
        self.__2_axis_control_widget.signal_serial_write.connect(
            self.__slot_on_serial_write
        )

        self.__splitter = QSplitter(Qt.Orientation.Horizontal)
        self.__splitter.setDisabled(True)
        self.__splitter.addWidget(self.__dc_motor_widget)
        self.__splitter.addWidget(self.__stepper_motor_widget)
        self.__splitter.addWidget(self.__2_axis_control_widget)

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
        data = self.__serial_port.readAll().data()
        logger.debug(f"{data.hex().upper()}")

        self.__serial_rx_buffer += data
        while len(self.__serial_rx_buffer) >= 4:
            try:
                packet = MCUPacket.from_bytes(self.__serial_rx_buffer[:4])
                self.__serial_rx_buffer = self.__serial_rx_buffer[4:]
                self.__dc_motor_widget.update_plot(
                    ((packet.data[0] << 8) + packet.data[1], datetime.now())
                )
            except Exception:
                self.__serial_rx_buffer.pop(0)

    def __slot_on_serial_write(self, message: bytearray):
        self.__serial_port.write(message)
        logger.debug(
            f"serial_bytes: {", ".join([x+y for (x,y) in (batched(message.hex().upper(),2))])}"
        )
